# Environment Configuration Guide

## Overview

This project uses environment-specific configuration files to manage settings across different deployment environments. Each environment has its own optimized settings.

## Available Environment Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `.env` | Your personal local config | Daily development (not in git) |
| `.env.example` | Template with all options | Reference for available settings |
| `.env.development` | Development template | Copy to `.env` for local dev |
| `.env.testing` | Testing configuration | Automated tests (CI/CD) |
| `.env.production` | Production template | Deployment to production |

## Quick Start

### For Local Development

```bash
# Option 1: Copy the development template
cp .env.development .env

# Option 2: Copy the example template
cp .env.example .env

# Option 3: Use the existing .env (already configured)
# Just start coding!
```

### For Testing

Tests automatically use `.env.testing` settings. No action needed.

```bash
poetry run pytest
```

### For Production Deployment

```bash
# Copy the production template
cp .env.production .env

# IMPORTANT: Edit .env and replace all placeholder values
# - Generate secure secrets
# - Add your database URL
# - Set your domain names
# - Review the checklist in the file
nano .env
```

## Environment Settings Breakdown

### Development (`.env.development`)

Optimized for local development:
- ✅ Debug mode enabled
- ✅ Verbose logging (SQL echo)
- ✅ In-memory database (fast, no setup)
- ✅ Relaxed security (all hosts allowed)
- ✅ No email verification required
- ✅ Dummy secret keys (not secure!)

### Testing (`.env.testing`)

Optimized for automated tests:
- ✅ In-memory database (`:memory:`)
- ✅ Fast, isolated tests
- ✅ No external dependencies
- ✅ Reproducible results
- ✅ Minimal logging
- ✅ Mock external services

### Production (`.env.production`)

Optimized for production deployment:
- ✅ Debug mode disabled
- ✅ PostgreSQL database
- ✅ Strict security settings
- ✅ Email verification required
- ✅ Strong password policies
- ✅ Real secret keys (you must set these!)

## Configuration Structure

Settings are organized by scope:

### Core Settings (`APP_*`)
Application-wide configuration:
- Application name and version
- Environment mode
- Debug settings
- Host and port

### Database Settings (`DB_*`)
Database connection and pooling:
- Connection URL
- SQL logging
- Connection pool size

### CORS Settings (`CORS_*`)
Cross-Origin Resource Sharing:
- Allowed origins (frontend URLs)
- Credentials handling
- Allowed methods/headers

### Security Settings (`SECURITY_*`)
Security and authentication:
- Allowed hosts
- Secret key for signing tokens

### Module Settings (`USERS_*`, etc.)
Domain-specific settings for each bounded context:
- Repository backend selection
- Business rules (password length, etc.)
- Feature flags (email verification)

## Best Practices

### ✅ DO

- Keep `.env` in `.gitignore` (already configured)
- Use templates for team consistency
- Generate strong secrets for production
- Review production checklist before deploying
- Use environment-specific settings
- Document custom settings

### ❌ DON'T

- Commit `.env` files with real secrets
- Use development settings in production
- Use wildcards (`*`) in production security settings
- Share secret keys across environments
- Use simple passwords/secrets

## Generating Secure Secrets

```bash
# Generate a secure secret key (32 bytes = 64 hex characters)
openssl rand -hex 32

# On Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Environment Variables Reference

### Required Settings

These must be set in all environments:

```bash
APP_NAME=TruLedgr API
APP_ENVIRONMENT=development|production|testing
DB_URL=<database-connection-string>
SECURITY_SECRET_KEY=<random-secret-key>
```

### Optional Settings

These have sensible defaults but can be customized:

```bash
APP_DEBUG=true|false
DB_ECHO=true|false
CORS_ALLOWED_ORIGINS=<comma-separated-urls>
USERS_REPOSITORY_BACKEND=inmemory|sqlalchemy
```

## Troubleshooting

### "No such file: .env"

Create your environment file:
```bash
cp .env.development .env
```

### "Extra inputs are not permitted"

You may have an old environment variable defined. Check:
```bash
env | grep -E "^(APP_|DB_|CORS_|SECURITY_|USERS_)"
```

### "ValidationError: APP_ENVIRONMENT"

Must be one of: `development`, `staging`, `production`, `testing`

### Tests failing with database errors

Ensure `.env.testing` is being used:
```bash
# Tests should automatically use .env.testing
poetry run pytest -v
```

## Adding New Settings

When adding settings for a new module:

1. **Define in code** (`api/your_module/settings.py`):
```python
class YourModuleSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="YOURMODULE_",
        extra="ignore",
    )
    some_setting: str = "default"
```

2. **Add to all environment templates**:
```bash
# .env.development
YOURMODULE_SOME_SETTING=dev-value

# .env.testing  
YOURMODULE_SOME_SETTING=test-value

# .env.production
YOURMODULE_SOME_SETTING=prod-value

# .env.example
YOURMODULE_SOME_SETTING=example-value
```

3. **Document in this README**

## Production Deployment Checklist

Before deploying to production:

- [ ] Copied `.env.production` to `.env`
- [ ] Generated secure `SECURITY_SECRET_KEY`
- [ ] Set production database URL
- [ ] Updated `CORS_ALLOWED_ORIGINS` with real domains
- [ ] Set `SECURITY_ALLOWED_HOSTS` (no wildcards!)
- [ ] Set `APP_DEBUG=false`
- [ ] Set `APP_ENVIRONMENT=production`
- [ ] Enabled `USERS_REQUIRE_EMAIL_VERIFICATION`
- [ ] Increased `USERS_MIN_PASSWORD_LENGTH` to 12+
- [ ] Tested in staging environment first
- [ ] Configured database backups
- [ ] Set up monitoring/logging
- [ ] Verified all secrets are secure

## Support

For questions about environment configuration, see:
- `docs/developer/settings-architecture.md` - Full architecture documentation
- Project README - General setup instructions
