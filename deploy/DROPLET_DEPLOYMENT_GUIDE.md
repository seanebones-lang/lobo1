# 🚀 RAG System Droplet Deployment Guide

Complete guide for deploying the RAG system to a DigitalOcean droplet.

## 📋 **Prerequisites**

### **DigitalOcean Droplet Requirements:**
- **OS:** Ubuntu 20.04 LTS or newer
- **RAM:** Minimum 4GB (8GB recommended for production)
- **CPU:** 2+ vCPUs
- **Storage:** 50GB+ SSD
- **Network:** Public IP with domain pointing to it

### **Domain Setup:**
- Domain name registered
- DNS A record pointing to droplet IP
- Email address for SSL certificate

### **API Keys Required:**
- OpenAI API key (required)
- Anthropic API key (optional, for Claude models)
- Cohere API key (optional, for reranking)

---

## 🚀 **Quick Deployment**

### **Option 1: Automated Deployment (Recommended)**

```bash
# 1. Connect to your droplet
ssh root@your-droplet-ip

# 2. Create a non-root user
adduser raguser
usermod -aG sudo raguser
su - raguser

# 3. Run the automated deployment script
wget https://raw.githubusercontent.com/seanebones-lang/lobo1/main/deploy/droplet-deploy.sh
chmod +x droplet-deploy.sh
./droplet-deploy.sh your-domain.com admin@your-domain.com docker
```

### **Option 2: Manual Step-by-Step**

```bash
# 1. Clone the repository
git clone https://github.com/seanebones-lang/lobo1.git
cd lobo1

# 2. Run the setup script
chmod +x deploy/droplet-setup.sh
./deploy/droplet-setup.sh

# 3. Configure environment
cp env.example .env
nano .env  # Add your API keys

# 4. Deploy with Docker
docker-compose -f deploy/docker-compose.prod.yml up -d

# 5. Set up SSL
sudo certbot --nginx -d your-domain.com
```

---

## 🔧 **Configuration**

### **Environment Variables (.env file)**

```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
COHERE_API_KEY=your_cohere_api_key_here

# Database Configuration
VECTOR_DB_TYPE=chroma
VECTOR_DB_PATH=./chroma_db
REDIS_URL=redis://localhost:6379

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False
LOG_LEVEL=INFO

# Model Configuration
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4
TEMPERATURE=0.1
MAX_TOKENS=1000

# RAG Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
RERANK_TOP_K=10
```

### **Nginx Configuration**

The production Nginx configuration includes:
- SSL/TLS termination
- Rate limiting
- Security headers
- CORS support
- WebSocket support for Streamlit
- Gzip compression

### **Docker Services**

The production Docker setup includes:
- **rag-api**: FastAPI backend
- **rag-frontend**: Streamlit frontend
- **redis**: Caching layer
- **qdrant**: Vector database
- **mlflow**: Experiment tracking
- **nginx**: Reverse proxy

---

## 🌐 **Access Points**

After deployment, your RAG system will be available at:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | `https://your-domain.com` | Main Streamlit interface |
| **API** | `https://your-domain.com/api` | FastAPI backend |
| **API Docs** | `https://your-domain.com/api/docs` | OpenAPI documentation |
| **Health Check** | `https://your-domain.com/api/health` | System health status |
| **MLflow** | `https://your-domain.com:5000` | Experiment tracking |

---

## 🔒 **Security Configuration**

### **Firewall Setup**
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw allow 8501
sudo ufw allow 5000
sudo ufw allow 6379
sudo ufw allow 6333
```

### **SSL Certificate**
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### **Security Headers**
The Nginx configuration includes:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Referrer-Policy: strict-origin-when-cross-origin`

---

## 📊 **Monitoring & Maintenance**

### **Health Checks**
```bash
# Check API health
curl https://your-domain.com/api/health

# Check Docker services
docker-compose ps

# Check logs
docker-compose logs -f
```

### **Backup Strategy**
```bash
# Manual backup
./backup.sh

# Automated daily backups (already configured)
# Backups stored in /opt/rag-system/backups/
```

### **Log Management**
```bash
# View logs
tail -f logs/api.log
tail -f logs/frontend.log

# Log rotation (already configured)
# Logs rotated daily, kept for 7 days
```

### **Performance Monitoring**
- **MLflow**: Track experiments and model performance
- **Nginx**: Access logs and error logs
- **Docker**: Container resource usage
- **System**: CPU, memory, disk usage

---

## 🔄 **Updates & Maintenance**

### **Updating the System**
```bash
# Pull latest changes
cd /opt/rag-system/lobo1
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose up -d --build
```

### **Scaling the System**
```bash
# Scale API service
docker-compose up -d --scale rag-api=3

# Scale frontend service
docker-compose up -d --scale rag-frontend=2
```

### **Database Maintenance**
```bash
# Backup vector database
docker-compose exec rag-api python -c "
from src.retrieval.vector_store import VectorStore
store = VectorStore()
# Backup logic here
"

# Clean up old data
docker-compose exec redis redis-cli FLUSHDB
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Services Not Starting**
```bash
# Check Docker logs
docker-compose logs rag-api
docker-compose logs rag-frontend

# Check system resources
htop
df -h
```

#### **2. SSL Certificate Issues**
```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

#### **3. API Not Responding**
```bash
# Check API health
curl http://localhost:8000/health

# Check Nginx configuration
sudo nginx -t

# Restart services
docker-compose restart rag-api
```

#### **4. Frontend Not Loading**
```bash
# Check Streamlit logs
docker-compose logs rag-frontend

# Check WebSocket connection
curl -I https://your-domain.com
```

### **Performance Issues**

#### **High Memory Usage**
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart

# Scale down if needed
docker-compose up -d --scale rag-api=1
```

#### **Slow Response Times**
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Check vector database
docker-compose exec rag-api python -c "
from src.retrieval.vector_store import VectorStore
store = VectorStore()
print(store.get_collection_info())
"
```

---

## 📈 **Production Optimizations**

### **Performance Tuning**
1. **Increase worker processes** in Nginx
2. **Enable Redis caching** for frequent queries
3. **Optimize vector database** settings
4. **Use CDN** for static assets
5. **Implement connection pooling**

### **Security Enhancements**
1. **Enable fail2ban** for intrusion prevention
2. **Set up log monitoring** and alerting
3. **Implement API rate limiting**
4. **Use environment-specific secrets**
5. **Regular security updates**

### **Monitoring Setup**
1. **Set up Prometheus** for metrics collection
2. **Configure Grafana** dashboards
3. **Implement alerting** for critical issues
4. **Set up log aggregation** (ELK stack)
5. **Monitor resource usage** and performance

---

## 🎯 **Post-Deployment Checklist**

- [ ] Domain DNS pointing to droplet IP
- [ ] SSL certificate installed and working
- [ ] All services running and healthy
- [ ] API endpoints responding correctly
- [ ] Frontend accessible and functional
- [ ] Environment variables configured
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting set up
- [ ] Documentation updated with domain

---

## 🆘 **Support & Resources**

### **Useful Commands**
```bash
# System status
./scripts/start_services.sh status

# View logs
./scripts/start_services.sh logs

# Restart services
./scripts/start_services.sh restart

# Clean up
make clean
```

### **Documentation**
- [Main README](../README.md)
- [API Documentation](https://your-domain.com/api/docs)
- [Quick Start Guide](../QUICK_START.md)
- [Test Results](../TEST_RESULTS.md)

### **Emergency Contacts**
- **System Issues**: Check logs and restart services
- **Domain Issues**: Verify DNS configuration
- **SSL Issues**: Renew certificates with Certbot
- **Performance Issues**: Monitor resources and scale

---

## 🎉 **Deployment Complete!**

Your RAG system is now live and ready for production use!

**Access your system at:** `https://your-domain.com`

**Next steps:**
1. Upload documents to build your knowledge base
2. Test the API endpoints
3. Configure monitoring and alerting
4. Set up regular backups
5. Monitor performance and scale as needed

**Happy RAG-ing!** 🚀
