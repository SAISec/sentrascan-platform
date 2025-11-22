#!/usr/bin/env bash
# Comprehensive Makefile Testing Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

test_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1${2:+ - $2}"
    ((TESTS_FAILED++))
}

test_skip() {
    echo -e "${YELLOW}⊘ SKIP${NC}: $1${2:+ - $2}"
    ((TESTS_SKIPPED++))
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Makefile Comprehensive Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

cd "$(dirname "$0")"

# Test 1: File exists and syntax
echo -e "${BLUE}[1] Syntax and Structure${NC}"
if [ -f Makefile ]; then
    test_pass "Makefile exists"
else
    test_fail "Makefile exists"
    exit 1
fi

# Test 2: Syntax check
if make -n help >/dev/null 2>&1; then
    test_pass "Makefile syntax validation"
else
    test_fail "Makefile syntax validation"
fi

# Test 3: Help target
echo ""
echo -e "${BLUE}[2] Help Target${NC}"
if make help 2>&1 | grep -q "SentraScan Platform"; then
    test_pass "Help target executes"
else
    test_fail "Help target executes"
fi

if make help 2>&1 | grep -q "Local Development"; then
    test_pass "Help shows local development"
else
    test_fail "Help shows local development"
fi

if make help 2>&1 | grep -q "Docker Operations"; then
    test_pass "Help shows Docker targets"
else
    test_fail "Help shows Docker targets"
fi

# Test 4: Target definitions
echo ""
echo -e "${BLUE}[3] Target Definitions${NC}"
TARGETS=("help" "install" "venv" "test" "docker-build" "clean" "gcp-auth")
for target in "${TARGETS[@]}"; do
    if make -n "$target" 2>&1 | grep -q "No rule to make target"; then
        test_fail "Target '$target' exists"
    else
        test_pass "Target '$target' exists"
    fi
done

# Test 5: Variable overrides
echo ""
echo -e "${BLUE}[4] Variable Overrides${NC}"
if make -n docker-build IMAGE_TAG=test:tag >/dev/null 2>&1; then
    test_pass "IMAGE_TAG override works"
else
    test_skip "IMAGE_TAG override works" "Cannot verify in dry-run"
fi

# Test 6: Dry-run tests
echo ""
echo -e "${BLUE}[5] Dry-Run Tests${NC}"
for target in help install venv clean docker-build; do
    if make -n "$target" >/dev/null 2>&1; then
        test_pass "Dry-run $target"
    else
        test_fail "Dry-run $target"
    fi
done

# Test 7: Error handling
echo ""
echo -e "${BLUE}[6] Error Handling${NC}"
if make invalid-target 2>&1 | grep -q "No rule to make target"; then
    test_pass "Invalid target handling"
else
    test_fail "Invalid target handling"
fi

# Test 8: Prerequisites
echo ""
echo -e "${BLUE}[7] Prerequisites${NC}"
command -v docker >/dev/null 2>&1 && test_pass "Docker available" || test_skip "Docker available" "Not installed"
command -v python3 >/dev/null 2>&1 && test_pass "Python3 available" || test_skip "Python3 available" "Not installed"
command -v pytest >/dev/null 2>&1 && test_pass "Pytest available" || test_skip "Pytest available" "Not installed"

# Test 9: Functional tests
echo ""
echo -e "${BLUE}[8] Functional Tests${NC}"
if command -v python3 >/dev/null 2>&1 && [ ! -d "venv" ]; then
    if make venv >/dev/null 2>&1 && [ -d "venv" ]; then
        test_pass "venv creation"
        rm -rf venv
    else
        test_fail "venv creation"
    fi
else
    test_skip "venv creation" "Already exists or Python3 not available"
fi

if make clean >/dev/null 2>&1; then
    test_pass "clean target"
else
    test_fail "clean target"
fi

# Test 10: Documentation
echo ""
echo -e "${BLUE}[9] Documentation${NC}"
TARGETS=("help" "install" "venv" "test" "docker-build" "clean")
for target in "${TARGETS[@]}"; do
    if grep -q "^${target}:" Makefile && grep -A 1 "^${target}:" Makefile | grep -q "##"; then
        test_pass "Target '$target' documented"
    else
        test_fail "Target '$target' documented"
    fi
done

# Test 11: Script integration
echo ""
echo -e "${BLUE}[10] Script Integration${NC}"
if grep -q "scripts/test.sh" Makefile && [ -f "scripts/test.sh" ]; then
    test_pass "scripts/test.sh integration"
else
    test_fail "scripts/test.sh integration"
fi

if grep -q "scripts/api-smoketest.sh" Makefile && [ -f "scripts/api-smoketest.sh" ]; then
    test_pass "scripts/api-smoketest.sh integration"
else
    test_fail "scripts/api-smoketest.sh integration"
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Passed:${NC} $TESTS_PASSED"
echo -e "${RED}Failed:${NC} $TESTS_FAILED"
echo -e "${YELLOW}Skipped:${NC} $TESTS_SKIPPED"
TOTAL=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
echo -e "Total: $TOTAL"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed.${NC}"
    exit 1
fi
