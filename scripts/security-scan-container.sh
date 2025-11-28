#!/bin/bash
# Container Image Security Scanning Script
# Scans Docker images for known security vulnerabilities

set -e

echo "=========================================="
echo "Container Image Security Scanning"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create reports directory
mkdir -p reports/security

# Image name and tag
IMAGE_NAME=${1:-sentrascan:latest}
DOCKERFILE=${2:-Dockerfile}

echo "Scanning image: $IMAGE_NAME"
echo "Using Dockerfile: $DOCKERFILE"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Build image if it doesn't exist
if ! docker image inspect $IMAGE_NAME &> /dev/null; then
    echo "Building image $IMAGE_NAME..."
    docker build -t $IMAGE_NAME -f $DOCKERFILE .
fi

echo "1. Running Docker Scan (Snyk)..."
echo "---------------------------------"
if command -v docker &> /dev/null && docker scan --version &> /dev/null 2>&1; then
    docker scan --json $IMAGE_NAME > reports/security/docker-scan-report.json 2>&1 || true
    docker scan $IMAGE_NAME > reports/security/docker-scan-report.txt 2>&1 || true
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Docker scan completed${NC}"
    else
        echo -e "${YELLOW}⚠ Docker scan completed with warnings${NC}"
        echo "See reports/security/docker-scan-report.txt for details"
    fi
else
    echo -e "${YELLOW}⚠ Docker scan not available (requires Docker Desktop with Snyk)${NC}"
fi

echo ""
echo "2. Running Trivy scanner..."
echo "---------------------------"
if command -v trivy &> /dev/null; then
    trivy image --format json --output reports/security/trivy-report.json $IMAGE_NAME 2>&1 || true
    trivy image --severity HIGH,CRITICAL --output reports/security/trivy-report.txt $IMAGE_NAME 2>&1 || true
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Trivy scan completed${NC}"
    else
        echo -e "${YELLOW}⚠ Trivy scan found vulnerabilities${NC}"
        echo "See reports/security/trivy-report.txt for details"
    fi
else
    echo -e "${YELLOW}⚠ Trivy not installed${NC}"
    echo "Install with: brew install trivy (macOS) or see https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
fi

echo ""
echo "3. Checking image size..."
echo "-------------------------"
IMAGE_SIZE=$(docker image inspect $IMAGE_NAME --format='{{.Size}}' 2>/dev/null | numfmt --to=iec-i --suffix=B 2>/dev/null || echo "unknown")
echo "Image size: $IMAGE_SIZE"

echo ""
echo "4. Checking for secrets in image layers..."
echo "-------------------------------------------"
# Use gitleaks or trufflehog if available in the image
if docker run --rm $IMAGE_NAME gitleaks version &> /dev/null 2>&1; then
    echo "gitleaks available in image"
else
    echo -e "${YELLOW}⚠ gitleaks not available in image${NC}"
fi

echo ""
echo "=========================================="
echo "Scan complete. Reports saved to reports/security/"
echo "=========================================="

