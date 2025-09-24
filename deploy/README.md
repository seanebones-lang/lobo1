# 🚀 RAG System Droplet Deployment

Complete deployment package for DigitalOcean droplets and other VPS providers.

## 📦 **Deployment Package Contents**

### **Scripts:**
- `droplet-setup.sh` - Initial server setup and configuration
- `droplet-deploy.sh` - Automated deployment script
- `health-check.sh` - System health monitoring

### **Configurations:**
- `docker-compose.prod.yml` - Production Docker setup
- `nginx.prod.conf` - Production Nginx configuration

### **Documentation:**
- `DROPLET_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `README.md` - This file

---

## 🚀 **Quick Start**

### **1. Prerequisites**
- DigitalOcean droplet (Ubuntu 20.04+)
- Domain name pointing to droplet IP
- API keys (OpenAI required, others optional)

### **2. Automated Deployment**
```bash
# Connect to your droplet
ssh root@your-droplet-ip

# Create user and switch
adduser raguser
usermod -aG sudo raguser
su - raguser

# Run deployment
wget https://raw.githubusercontent.com/seanebones-lang/lobo1/main/deploy/droplet-deploy.sh
chmod +x droplet-deploy.sh
./droplet-deploy.sh your-domain.com admin@your-domain.com docker
```

### **3. Manual Setup**
```bash
# Clone repository
git clone https://github.com/seanebones-lang/lobo1.git
cd lobo1

# Run setup
chmod +x deploy/droplet-setup.sh
./deploy/droplet-setup.sh

# Configure environment
cp env.example .env
nano .env  # Add your API keys

# Deploy
docker-compose -f deploy/docker-compose.prod.yml up -d
```

---

## 🔧 **Configuration**

### **Environment Variables**
Edit `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
COHERE_API_KEY=your_cohere_key_here
```

### **Domain Configuration**
Update `nginx.prod.conf` with your domain:
```nginx
server_name your-domain.com;
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

---

## 🌐 **Access Points**

After deployment:
- **Frontend**: `https://your-domain.com`
- **API**: `https://your-domain.com/api`
- **API Docs**: `https://your-domain.com/api/docs`
- **MLflow**: `https://your-domain.com:5000`

---

## 🔍 **Health Monitoring**

### **Check System Health**
```bash
./deploy/health-check.sh your-domain.com
```

### **View Logs**
```bash
docker-compose logs -f
tail -f logs/api.log
tail -f logs/frontend.log
```

### **Restart Services**
```bash
docker-compose restart
# or
./scripts/start_services.sh restart
```

---

## 🛠️ **Maintenance**

### **Updates**
```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

### **Backups**
```bash
./backup.sh  # Manual backup
# Automated daily backups already configured
```

### **SSL Certificate Renewal**
```bash
sudo certbot renew
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Services Not Starting**
```bash
# Check Docker logs
docker-compose logs

# Check system resources
htop
df -h
```

#### **SSL Issues**
```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

#### **API Not Responding**
```bash
# Check API health
curl http://localhost:8000/health

# Check Nginx
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📊 **Production Features**

### **Security**
- SSL/TLS encryption
- Rate limiting
- Security headers
- Firewall configuration
- Fail2ban protection

### **Performance**
- Nginx reverse proxy
- Gzip compression
- Connection pooling
- Resource limits
- Health checks

### **Monitoring**
- Health check endpoints
- Log rotation
- Performance monitoring
- Automated backups
- Alert system

### **Scalability**
- Docker containerization
- Load balancing ready
- Horizontal scaling support
- Database optimization
- Caching layers

---

## 📚 **Documentation**

- [Complete Deployment Guide](DROPLET_DEPLOYMENT_GUIDE.md)
- [Main README](../README.md)
- [Quick Start Guide](../QUICK_START.md)
- [API Documentation](https://your-domain.com/api/docs)

---

## 🆘 **Support**

### **Useful Commands**
```bash
# System status
./scripts/start_services.sh status

# View logs
./scripts/start_services.sh logs

# Health check
./deploy/health-check.sh

# Restart services
./scripts/start_services.sh restart
```

### **Emergency Procedures**
1. **Check logs** for error messages
2. **Restart services** if needed
3. **Check system resources** (CPU, memory, disk)
4. **Verify network connectivity**
5. **Check SSL certificate status**

---

## 🎉 **Deployment Complete!**

Your RAG system is now live and ready for production use!

**Next steps:**
1. Upload documents to build knowledge base
2. Test all endpoints
3. Configure monitoring
4. Set up regular backups
5. Monitor performance

**Happy RAG-ing!** 🚀
