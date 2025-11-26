# SentraScan Platform - Test Documentation

## Overview

This directory contains comprehensive tests for the SentraScan Platform UI redesign implementation. The test suite covers functionality, accessibility, performance, and user experience across all UI components.

## Test Structure

### Test Organization

Tests are organized by category:

- **UI Tests** (`test_ui_*.py`) - User interface and interaction tests
- **API Tests** (`test_api.py`) - Backend API endpoint tests
- **Pipeline Tests** (`test_mcp_pipeline.py`, `test_model_scanner.py`) - Scanner functionality tests
- **Non-functional Tests** (`test_nonfunctional.py`) - Performance and concurrency tests
- **Smoke Tests** (`test_ui_smoke.py`) - Basic functionality verification

### UI Test Files

| File | Purpose | Coverage |
|------|---------|----------|
| `test_ui_smoke.py` | Basic smoke tests for login and forms | Login, scan forms |
| `test_ui_aria.py` | ARIA attributes and accessibility compliance | ARIA landmarks, labels, roles, live regions |
| `test_ui_chart_accessibility.py` | Chart accessibility (keyboard nav, ARIA) | Chart ARIA labels, role attributes, screen reader support |
| `test_ui_errors_empty.py` | Error handling and empty states | 404/500 pages, empty states, error messages |
| `test_ui_form_validation.py` | Form validation and error messages | Login form, scan forms, validation errors |
| `test_ui_mobile_navigation.py` | Mobile navigation (hamburger menu, drawer) | Touch targets, focus trap, ESC key, drawer functionality |
| `test_ui_modal_focus_esc.py` | Modal focus trap and ESC key | Focus trapping, ESC key, focus restoration |
| `test_ui_performance.py` | Performance testing (Core Web Vitals) | FCP, LCP, TTI, CLS metrics |
| `test_ui_progressive_enhancement.py` | Progressive enhancement (no-JS) | Forms, links, navigation without JavaScript |
| `test_ui_toast_stacking.py` | Toast notification stacking and auto-dismiss | Toast stacking, auto-dismiss, close buttons |

## Running Tests

### Prerequisites

1. **Python 3.11+** - Required for running tests
2. **Playwright** - For browser automation tests
3. **Docker** - For integration tests (optional, some tests skip if Docker unavailable)
4. **API Server** - Tests require the API to be running (via docker-compose or local server)

### Installation

```bash
# Install Python dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium

# Or install all browsers
playwright install
```

### Running All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src/sentrascan --cov-report=html --cov-report=term

# Run only UI tests
pytest tests/test_ui_*.py -v

# Run specific test file
pytest tests/test_ui_aria.py -v

# Run specific test
pytest tests/test_ui_aria.py::test_aria_landmarks_base -v
```

### Running Integration Tests

Integration tests require the API server to be running:

```bash
# Start API server (in separate terminal)
docker compose up

# Or run locally
sentrascan server

# Run integration tests
pytest tests/ -m integration -v
```

### Running Tests by Category

```bash
# Run accessibility tests
pytest tests/test_ui_aria.py tests/test_ui_chart_accessibility.py -v

# Run performance tests
pytest tests/test_ui_performance.py -v

# Run form validation tests
pytest tests/test_ui_form_validation.py -v

# Run mobile navigation tests
pytest tests/test_ui_mobile_navigation.py -v
```

## Test Configuration

### Fixtures

Tests use shared fixtures defined in `conftest.py`:

- `api_base` - API base URL (default: `http://localhost:8200`)
- `wait_api` - Waits for API to be ready
- `admin_key` - Admin API key for authentication
- `viewer_key` - Viewer API key for authentication
- `authenticated_page` - Playwright page with authentication
- `mobile_viewport` - Mobile viewport configuration

### Environment Variables

Tests can be configured via environment variables:

- `SENTRASCAN_API_BASE` - Override API base URL
- `SENTRASCAN_ADMIN_KEY` - Override admin API key
- `SENTRASCAN_VIEWER_KEY` - Override viewer API key

### Test Markers

Tests use pytest markers:

- `@pytest.mark.integration` - Integration tests requiring API server

Run tests by marker:

```bash
# Run only integration tests
pytest -m integration -v

# Skip integration tests
pytest -m "not integration" -v
```

## Test Coverage by Area

### 1. Accessibility Testing

**Files:** `test_ui_aria.py`, `test_ui_chart_accessibility.py`

**Coverage:**
- ARIA landmarks (header, nav, main, footer)
- ARIA labels on interactive elements
- ARIA roles (dialog, menu, alert, status)
- ARIA expanded/collapsed states
- ARIA live regions
- Chart accessibility (role="img", ARIA labels)
- Form accessibility (aria-describedby, aria-required, aria-invalid)
- Table accessibility (scope attributes, captions)

**Key Tests:**
- Landmark roles are present
- All interactive elements have accessible names
- Charts have descriptive ARIA labels
- Forms have proper ARIA associations

### 2. Form Validation Testing

**Files:** `test_ui_form_validation.py`

**Coverage:**
- Required field validation
- Minimum length validation
- Real-time validation
- Error message display
- ARIA error attributes
- Form submission prevention

**Key Tests:**
- Login form validates required fields
- Scan forms validate model path
- Error messages are displayed correctly
- ARIA attributes are set for errors

### 3. Modal and Focus Management

**Files:** `test_ui_modal_focus_esc.py`

**Coverage:**
- Focus trap within modals
- ESC key closes modals
- Focus restoration after modal closes
- Tab navigation cycles within modal
- Shift+Tab navigation

**Key Tests:**
- Focus is trapped in modals
- ESC key closes active modal
- Focus returns to trigger element
- Tab wraps correctly

### 4. Mobile Navigation

**Files:** `test_ui_mobile_navigation.py`

**Coverage:**
- Hamburger menu toggle
- Drawer opening/closing
- Touch target sizes (44x44px minimum)
- Focus trap in drawer
- ESC key closes drawer
- Overlay click closes drawer
- Body scroll prevention

**Key Tests:**
- Hamburger menu visible on mobile
- Drawer opens and closes correctly
- Touch targets meet minimum size
- Focus is trapped in drawer

### 5. Performance Testing

**Files:** `test_ui_performance.py`

**Coverage:**
- First Contentful Paint (FCP) < 1.5s
- Largest Contentful Paint (LCP) < 2.5s
- Time to Interactive (TTI) < 3.5s
- Cumulative Layout Shift (CLS) < 0.1

**Key Tests:**
- Dashboard page performance
- Scan list page performance
- Scan detail page performance
- Scan forms page performance
- Baselines page performance

### 6. Error Handling and Empty States

**Files:** `test_ui_errors_empty.py`

**Coverage:**
- 404 error page
- 500 error page
- API error handling (404, 403, 400)
- Form validation errors
- Empty scan list
- Empty findings
- Empty baselines
- Empty search results
- Empty chart data

**Key Tests:**
- Error pages display correctly
- API errors are handled properly
- Empty states show helpful messages
- Empty states have CTAs

### 7. Progressive Enhancement

**Files:** `test_ui_progressive_enhancement.py`

**Coverage:**
- Forms submit without JavaScript
- Links navigate without JavaScript
- Basic HTML structure
- Semantic HTML elements
- HTML5 validation
- Content accessibility

**Key Tests:**
- Forms have proper action/method attributes
- Links have href attributes
- Semantic HTML is present
- Content is accessible without JS

### 8. Toast Notifications

**Files:** `test_ui_toast_stacking.py`

**Coverage:**
- Toast stacking (multiple toasts)
- Auto-dismiss functionality
- Custom duration
- Close button functionality
- Stacking order
- Independent dismissal

**Key Tests:**
- Multiple toasts stack vertically
- Toasts auto-dismiss after duration
- Close buttons work in stacked toasts
- Toasts dismiss independently

### 9. Chart Accessibility

**Files:** `test_ui_chart_accessibility.py`

**Coverage:**
- ARIA labels on charts
- Role="img" on canvas elements
- Chart section headings
- Keyboard navigation
- Screen reader support
- Chart context information

**Key Tests:**
- Charts have descriptive ARIA labels
- Charts have role="img"
- Chart sections have headings
- Charts don't trap focus

## Test Execution Best Practices

### 1. Run Tests Before Committing

```bash
# Run all tests
pytest tests/ -v

# Run with linting
pytest tests/ && ruff check tests/
```

### 2. Run Specific Test Categories

```bash
# Quick smoke tests
pytest tests/test_ui_smoke.py -v

# Accessibility tests
pytest tests/test_ui_aria.py tests/test_ui_chart_accessibility.py -v

# Form tests
pytest tests/test_ui_form_validation.py -v
```

### 3. Debugging Tests

```bash
# Run with verbose output
pytest tests/test_ui_aria.py -vv

# Run with print statements visible
pytest tests/test_ui_aria.py -s

# Run with browser visible (no headless)
# Modify test to use headless=False in Playwright
```

### 4. Test Coverage

```bash
# Generate HTML coverage report
pytest tests/ --cov=src/sentrascan --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Known Limitations

### Environment Dependencies

- Some tests require Docker to be running
- Integration tests require API server to be accessible
- Performance tests may vary based on system load

### Test Skipping

Tests may skip if:
- API server is not available
- Docker is not running
- Required test data is not present
- Browser/Playwright is not installed

### Manual Testing

Some aspects require manual testing:
- Screen reader testing (NVDA, JAWS, VoiceOver)
- Cross-browser compatibility
- Color contrast verification
- Touch device testing

## Adding New Tests

### Test File Structure

```python
"""
Tests for [feature name].

Tests:
- Test aspect 1
- Test aspect 2
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def authenticated_page(page: Page, api_base, admin_key):
    """Create an authenticated page for testing."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    page.fill('input[name="api_key"]', admin_key)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{api_base}/**", timeout=5000)
    return page


@pytest.mark.integration
def test_feature_aspect(authenticated_page: Page, api_base):
    """Test description."""
    authenticated_page.goto(f"{api_base}/path", wait_until="networkidle")
    
    # Test implementation
    element = authenticated_page.locator("selector")
    expect(element).to_be_visible()
    
    # Assertions
    assert condition, "Error message"
```

### Test Naming Conventions

- Test files: `test_ui_<feature>.py`
- Test functions: `test_<feature>_<aspect>`
- Use descriptive names that explain what is being tested

### Test Organization

- Group related tests in sections with comments
- Use fixtures for common setup
- Use markers for test categorization
- Include docstrings explaining test purpose

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest tests/ -v --tb=short
    pytest tests/ --cov=src/sentrascan --cov-report=xml
```

## Troubleshooting

### Tests Fail with "API not ready"

**Solution:** Ensure API server is running:
```bash
docker compose up
# Or
sentrascan server
```

### Playwright Tests Fail

**Solution:** Install Playwright browsers:
```bash
playwright install chromium
```

### Tests Timeout

**Solution:** Increase timeout or check network:
```bash
# Increase timeout in test
page.wait_for_timeout(5000)  # 5 seconds
```

### Tests Skip Unexpectedly

**Solution:** Check skip conditions in test code and ensure prerequisites are met.

## Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)

## Test Maintenance

### Regular Updates

- Update tests when UI changes
- Add tests for new features
- Remove obsolete tests
- Update documentation when test structure changes

### Test Review

- Review test coverage regularly
- Identify gaps in test coverage
- Refactor tests for maintainability
- Ensure tests are fast and reliable

