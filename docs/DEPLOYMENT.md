# Digital Ocean Deployment Guide

This guide will help you deploy the McGuire Technology API to a Digital Ocean Droplet.

## Prerequisites

- A Digital Ocean account
- A domain name (api.mcguire.technology)
- SSH access to your droplet
- Git repository: https://github.com/McGuireTechnology/API

## 1. Create a Digital Ocean Droplet

1. **Log in to Digital Ocean Console**
2. **Create a new Droplet**:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month recommended for start)
   - **CPU**: Regular with SSD (1GB RAM / 1 CPU)
   - **Datacenter**: Choose closest to your users
   - **Authentication**: SSH Key (recommended)
   - **Hostname**: `mcguire-api`

3. **Note your Droplet's IP address**

## 2. Configure DNS

Point your domain to the droplet:

```
Type: A Record
Name: api.mcguire.technology
Value: <your-droplet-ip>
TTL: 3600
```

Wait for DNS propagation (can take up to 48 hours, usually minutes).

## 3. Initial Server Setup

### Connect to your droplet:

```bash
ssh root@<your-droplet-ip>
```

### Clone your repository:

```bash
# Set your repository URL
export REPO_URL="https://github.com/McGuireTechnology/API.git"
export ADMIN_EMAIL="admin@mcguire.technology"

# Download and run the setup script
curl -sSL https://raw.githubusercontent.com/McGuireTechnology/API/main/deploy/setup.sh | bash
```

Or manually:

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y python3.11 python3.11-venv nginx git curl certbot python3-certbot-nginx

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/root/.local/bin:$PATH"

# Clone repository
git clone https://github.com/McGuireTechnology/API.git /var/www/mcguire-api
cd /var/www/mcguire-api

# Install dependencies
poetry install --only main

# Set up environment
cp .env.example .env
# Edit .env with your settings
nano .env
```

## 4. Run the Setup Script

```bash
cd /var/www/mcguire-api
export REPO_URL="https://github.com/McGuireTechnology/API.git"
export ADMIN_EMAIL="admin@mcguire.technology"
bash deploy/setup.sh
```

This script will:
- Install system dependencies
- Set up Python and Poetry
- Configure Nginx
- Set up SSL with Let's Encrypt
- Create systemd service
- Configure firewall

## 5. Configure Environment Variables

Edit the `.env` file:

```bash
nano /var/www/mcguire-api/.env
```

Update with your production settings:

```env
APP_NAME=McGuire Technology API
ENVIRONMENT=production
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=https://mcguire.technology,https://www.mcguire.technology
```

## 6. Manual Service Setup (if needed)

If you didn't use the setup script:

```bash
# Copy systemd service
cp /var/www/mcguire-api/deploy/mcguire-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable mcguire-api
systemctl start mcguire-api

# Check status
systemctl status mcguire-api
```

## 7. Configure Nginx

```bash
# Copy Nginx config
cp /var/www/mcguire-api/deploy/nginx.conf /etc/nginx/sites-available/api.mcguire.technology
ln -s /etc/nginx/sites-available/api.mcguire.technology /etc/nginx/sites-enabled/

# Remove default site
rm /etc/nginx/sites-enabled/default

# Test configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

## 8. Set Up SSL

```bash
certbot --nginx -d api.mcguire.technology
```

Follow the prompts to set up SSL certificates.

## 9. Verify Deployment

```bash
# Check service status
systemctl status mcguire-api

# Check logs
journalctl -u mcguire-api -f

# Test the API
curl https://api.mcguire.technology/health
```

## Continuous Deployment

### Using the deploy script:

```bash
# On your local machine
export DROPLET_IP="your-droplet-ip"
export DROPLET_USER="root"
bash deploy/deploy.sh
```

### Manual deployment:

```bash
# On the droplet
cd /var/www/mcguire-api
git pull origin main
poetry install --only main
systemctl restart mcguire-api
```

## Makefile Commands (on server)

```bash
cd /var/www/mcguire-api

# Restart service
make restart-service

# View logs
make logs

# Update and restart
make deploy-production
```

Add these to your Makefile:

```makefile
restart-service: ## Restart the systemd service
	sudo systemctl restart mcguire-api

logs: ## View application logs
	sudo journalctl -u mcguire-api -f

deploy-production: ## Deploy to production
	git pull origin main
	poetry install --only main --no-interaction
	sudo systemctl restart mcguire-api
	@echo "✅ Deployment completed"
```

## Monitoring

### Check service status:

```bash
systemctl status mcguire-api
```

### View logs:

```bash
# Application logs
journalctl -u mcguire-api -f

# Nginx access logs
tail -f /var/log/nginx/api.mcguire.technology.access.log

# Nginx error logs
tail -f /var/log/nginx/api.mcguire.technology.error.log
```

## Troubleshooting

### Service won't start:

```bash
# Check logs
journalctl -u mcguire-api -xe

# Check if port is in use
netstat -tlnp | grep 8000

# Verify Python path
which python3
/var/www/mcguire-api/.venv/bin/python --version
```

### Nginx errors:

```bash
# Test configuration
nginx -t

# Check error logs
tail -f /var/log/nginx/error.log
```

### SSL issues:

```bash
# Renew certificates
certbot renew --dry-run
certbot renew

# Check certificate status
certbot certificates
```

## Security Checklist

- [ ] Firewall configured (UFW)
- [ ] SSH key authentication only (disable password auth)
- [ ] Fail2ban installed and configured
- [ ] SSL certificates installed
- [ ] Environment variables secured
- [ ] Regular backups configured
- [ ] Monitoring set up

## Backup

```bash
# Backup application data
tar -czf backup-$(date +%Y%m%d).tar.gz /var/www/mcguire-api

# Backup to Digital Ocean Spaces or S3
# Set up automated backups with cron
```

## Maintenance

### Update dependencies:

```bash
cd /var/www/mcguire-api
poetry update
systemctl restart mcguire-api
```

### Update system:

```bash
apt-get update
apt-get upgrade -y
reboot # if kernel updated
```

## Scaling

For high traffic, consider:

1. **Increase Droplet size** (more CPU/RAM)
2. **Add load balancer** (Digital Ocean Load Balancer)
3. **Database optimization** (managed PostgreSQL)
4. **CDN** (Digital Ocean Spaces + CDN)
5. **Multiple droplets** with load balancing

## Support

For issues:
- Check logs: `journalctl -u mcguire-api -f`
- Review Nginx logs: `/var/log/nginx/`
- Contact: admin@mcguire.technology
