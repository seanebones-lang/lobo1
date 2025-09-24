#!/bin/bash
# deploy/deploy-to-droplet.sh
# Automated deployment script for DigitalOcean droplet

set -e

# Configuration
DROPLET_IP="178.128.65.207"
DROPLET_USER="root"  # Change to your droplet user if different
REPO_URL="https://github.com/seanebones-lang/lobo1.git"
DEPLOY_DIR="/opt/lobo1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if SSH key exists
check_ssh_key() {
    if [ ! -f ~/.ssh/id_rsa ] && [ ! -f ~/.ssh/id_ed25519 ]; then
        log_error "No SSH key found. Please generate one with: ssh-keygen -t ed25519 -C 'your_email@example.com'"
    fi
    log_info "SSH key found"
}

# Copy SSH key to droplet
setup_ssh_access() {
    log_info "Setting up SSH access to droplet..."
    ssh-copy-id -o StrictHostKeyChecking=no $DROPLET_USER@$DROPLET_IP || {
        log_warn "SSH key copy failed. You may need to manually add your SSH key to the droplet."
        log_warn "Run: ssh-copy-id $DROPLET_USER@$DROPLET_IP"
    }
}

# Test SSH connection
test_ssh_connection() {
    log_info "Testing SSH connection to droplet..."
    ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $DROPLET_USER@$DROPLET_IP "echo 'SSH connection successful'" || {
        log_error "Cannot connect to droplet. Please check your SSH configuration."
    }
}

# Deploy to droplet
deploy_to_droplet() {
    log_info "Deploying RAG system to droplet $DROPLET_IP..."
    
    # Create deployment script on droplet
    ssh $DROPLET_USER@$DROPLET_IP "cat > /tmp/deploy-rag.sh << 'EOF'
#!/bin/bash
set -e

# Update system
apt update && apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo 'Installing Docker...'
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo 'Installing Docker Compose...'
    DOCKER_COMPOSE_VERSION='v2.24.5'
    curl -L \"https://github.com/docker/compose/releases/download/\$DOCKER_COMPOSE_VERSION/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

# Install Nginx if not present
if ! command -v nginx &> /dev/null; then
    echo 'Installing Nginx...'
    apt install nginx -y
    systemctl start nginx
    systemctl enable nginx
fi

# Clone repository
if [ -d \"$DEPLOY_DIR\" ]; then
    echo 'Repository exists, updating...'
    cd \"$DEPLOY_DIR\"
    git pull origin main
else
    echo 'Cloning repository...'
    git clone \"$REPO_URL\" \"$DEPLOY_DIR\"
    cd \"$DEPLOY_DIR\"
fi

# Copy environment file
if [ ! -f .env ]; then
    cp env.example .env
    echo 'Please edit .env file with your API keys'
fi

# Make scripts executable
chmod +x scripts/*.sh deploy/*.sh

# Start services with Docker Compose
echo 'Starting RAG system services...'
docker-compose -f deploy/docker-compose.simple.yml up -d --build

echo 'Deployment complete!'
echo 'Services should be available at:'
echo '- Frontend: http://$DROPLET_IP:8501'
echo '- API: http://$DROPLET_IP:8000'
echo '- API Docs: http://$DROPLET_IP:8000/docs'
EOF"

    # Execute deployment script on droplet
    ssh $DROPLET_USER@$DROPLET_IP "chmod +x /tmp/deploy-rag.sh && /tmp/deploy-rag.sh"
    
    log_info "Deployment completed!"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check if services are running
    ssh $DROPLET_USER@$DROPLET_IP "cd $DEPLOY_DIR && docker-compose -f deploy/docker-compose.simple.yml ps"
    
    # Test API endpoint
    log_info "Testing API endpoint..."
    curl -f http://$DROPLET_IP:8000/health || log_warn "API health check failed"
    
    # Test frontend
    log_info "Testing frontend..."
    curl -f http://$DROPLET_IP:8501 || log_warn "Frontend health check failed"
}

# Main execution
main() {
    echo "🚀 Deploying RAG System to DigitalOcean Droplet"
    echo "================================================"
    echo "Droplet IP: $DROPLET_IP"
    echo "Repository: $REPO_URL"
    echo "================================================"
    
    check_ssh_key
    setup_ssh_access
    test_ssh_connection
    deploy_to_droplet
    health_check
    
    log_info "Deployment completed successfully!"
    echo ""
    echo "🌐 Your RAG system is now available at:"
    echo "   Frontend: http://$DROPLET_IP:8501"
    echo "   API: http://$DROPLET_IP:8000"
    echo "   API Docs: http://$DROPLET_IP:8000/docs"
    echo ""
    echo "📝 Next steps:"
    echo "   1. SSH into your droplet: ssh $DROPLET_USER@$DROPLET_IP"
    echo "   2. Edit the .env file: cd $DEPLOY_DIR && nano .env"
    echo "   3. Add your API keys to the .env file"
    echo "   4. Restart services: cd $DEPLOY_DIR && docker-compose -f deploy/docker-compose.prod.yml restart"
}

main "$@"
