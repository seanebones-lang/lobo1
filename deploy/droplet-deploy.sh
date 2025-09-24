#!/bin/bash

# RAG System Droplet Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Configuration
DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"admin@your-domain.com"}
DEPLOY_METHOD=${3:-"docker"}  # docker or local

print_header "🚀 RAG System Droplet Deployment"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Validate domain
if [ "$DOMAIN" = "your-domain.com" ]; then
    print_error "Please provide a valid domain name as the first argument"
    print_error "Usage: $0 <domain> <email> [deploy_method]"
    print_error "Example: $0 mydomain.com admin@mydomain.com docker"
    exit 1
fi

print_status "Deploying RAG System to domain: $DOMAIN"
print_status "Email: $EMAIL"
print_status "Deploy method: $DEPLOY_METHOD"

# Update system
print_status "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Install Certbot for SSL
print_status "Installing Certbot for SSL certificates..."
sudo apt-get install -y certbot python3-certbot-nginx

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p /opt/rag-system
sudo chown $USER:$USER /opt/rag-system
cd /opt/rag-system

# Clone or update repository
if [ -d "lobo1" ]; then
    print_status "Updating existing repository..."
    cd lobo1
    git pull origin main
else
    print_status "Cloning repository..."
    git clone https://github.com/seanebones-lang/lobo1.git
    cd lobo1
fi

# Set up environment
print_status "Setting up environment..."
if [ ! -f ".env" ]; then
    cp env.example .env
    print_warning "Please edit .env file with your API keys:"
    print_warning "nano .env"
    print_warning "Required keys: OPENAI_API_KEY, ANTHROPIC_API_KEY (optional), COHERE_API_KEY (optional)"
    read -p "Press Enter after configuring .env file..."
fi

# Create necessary directories
print_status "Creating application directories..."
mkdir -p logs data chroma_db ssl

# Configure firewall
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw allow 8501
sudo ufw allow 5000
sudo ufw allow 6379
sudo ufw allow 6333

# Deploy based on method
if [ "$DEPLOY_METHOD" = "docker" ]; then
    print_status "Deploying with Docker..."
    
    # Copy production configuration
    cp deploy/docker-compose.prod.yml docker-compose.yml
    cp deploy/nginx.prod.conf nginx.prod.conf
    
    # Update domain in nginx config
    sed -i "s/your-domain.com/$DOMAIN/g" nginx.prod.conf
    
    # Start services
    print_status "Starting Docker services..."
    docker-compose up -d
    
    # Wait for services to start
    print_status "Waiting for services to start..."
    sleep 30
    
elif [ "$DEPLOY_METHOD" = "local" ]; then
    print_status "Deploying locally..."
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Configure Nginx
    print_status "Configuring Nginx..."
    sudo cp deploy/nginx.prod.conf /etc/nginx/sites-available/rag-system
    sudo sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/rag-system
    sudo ln -sf /etc/nginx/sites-available/rag-system /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    sudo nginx -t
    
    # Start services
    print_status "Starting services..."
    ./scripts/start_services.sh start
    
else
    print_error "Invalid deploy method. Use 'docker' or 'local'"
    exit 1
fi

# Set up SSL certificate
print_status "Setting up SSL certificate..."
sudo certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive --redirect

# Configure log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/rag-system > /dev/null <<EOF
/opt/rag-system/lobo1/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

# Set up monitoring
print_status "Setting up basic monitoring..."
sudo tee /etc/cron.d/rag-system-health > /dev/null <<EOF
*/5 * * * * $USER curl -f http://localhost:8000/health > /dev/null 2>&1 || echo "RAG API health check failed" | mail -s "RAG System Alert" $EMAIL
EOF

# Create backup script
print_status "Creating backup script..."
tee backup.sh > /dev/null <<EOF
#!/bin/bash
# RAG System Backup Script
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/rag-system/backups"
mkdir -p \$BACKUP_DIR

# Backup application data
tar -czf \$BACKUP_DIR/rag-system-\$DATE.tar.gz \\
    --exclude=venv \\
    --exclude=__pycache__ \\
    --exclude=.git \\
    /opt/rag-system/lobo1

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "rag-system-*.tar.gz" -mtime +7 -delete

echo "Backup completed: rag-system-\$DATE.tar.gz"
EOF

chmod +x backup.sh

# Set up daily backups
print_status "Setting up daily backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/rag-system/lobo1/backup.sh") | crontab -

print_header "🎉 Deployment Complete!"

print_status "RAG System is now deployed and accessible at:"
echo "🌐 Frontend: https://$DOMAIN"
echo "🔌 API: https://$DOMAIN/api"
echo "📚 API Docs: https://$DOMAIN/api/docs"
echo "📊 MLflow: https://$DOMAIN:5000"

print_status "System Status:"
if [ "$DEPLOY_METHOD" = "docker" ]; then
    docker-compose ps
else
    ./scripts/start_services.sh status
fi

print_warning "Important next steps:"
echo "1. Verify your domain DNS points to this droplet's IP"
echo "2. Test all endpoints to ensure they're working"
echo "3. Set up monitoring and alerting"
echo "4. Configure regular backups"
echo "5. Review security settings"

print_status "Deployment completed successfully! 🚀"
print_status "Your RAG system is now live at https://$DOMAIN"
