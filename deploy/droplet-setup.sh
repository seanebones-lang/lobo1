#!/bin/bash

# DigitalOcean Droplet Deployment Script for RAG System
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

print_header "🚀 RAG System Droplet Deployment Setup"

# Update system packages
print_status "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install essential packages
print_status "Installing essential packages..."
sudo apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    nginx \
    redis-server \
    supervisor \
    ufw \
    fail2ban \
    htop \
    nano \
    vim

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker installed successfully"
else
    print_status "Docker already installed"
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully"
else
    print_status "Docker Compose already installed"
fi

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

# Configure fail2ban
print_status "Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p /opt/rag-system
sudo chown $USER:$USER /opt/rag-system
cd /opt/rag-system

# Clone repository
print_status "Cloning RAG system repository..."
if [ ! -d "lobo1" ]; then
    git clone https://github.com/seanebones-lang/lobo1.git
    cd lobo1
else
    cd lobo1
    git pull origin main
fi

# Set up environment
print_status "Setting up environment..."
cp env.example .env
print_warning "Please edit .env file with your API keys:"
print_warning "nano .env"

# Create necessary directories
print_status "Creating application directories..."
mkdir -p logs data chroma_db ssl

# Set up SSL certificates (Let's Encrypt)
print_status "Setting up SSL certificates..."
sudo apt-get install -y certbot python3-certbot-nginx

# Configure Nginx
print_status "Configuring Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/rag-system
sudo ln -sf /etc/nginx/sites-available/rag-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Configure Supervisor for process management
print_status "Configuring Supervisor..."
sudo tee /etc/supervisor/conf.d/rag-system.conf > /dev/null <<EOF
[program:rag-api]
command=/opt/rag-system/lobo1/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
directory=/opt/rag-system/lobo1
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/rag-system/lobo1/logs/api.log

[program:rag-frontend]
command=/opt/rag-system/lobo1/venv/bin/streamlit run src/frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
directory=/opt/rag-system/lobo1
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/rag-system/lobo1/logs/frontend.log
EOF

# Configure Redis
print_status "Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Set up log rotation
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

# Create systemd service for the application
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/rag-system.service > /dev/null <<EOF
[Unit]
Description=RAG System
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/opt/rag-system/lobo1/scripts/start-services.sh start
ExecStop=/opt/rag-system/lobo1/scripts/start-services.sh stop
User=$USER
WorkingDirectory=/opt/rag-system/lobo1

[Install]
WantedBy=multi-user.target
EOF

# Enable services
sudo systemctl daemon-reload
sudo systemctl enable rag-system

print_header "🎉 Droplet Setup Complete!"

print_status "Next steps:"
echo "1. Edit environment file: nano /opt/rag-system/lobo1/.env"
echo "2. Set up SSL certificate: sudo certbot --nginx -d your-domain.com"
echo "3. Start the system: cd /opt/rag-system/lobo1 && make quick-start"
echo "4. Or use Docker: cd /opt/rag-system/lobo1 && docker-compose up -d"

print_status "System will be available at:"
echo "- Frontend: http://your-domain.com or http://your-droplet-ip:8501"
echo "- API: http://your-domain.com/api or http://your-droplet-ip:8000"
echo "- API Docs: http://your-domain.com/api/docs"

print_warning "Don't forget to:"
echo "- Configure your domain DNS to point to this droplet"
echo "- Set up SSL certificates with Let's Encrypt"
echo "- Configure your API keys in .env file"
echo "- Set up monitoring and backups"

print_status "Setup completed successfully! 🚀"
