# Digital Ocean App Platform Deployment

This guide covers deploying the McGuire Technology API to Digital Ocean's App Platform.

## Why App Platform?

App Platform is simpler than managing droplets:
- ✅ Automatic deployments from GitHub
- ✅ Auto-scaling and load balancing
- ✅ Automatic SSL certificates
- ✅ Built-in logging and metrics
- ✅ Zero infrastructure management
- ✅ Pay only for what you use

## Prerequisites

1. **doctl CLI** - Already installed ✓
2. **GitHub repository** - McGuireTechnology/API ✓
3. **Digital Ocean account** - Already authenticated ✓

## Quick Deploy

Deploy the app with one command:

```bash
./deploy/create-app.sh
```

This will:
1. Validate the app specification
2. Create the App Platform application
3. Deploy your code from GitHub
4. Provision SSL certificates
5. Set up automatic deployments

## Manual Deploy (Alternative)

If you prefer manual control:

```bash
# Validate the spec
doctl apps spec validate .do/app.yaml

# Create the app
doctl apps create --spec .do/app.yaml

# Get the app ID
APP_ID=$(doctl apps list --format ID --no-header)

# Watch deployment logs
doctl apps logs $APP_ID --follow --type BUILD
```

## Configuration

The app configuration is in `.do/app.yaml`:

- **Instance**: basic-xxs (512MB RAM, 1 vCPU) - $5/month
- **Region**: NYC
- **Auto-deploy**: Enabled on push to main branch
- **Health check**: `/health` endpoint

## Environment Variables

Required secrets (set in DO dashboard or via CLI):

```bash
# Database connection
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Digital Ocean Spaces (object storage)
SPACES_KEY=your_spaces_key
SPACES_SECRET=your_spaces_secret
```

Set via CLI:

```bash
# Get your app ID
APP_ID=$(doctl apps list --format ID --no-header)

# Update environment variables
doctl apps update $APP_ID \
  --env DATABASE_URL=your_database_url \
  --env SPACES_KEY=your_key \
  --env SPACES_SECRET=your_secret
```

## Custom Domain

After deployment:

1. Get your app's URL:
   ```bash
   doctl apps get $APP_ID --format DefaultIngress --no-header
   ```

2. Add CNAME record in your DNS:
   ```
   api.mcguire.technology → your-app-xyz.ondigitalocean.app
   ```

3. SSL certificate will be automatically provisioned within minutes

## Useful Commands

```bash
# List all apps
doctl apps list

# Get app details
doctl apps get $APP_ID

# View runtime logs
doctl apps logs $APP_ID --follow --type RUN

# View build logs
doctl apps logs $APP_ID --follow --type BUILD

# Trigger manual deployment
doctl apps create-deployment $APP_ID

# Delete the app
doctl apps delete $APP_ID
```

## Automatic Deployments

Every push to the `main` branch automatically:
1. Builds the application
2. Runs health checks
3. Deploys to production
4. Rolls back if deployment fails

No manual intervention needed!

## Cost

- **Basic plan**: $5/month (basic-xxs)
- **Professional plan**: $12/month (basic-xs) - for production
- **Bandwidth**: First 250GB free

App Platform pricing is more predictable than managing droplets + load balancers.

## Monitoring

View metrics in the Digital Ocean dashboard:
- Request rate
- Response times
- Error rates
- Memory/CPU usage

Or use the CLI:

```bash
doctl apps get-metrics $APP_ID
```

## Scaling

To scale up/down, edit `.do/app.yaml`:

```yaml
instance_count: 2  # Scale to 2 instances
instance_size_slug: basic-xs  # Upgrade to 1GB RAM
```

Then update:

```bash
doctl apps update $APP_ID --spec .do/app.yaml
```

## Troubleshooting

### Build fails
```bash
# View build logs
doctl apps logs $APP_ID --type BUILD

# Common issues:
# - Missing dependencies in pyproject.toml
# - Python version mismatch
# - Build command errors
```

### App won't start
```bash
# View runtime logs
doctl apps logs $APP_ID --type RUN

# Check health endpoint
curl https://your-app.ondigitalocean.app/health
```

### Environment variables
```bash
# List current env vars
doctl apps spec get $APP_ID

# Update env vars
doctl apps update $APP_ID --spec .do/app.yaml
```

## Migration from Droplet

If you created a droplet earlier, you can safely delete it:

```bash
# List droplets
doctl compute droplet list

# Delete droplet
doctl compute droplet delete 532708632
```

App Platform replaces the need for:
- Manual server setup
- Nginx configuration
- SSL certificate management
- Process management (systemd)
- Security updates

## Next Steps

1. Run `./deploy/create-app.sh` to deploy
2. Wait 5-10 minutes for initial deployment
3. Configure DNS CNAME record
4. Set environment secrets in DO dashboard
5. Push to main branch to deploy updates automatically

Your API will be live at `https://your-app.ondigitalocean.app` and `https://api.mcguire.technology` (after DNS setup).
