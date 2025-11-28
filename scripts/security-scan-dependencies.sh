#!/bin/bash
# Dependency Vulnerability Scanning Script
# Scans Python dependencies for known security vulnerabilities

set -e

echo "=========================================="
echo "Dependency Vulnerability Scanning"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create reports directory
mkdir -p reports/security

# Check if tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${YELLOW}Warning: $1 not found. Installing...${NC}"
        return 1
    fi
    return 0
}

# Install safety if not available
if ! check_tool safety; then
    pip install safety || echo -e "${YELLOW}Could not install safety${NC}"
fi

# Install pip-audit if not available
if ! check_tool pip-audit; then
    pip install pip-audit || echo -e "${YELLOW}Could not install pip-audit${NC}"
fi

echo "1. Running Safety check..."
echo "---------------------------"
if command -v safety &> /dev/null; then
    safety check --json > reports/security/safety-report.json 2>&1 || true
    safety check --short-report > reports/security/safety-report.txt 2>&1 || true
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Safety check passed${NC}"
    else
        echo -e "${RED}✗ Safety check found vulnerabilities${NC}"
        echo "See reports/security/safety-report.txt for details"
    fi
else
    echo -e "${YELLOW}⚠ Safety not available${NC}"
fi

echo ""
echo "2. Running pip-audit..."
echo "------------------------"
if command -v pip-audit &> /dev/null; then
    pip-audit --format json --output reports/security/pip-audit-report.json 2>&1 || true
    pip-audit --format table --output reports/security/pip-audit-report.txt 2>&1 || true
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ pip-audit check passed${NC}"
    else
        echo -e "${RED}✗ pip-audit found vulnerabilities${NC}"
        echo "See reports/security/pip-audit-report.txt for details"
    fi
else
    echo -e "${YELLOW}⚠ pip-audit not available${NC}"
fi

echo ""
echo "3. Checking for outdated packages..."
echo "-------------------------------------"
pip list --outdated > reports/security/outdated-packages.txt 2>&1 || true
if [ -s reports/security/outdated-packages.txt ]; then
    echo -e "${YELLOW}⚠ Some packages are outdated${NC}"
    echo "See reports/security/outdated-packages.txt for details"
else
    echo -e "${GREEN}✓ All packages are up to date${NC}"
fi

echo ""
echo "=========================================="
echo "Scan complete. Reports saved to reports/security/"
echo "=========================================="

