# ============================================================================
# Build and Push Docker Images to GitHub Container Registry (GHCR)
# ============================================================================
# This script builds linux/amd64 images for AWS Lightsail deployment
# and pushes them to GHCR with version tag and 'latest' tag.
#
# Usage: .\scripts\build-push.ps1 v0.1.0
# Requires: $env:GHCR_TOKEN set with a GitHub PAT
# ============================================================================

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Version
)

# Configuration - REPLACE WITH YOUR GITHUB USERNAME
$GHCR_USERNAME = "wmurphy41"
$REGISTRY = "ghcr.io"
$BACKEND_IMAGE = "$REGISTRY/$GHCR_USERNAME/sudoku-backend"
$WEB_IMAGE = "$REGISTRY/$GHCR_USERNAME/sudoku-web"

# Error handling
$ErrorActionPreference = "Stop"

Write-Host "Building version: $Version" -ForegroundColor Green

# Validate version format (should start with 'v')
if ($Version -notmatch '^v\d+\.\d+\.\d+') {
    Write-Host "Warning: Version should follow format v0.1.0" -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        exit 1
    }
}

# Check for GHCR_TOKEN
if (-not $env:GHCR_TOKEN) {
    Write-Host "Error: GHCR_TOKEN environment variable not set" -ForegroundColor Red
    Write-Host "Please set your GitHub Personal Access Token:" -ForegroundColor Red
    Write-Host '  $env:GHCR_TOKEN = "your_github_token"' -ForegroundColor Yellow
    exit 1
}

# Check for Docker
try {
    docker version | Out-Null
} catch {
    Write-Host "Error: Docker not found" -ForegroundColor Red
    Write-Host "Please install Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check for docker buildx
try {
    docker buildx version | Out-Null
} catch {
    Write-Host "Error: docker buildx not found" -ForegroundColor Red
    Write-Host "Please ensure Docker Desktop is installed and buildx is enabled" -ForegroundColor Yellow
    Write-Host "Run: docker buildx install" -ForegroundColor Yellow
    exit 1
}

# Create buildx builder if it doesn't exist
$builderExists = docker buildx inspect multiarch 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating buildx builder for multi-platform builds..." -ForegroundColor Yellow
    docker buildx create --name multiarch --use
    docker buildx inspect --bootstrap
} else {
    docker buildx use multiarch
}

# Login to GHCR
Write-Host "Logging in to GitHub Container Registry..." -ForegroundColor Green
$env:GHCR_TOKEN | docker login ghcr.io -u $GHCR_USERNAME --password-stdin

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to login to GHCR" -ForegroundColor Red
    exit 1
}

Write-Host "Login successful!" -ForegroundColor Green

# Build and push backend image
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Building and pushing backend image..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Platform: linux/amd64 for AWS Lightsail x86_64 instances
# Build context is project root (.) to access src/ directory
docker buildx build --platform linux/amd64 `
    -t "${BACKEND_IMAGE}:${Version}" `
    -t "${BACKEND_IMAGE}:latest" `
    -f web/backend/Dockerfile `
    . `
    --push

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Backend image build failed" -ForegroundColor Red
    exit 1
}

Write-Host "Backend image built and pushed successfully!" -ForegroundColor Green

# Build and push web (frontend + nginx) image
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Building and pushing web image..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Platform: linux/amd64 for AWS Lightsail x86_64 instances
# Build args for subpath deployment: /sudokusolver/
docker buildx build --platform linux/amd64 `
    --build-arg VITE_BASE_PATH=/sudokusolver/ `
    --build-arg VITE_API_BASE=/sudokusolver/api `
    -t "${WEB_IMAGE}:${Version}" `
    -t "${WEB_IMAGE}:latest" `
    -f web/frontend/Dockerfile.prod `
    web `
    --push

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Web image build failed" -ForegroundColor Red
    exit 1
}

Write-Host "Web image built and pushed successfully!" -ForegroundColor Green

# Success summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "All images built and pushed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Images pushed to GHCR:" -ForegroundColor Cyan
Write-Host "  Backend: ${BACKEND_IMAGE}:${Version}" -ForegroundColor White
Write-Host "           ${BACKEND_IMAGE}:latest" -ForegroundColor White
Write-Host "  Web:     ${WEB_IMAGE}:${Version}" -ForegroundColor White
Write-Host "           ${WEB_IMAGE}:latest" -ForegroundColor White
Write-Host ""
Write-Host "To deploy on your Lightsail server:" -ForegroundColor Cyan
Write-Host "  1. Update docker-compose.yml to use these image tags" -ForegroundColor White
Write-Host "  2. Run: docker compose pull" -ForegroundColor White
Write-Host "  3. Run: docker compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "Done!" -ForegroundColor Green

