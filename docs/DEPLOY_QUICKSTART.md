# Deployment Quick Reference

## Initial Setup (First Time Only)

1. **Create Digital Ocean Droplet**
   - Ubuntu 22.04 LTS
   - 1GB RAM minimum
   - SSH key authentication

2. **Configure DNS**
   ```
   A Record: api.mcguire.technology → <droplet-ip>
   ```

3. **Run Setup Script** (on droplet)
   ```bash
   ssh root@<droplet-ip>
   
   # Set variables
   export REPO_URL="https://github.com/McGuireTechnology/API.git"
   export ADMIN_EMAIL="admin@mcguire.technology"
   
   # Run setup
   curl -sSL https://raw.githubusercontent.com/McGuireTechnology/API/main/deploy/setup.sh | bash
   ```

## Deploy Updates

### From Local Machine:
```bash
export DROPLET_IP="your-droplet-ip"
make deploy-droplet
```

### On Droplet:
```bash
cd /var/www/mcguire-api
make deploy-production
```

## Common Commands (on Droplet)

```bash
# Check status
sudo systemctl status mcguire-api

# View logs
sudo journalctl -u mcguire-api -f

# Restart service
sudo systemctl restart mcguire-api

# Test API
curl http://localhost:8000/health
curl https://api.mcguire.technology/health
```

## File Locations

- Application: `/var/www/mcguire-api`
- Systemd service: `/etc/systemd/system/mcguire-api.service`
- Nginx config: `/etc/nginx/sites-available/api.mcguire.technology`
- SSL certificates: `/etc/letsencrypt/live/api.mcguire.technology/`
- Logs: `/var/log/nginx/` and `journalctl -u mcguire-api`

## Troubleshooting

**Service won't start:**
```bash
sudo journalctl -u mcguire-api -xe
sudo systemctl restart mcguire-api
```

**Port in use:**
```bash
sudo netstat -tlnp | grep 8000
sudo systemctl restart mcguire-api
```

**SSL issues:**
```bash
sudo certbot renew
sudo systemctl reload nginx
```

## Access Points

- API: https://api.mcguire.technology
- Health: https://api.mcguire.technology/health
- Docs: https://api.mcguire.technology/docs (if DEBUG=true)
- Example App: https://api.mcguire.technology/example/docs
