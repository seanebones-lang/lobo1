# 🚀 RAG System Deployment Guide

## Quick Deployment to DigitalOcean Droplet

### Prerequisites
- SSH access to your droplet (IP: 178.128.65.207)
- SSH key configured for passwordless access
- Domain name (optional, for SSL setup)

### Method 1: Automated Deployment (Recommended)

1. **Run the deployment script:**
   ```bash
   ./deploy/deploy-to-droplet.sh
   ```

2. **The script will:**
   - Install Docker and Docker Compose on your droplet
   - Clone the repository
   - Set up the environment
   - Start all services
   - Perform health checks

3. **After deployment, your services will be available at:**
   - Frontend: http://178.128.65.207:8501
   - API: http://178.128.65.207:8000
   - API Docs: http://178.128.65.207:8000/docs

### Method 2: Manual Deployment

1. **SSH into your droplet:**
   ```bash
   ssh root@178.128.65.207
   ```

2. **Install dependencies:**
   ```bash
   # Update system
   apt update && apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   rm get-docker.sh
   
   # Install Docker Compose
   DOCKER_COMPOSE_VERSION="v2.24.5"
   curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   chmod +x /usr/local/bin/docker-compose
   ```

3. **Clone and setup:**
   ```bash
   git clone https://github.com/seanebones-lang/lobo1.git /opt/lobo1
   cd /opt/lobo1
   cp env.example .env
   # Edit .env with your API keys
   nano .env
   ```

4. **Start services:**
   ```bash
   docker-compose -f deploy/docker-compose.simple.yml up -d --build
   ```

### Post-Deployment Configuration

1. **Configure API Keys:**
   ```bash
   ssh root@178.128.65.207
   cd /opt/lobo1
   nano .env
   ```
   
   Add your API keys:
   ```
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   COHERE_API_KEY=your_cohere_key_here
   ```

2. **Restart services after adding API keys:**
   ```bash
   docker-compose -f deploy/docker-compose.simple.yml restart
   ```

### Monitoring and Management

**Check service status:**
```bash
docker-compose -f deploy/docker-compose.simple.yml ps
```

**View logs:**
```bash
docker-compose -f deploy/docker-compose.simple.yml logs -f
```

**Stop services:**
```bash
docker-compose -f deploy/docker-compose.simple.yml down
```

**Update services:**
```bash
git pull origin main
docker-compose -f deploy/docker-compose.simple.yml up -d --build
```

### Security Considerations

1. **Firewall setup:**
   ```bash
   ufw allow ssh
   ufw allow 80
   ufw allow 443
   ufw allow 8000
   ufw allow 8501
   ufw enable
   ```

2. **SSL Setup (Optional):**
   - Use Let's Encrypt with Certbot
   - Configure Nginx reverse proxy
   - See `deploy/nginx.prod.conf` for SSL configuration

### Troubleshooting

**If services fail to start:**
1. Check logs: `docker-compose -f deploy/docker-compose.simple.yml logs`
2. Verify API keys in `.env` file
3. Check disk space: `df -h`
4. Check memory usage: `free -h`

**If API is not responding:**
1. Check if the service is running: `docker ps`
2. Check API logs: `docker logs rag-api`
3. Test locally: `curl http://localhost:8000/health`

**If frontend is not loading:**
1. Check if the service is running: `docker ps`
2. Check frontend logs: `docker logs rag-frontend`
3. Verify API_BASE_URL in environment

### Performance Optimization

1. **Resource limits:** Already configured in docker-compose.simple.yml
2. **Caching:** Redis is configured for response caching
3. **Vector DB:** Qdrant is configured for efficient vector operations
4. **Monitoring:** MLflow is available for experiment tracking

### Backup and Recovery

**Backup data:**
```bash
# Backup vector database
tar -czf chroma_backup.tar.gz chroma_db/

# Backup Redis data
docker exec redis redis-cli BGSAVE
```

**Restore data:**
```bash
# Restore vector database
tar -xzf chroma_backup.tar.gz
```

### Next Steps

1. **Set up monitoring:** Configure MLflow for experiment tracking
2. **Add SSL:** Use Let's Encrypt for HTTPS
3. **Scale services:** Use Docker Swarm or Kubernetes for production
4. **Add monitoring:** Set up Prometheus and Grafana
5. **Backup strategy:** Implement automated backups

## Support

If you encounter issues:
1. Check the logs first
2. Verify all environment variables
3. Ensure sufficient system resources
4. Check network connectivity

For more detailed information, see the main README.md file.
