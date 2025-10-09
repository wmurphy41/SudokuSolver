# Deploying SudokuSolver with Pre-built Images

This guide explains how to build Docker images locally and deploy them to AWS Lightsail using GitHub Container Registry (GHCR).

## Prerequisites

### Local Machine (Windows or Linux/Mac)

1. **Docker Desktop** with buildx support
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker buildx version`

2. **GitHub Personal Access Token (PAT)** with `write:packages` permission
   - Create at: https://github.com/settings/tokens
   - Scopes needed: `write:packages`, `read:packages`, `delete:packages`

### AWS Lightsail Server

1. **Docker and Docker Compose** installed
2. **GitHub PAT** (read:packages permission) for pulling images

## Building and Pushing Images

### Step 1: Set Your GitHub Token

**On Windows (PowerShell):**
```powershell
$env:GHCR_TOKEN = "ghp_your_token_here"
```

**On Linux/Mac (Bash):**
```bash
export GHCR_TOKEN="ghp_your_token_here"
```

### Step 2: Build and Push Images

**On Windows:**
```powershell
.\scripts\build-push.ps1 v0.1.0
```

**On Linux/Mac:**
```bash
chmod +x scripts/build-push.sh
./scripts/build-push.sh v0.1.0
```

This will:
- Build `linux/amd64` images (compatible with Lightsail x86_64 instances)
- Tag images with both version tag (`v0.1.0`) and `latest`
- Push to GHCR: `ghcr.io/wmurphy41/sudoku-backend` and `ghcr.io/wmurphy41/sudoku-web`

### Step 3: Verify Images

Visit: https://github.com/wmurphy41?tab=packages

You should see:
- `sudoku-backend`
- `sudoku-web`

## Deploying to Lightsail

### Step 1: Update docker-compose.yml

On your Lightsail server, edit `/home/ubuntu/SudokuSolver/web/docker-compose.yml`:

```yaml
# Docker Compose configuration for SudokuSolver web application
# Using pre-built images from GitHub Container Registry

services:
  # FastAPI backend service
  backend:
    image: ghcr.io/wmurphy41/sudoku-backend:v0.1.0
    container_name: sudoku-backend
    expose:
      - "8000"
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Nginx + React frontend service
  web:
    image: ghcr.io/wmurphy41/sudoku-web:v0.1.0
    container_name: sudoku-web
    ports:
      - "80:80"
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Step 2: Login to GHCR on Lightsail

**First time only:**
```bash
# Set your GitHub token
export GHCR_TOKEN="ghp_your_token_here"

# Login to GHCR
echo "$GHCR_TOKEN" | docker login ghcr.io -u wmurphy41 --password-stdin
```

Docker will cache your credentials, so you only need to do this once.

### Step 3: Deploy

```bash
cd /home/ubuntu/SudokuSolver/web

# Pull the latest images
docker compose pull

# Stop old containers and start new ones
docker compose down
docker compose up -d

# Verify services are running
docker compose ps
```

### Step 4: Verify Deployment

```bash
# Test backend
curl http://localhost/api/healthz

# Test frontend
curl http://localhost

# Check logs if needed
docker compose logs backend
docker compose logs web
```

## Updating to a New Version

### Build and Push New Version Locally

```powershell
# Windows
.\scripts\build-push.ps1 v0.2.0
```

```bash
# Linux/Mac
./scripts/build-push.sh v0.2.0
```

### Deploy New Version on Lightsail

```bash
cd /home/ubuntu/SudokuSolver/web

# Update docker-compose.yml to use new version tag
# Change: image: ghcr.io/wmurphy41/sudoku-backend:v0.1.0
# To:     image: ghcr.io/wmurphy41/sudoku-backend:v0.2.0
nano docker-compose.yml

# Pull and deploy
docker compose pull
docker compose up -d
```

## Rolling Back

If something goes wrong, rollback to the previous version:

```bash
cd /home/ubuntu/SudokuSolver/web

# Update docker-compose.yml back to previous version
nano docker-compose.yml  # Change v0.2.0 back to v0.1.0

# Pull and restart
docker compose pull
docker compose up -d
```

## Using 'latest' Tag

Instead of version tags, you can use `latest` for automatic updates:

```yaml
services:
  backend:
    image: ghcr.io/wmurphy41/sudoku-backend:latest
  web:
    image: ghcr.io/wmurphy41/sudoku-web:latest
```

Then deployments are simpler:
```bash
docker compose pull && docker compose up -d
```

**Note:** Using `latest` is convenient but makes rollbacks harder. Use version tags in production.

## Troubleshooting

### Build Fails Locally

**Check Docker buildx:**
```bash
docker buildx version
docker buildx ls
```

**Recreate builder:**
```bash
docker buildx rm multiarch
docker buildx create --name multiarch --use --bootstrap
```

### Authentication Errors

**Check token permissions:**
- Token must have `write:packages` scope
- Token must not be expired

**Re-login:**
```bash
# Logout first
docker logout ghcr.io

# Login again
echo "$GHCR_TOKEN" | docker login ghcr.io -u wmurphy41 --password-stdin
```

### Pull Fails on Lightsail

**Check you're logged in:**
```bash
docker login ghcr.io
```

**Check image exists:**
```bash
docker manifest inspect ghcr.io/wmurphy41/sudoku-backend:v0.1.0
```

**Make sure images are public or you have read access:**
- Go to https://github.com/wmurphy41?tab=packages
- Click on each package
- Settings → Change visibility or manage access

### Container Won't Start

**Check logs:**
```bash
docker compose logs backend
docker compose logs web
```

**Check image platform:**
```bash
docker image inspect ghcr.io/wmurphy41/sudoku-backend:v0.1.0 | grep Architecture
# Should show: "Architecture": "amd64"
```

## Image Management

### List Local Images
```bash
docker images | grep ghcr.io/wmurphy41
```

### Remove Old Images
```bash
# Remove specific version
docker rmi ghcr.io/wmurphy41/sudoku-backend:v0.1.0

# Remove all unused images
docker image prune -a
```

### Delete Package from GHCR

1. Go to https://github.com/wmurphy41?tab=packages
2. Click on the package
3. Settings → Delete this package

## Best Practices

1. **Use version tags** for production deployments
2. **Test locally** before pushing to GHCR
3. **Keep old versions** in GHCR for quick rollbacks
4. **Document changes** in version tags (v0.1.0, v0.2.0, etc.)
5. **Use secrets** for tokens (never commit them)
6. **Make images public** or manage access carefully

## Quick Reference

### Build and Push
```bash
# Set token
export GHCR_TOKEN="ghp_..."  # or $env:GHCR_TOKEN on PowerShell

# Build and push
./scripts/build-push.sh v0.1.0
```

### Deploy on Lightsail
```bash
cd /home/ubuntu/SudokuSolver/web
docker compose pull
docker compose up -d
```

### Check Status
```bash
docker compose ps
docker compose logs -f
curl http://localhost/api/healthz
```

## Support

For issues:
1. Check the troubleshooting section above
2. Review Docker logs: `docker compose logs`
3. Verify GHCR access: https://github.com/wmurphy41?tab=packages

