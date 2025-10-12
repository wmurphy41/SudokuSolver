#!/bin/bash
set -e  # Exit on any error

# ============================================================================
# Build and Push Docker Images to GitHub Container Registry (GHCR)
# ============================================================================
# This script builds linux/amd64 images for AWS Lightsail deployment
# and pushes them to GHCR with version tag and 'latest' tag.
#
# Usage: ./scripts/build-push.sh v0.1.0
# Requires: GHCR_TOKEN environment variable set with a GitHub PAT
# ============================================================================

# Configuration - REPLACE WITH YOUR GITHUB USERNAME
GHCR_USERNAME="wmurphy41"
REGISTRY="ghcr.io"
BACKEND_IMAGE="${REGISTRY}/${GHCR_USERNAME}/sudoku-backend"
WEB_IMAGE="${REGISTRY}/${GHCR_USERNAME}/sudoku-web"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for version argument
if [ -z "$1" ]; then
    echo -e "${RED}Error: Version argument required${NC}"
    echo "Usage: $0 <version>"
    echo "Example: $0 v0.1.0"
    exit 1
fi

VERSION="$1"
echo -e "${GREEN}Building version: ${VERSION}${NC}"

# Validate version format (should start with 'v')
if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+.*$ ]]; then
    echo -e "${YELLOW}Warning: Version should follow format v0.1.0${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for GHCR_TOKEN
if [ -z "$GHCR_TOKEN" ]; then
    echo -e "${RED}Error: GHCR_TOKEN environment variable not set${NC}"
    echo "Please set your GitHub Personal Access Token:"
    echo "  export GHCR_TOKEN=your_github_token"
    exit 1
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker not found${NC}"
    echo "Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check for docker buildx
if ! docker buildx version &> /dev/null; then
    echo -e "${RED}Error: docker buildx not found${NC}"
    echo "Please ensure Docker Desktop is installed and buildx is enabled"
    echo "Run: docker buildx install"
    exit 1
fi

# Create buildx builder if it doesn't exist
if ! docker buildx inspect multiarch &> /dev/null 2>&1; then
    echo -e "${YELLOW}Creating buildx builder for multi-platform builds...${NC}"
    docker buildx create --name multiarch --use
    docker buildx inspect --bootstrap
else
    docker buildx use multiarch
fi

# Login to GHCR
echo -e "${GREEN}Logging in to GitHub Container Registry...${NC}"
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to login to GHCR${NC}"
    exit 1
fi

echo -e "${GREEN}Login successful!${NC}"

# Build and push backend image
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Building and pushing backend image...${NC}"
echo -e "${GREEN}========================================${NC}"
# Platform: linux/amd64 for AWS Lightsail x86_64 instances
# Build context is project root (.) to access src/ directory
docker buildx build --platform linux/amd64 \
    -t "${BACKEND_IMAGE}:${VERSION}" \
    -t "${BACKEND_IMAGE}:latest" \
    -f web/backend/Dockerfile \
    . \
    --push

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Backend image build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend image built and pushed successfully!${NC}"

# Build and push web (frontend + nginx) image
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Building and pushing web image...${NC}"
echo -e "${GREEN}========================================${NC}"
# Platform: linux/amd64 for AWS Lightsail x86_64 instances
docker buildx build --platform linux/amd64 \
    -t "${WEB_IMAGE}:${VERSION}" \
    -t "${WEB_IMAGE}:latest" \
    -f web/frontend/Dockerfile.prod \
    web \
    --push

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Web image build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Web image built and pushed successfully!${NC}"

# Success summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ All images built and pushed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Images pushed to GHCR:"
echo "  Backend: ${BACKEND_IMAGE}:${VERSION}"
echo "           ${BACKEND_IMAGE}:latest"
echo "  Web:     ${WEB_IMAGE}:${VERSION}"
echo "           ${WEB_IMAGE}:latest"
echo ""
echo "To deploy on your Lightsail server:"
echo "  1. Update docker-compose.yml to use these image tags"
echo "  2. Run: docker compose pull"
echo "  3. Run: docker compose up -d"
echo ""
echo -e "${GREEN}Done!${NC}"

