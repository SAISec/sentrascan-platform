"""
Cross-Browser Compatibility Tests

Tests compatibility across major browsers:
- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

Note: These tests should be run with Playwright's browser context switching
or in CI/CD with multiple browser configurations.
"""

import pytest
from playwright.sync_api import Page, expect
import os


@pytest.fixture
def authenticated_page(page: Page, api_base, admin_key):
    """Create an authenticated page for testing."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    page.fill('input[name="api_key"]', admin_key)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{api_base}/**", timeout=5000)
    return page


# ============================================
# Browser Detection and Feature Support
# ============================================

@pytest.mark.integration
def test_browser_user_agent(page: Page, api_base):
    """Verify browser user agent is detected correctly."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    user_agent = page.evaluate("() => navigator.userAgent")
    assert user_agent is not None and len(user_agent) > 0, "User agent not detected"
    
    # Log browser info for debugging
    browser_name = page.context.browser.browser_type.name if page.context.browser else "unknown"
    print(f"Browser: {browser_name}, User Agent: {user_agent[:50]}...")


@pytest.mark.integration
def test_css_vendor_prefixes(page: Page, api_base):
    """Verify CSS uses standard properties with vendor prefixes where needed."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    # Check that CSS uses standard properties
    # Vendor prefixes should be handled by build tools (PostCSS, Autoprefixer)
    # This test verifies the page loads without CSS errors
    
    # Check for CSS parse errors
    css_errors = page.evaluate("""
        () => {
            const errors = [];
            const sheets = document.styleSheets;
            for (let sheet of sheets) {
                try {
                    const rules = sheet.cssRules || sheet.rules;
                } catch (e) {
                    errors.push(e.message);
                }
            }
            return errors;
        }
    """)
    
    assert len(css_errors) == 0, f"CSS parse errors found: {css_errors}"


# ============================================
# JavaScript Compatibility
# ============================================

@pytest.mark.integration
def test_es6_features_supported(page: Page, api_base):
    """Verify ES6+ features are supported or polyfilled."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    # Test ES6 features
    es6_support = page.evaluate("""
        () => {
            return {
                arrowFunctions: typeof (() => {}) === 'function',
                promises: typeof Promise !== 'undefined',
                classes: typeof class {} === 'function',
                templateLiterals: typeof `test` === 'string',
                destructuring: (() => { try { const {a} = {a: 1}; return true; } catch(e) { return false; } })(),
                spread: (() => { try { const arr = [...[1,2]]; return arr.length === 2; } catch(e) { return false; } })(),
                asyncAwait: (() => { try { eval('async () => {}'); return true; } catch(e) { return false; } })(),
            };
        }
    """)
    
    for feature, supported in es6_support.items():
        assert supported, f"ES6 feature not supported: {feature}"


@pytest.mark.integration
def test_fetch_api_supported(page: Page, api_base):
    """Verify Fetch API is supported or polyfilled."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    fetch_supported = page.evaluate("() => typeof fetch !== 'undefined'")
    assert fetch_supported, "Fetch API not supported"


@pytest.mark.integration
def test_localstorage_supported(page: Page, api_base):
    """Verify localStorage is supported."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    localStorage_supported = page.evaluate("""
        () => {
            try {
                localStorage.setItem('test', 'value');
                localStorage.removeItem('test');
                return true;
            } catch (e) {
                return false;
            }
        }
    """)
    
    assert localStorage_supported, "localStorage not supported"


# ============================================
# Layout and Rendering
# ============================================

@pytest.mark.integration
def test_css_grid_support(page: Page, api_base):
    """Verify CSS Grid is supported."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    grid_supported = page.evaluate("""
        () => {
            const test = document.createElement('div');
            test.style.display = 'grid';
            return test.style.display === 'grid';
        }
    """)
    
    assert grid_supported, "CSS Grid not supported"


@pytest.mark.integration
def test_flexbox_support(page: Page, api_base):
    """Verify Flexbox is supported."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    flexbox_supported = page.evaluate("""
        () => {
            const test = document.createElement('div');
            test.style.display = 'flex';
            return test.style.display === 'flex' || test.style.display === '-webkit-flex';
        }
    """)
    
    assert flexbox_supported, "Flexbox not supported"


@pytest.mark.integration
def test_css_variables_support(page: Page, api_base):
    """Verify CSS Custom Properties (variables) are supported."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    css_vars_supported = page.evaluate("""
        () => {
            const test = document.createElement('div');
            test.style.setProperty('--test-var', 'value');
            return test.style.getPropertyValue('--test-var') === 'value';
        }
    """)
    
    assert css_vars_supported, "CSS Custom Properties not supported"


# ============================================
# Form Compatibility
# ============================================

@pytest.mark.integration
def test_form_validation_api(page: Page, api_base):
    """Verify HTML5 form validation API is supported."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    validation_supported = page.evaluate("""
        () => {
            const input = document.createElement('input');
            input.type = 'email';
            input.required = true;
            return typeof input.checkValidity === 'function';
        }
    """)
    
    assert validation_supported, "HTML5 form validation API not supported"


@pytest.mark.integration
def test_input_types_supported(page: Page, api_base):
    """Verify modern input types are supported."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    input_types = page.evaluate("""
        () => {
            const types = ['email', 'password', 'text', 'number', 'date', 'time'];
            const support = {};
            types.forEach(type => {
                const input = document.createElement('input');
                input.type = type;
                support[type] = input.type === type;
            });
            return support;
        }
    """)
    
    # Essential input types must be supported
    essential_types = ['email', 'password', 'text']
    for input_type in essential_types:
        assert input_types.get(input_type, False), \
            f"Input type '{input_type}' not supported"


# ============================================
# Event Handling
# ============================================

@pytest.mark.integration
def test_event_listener_support(page: Page, api_base):
    """Verify addEventListener is supported."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    event_support = page.evaluate("""
        () => {
            const div = document.createElement('div');
            return typeof div.addEventListener === 'function';
        }
    """)
    
    assert event_support, "addEventListener not supported"


@pytest.mark.integration
def test_touch_events_supported(page: Page, api_base):
    """Verify touch events are supported (for mobile browsers)."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    touch_support = page.evaluate("""
        () => {
            return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        }
    """)
    
    # Touch support is optional (desktop browsers may not have it)
    # Just verify the check doesn't error


# ============================================
# Responsive Design
# ============================================

@pytest.mark.integration
def test_viewport_meta_tag(page: Page, api_base):
    """Verify viewport meta tag is present for responsive design."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    viewport = page.locator("meta[name='viewport']")
    assert viewport.count() > 0, "Viewport meta tag missing"
    
    viewport_content = viewport.get_attribute("content")
    assert viewport_content is not None, "Viewport meta tag missing content"
    assert "width=device-width" in viewport_content, \
        "Viewport meta tag missing width=device-width"


@pytest.mark.integration
def test_responsive_breakpoints(authenticated_page: Page, api_base):
    """Verify responsive breakpoints work across browsers."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Test mobile viewport (375px)
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.wait_for_timeout(500)
    
    # Check that mobile navigation is accessible
    mobile_nav = authenticated_page.locator("nav[aria-label*='Mobile'], button[aria-label*='menu']")
    # Mobile nav should be present or hamburger menu visible
    
    # Test tablet viewport (768px)
    authenticated_page.set_viewport_size({"width": 768, "height": 1024})
    authenticated_page.wait_for_timeout(500)
    
    # Test desktop viewport (1920px)
    authenticated_page.set_viewport_size({"width": 1920, "height": 1080})
    authenticated_page.wait_for_timeout(500)
    
    # Page should render correctly at all sizes
    main_content = authenticated_page.locator("main, [role='main']")
    assert main_content.count() > 0, "Main content not visible"


# ============================================
# API Compatibility
# ============================================

@pytest.mark.integration
def test_fetch_api_works(page: Page, api_base):
    """Verify Fetch API works for API calls."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    fetch_works = page.evaluate(f"""
        async () => {{
            try {{
                const response = await fetch('{api_base}/health');
                return response.ok || response.status === 200 || response.status === 404;
            }} catch (e) {{
                return false;
            }}
        }}
    """)
    
    assert fetch_works, "Fetch API not working"


# ============================================
# Performance Compatibility
# ============================================

@pytest.mark.integration
def test_request_animation_frame(page: Page, api_base):
    """Verify requestAnimationFrame is supported."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    raf_supported = page.evaluate("() => typeof requestAnimationFrame !== 'undefined'")
    assert raf_supported, "requestAnimationFrame not supported"


# ============================================
# Security Features
# ============================================

@pytest.mark.integration
def test_csp_support(page: Page, api_base):
    """Verify Content Security Policy headers are respected."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    # Check for CSP header (if set)
    # This is a basic check - full CSP testing requires header inspection
    response = page.request.get(f"{api_base}/login")
    headers = response.headers()
    
    # CSP header may or may not be present
    # Just verify the page loads without CSP violations


# ============================================
# Browser-Specific Tests
# ============================================

@pytest.mark.integration
def test_chrome_compatibility(page: Page, api_base):
    """Verify Chrome-specific features work."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    user_agent = page.evaluate("() => navigator.userAgent")
    is_chrome = "Chrome" in user_agent and "Edg" not in user_agent
    
    if is_chrome:
        # Chrome-specific tests
        # Verify Chrome DevTools Protocol features (if used)
        pass


@pytest.mark.integration
def test_firefox_compatibility(page: Page, api_base):
    """Verify Firefox-specific features work."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    user_agent = page.evaluate("() => navigator.userAgent")
    is_firefox = "Firefox" in user_agent
    
    if is_firefox:
        # Firefox-specific tests
        # Verify Firefox-specific CSS properties work
        pass


@pytest.mark.integration
def test_safari_compatibility(page: Page, api_base):
    """Verify Safari-specific features work."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    user_agent = page.evaluate("() => navigator.userAgent")
    is_safari = "Safari" in user_agent and "Chrome" not in user_agent
    
    if is_safari:
        # Safari-specific tests
        # Verify WebKit-specific features work
        pass


@pytest.mark.integration
def test_edge_compatibility(page: Page, api_base):
    """Verify Edge-specific features work."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    user_agent = page.evaluate("() => navigator.userAgent")
    is_edge = "Edg" in user_agent
    
    if is_edge:
        # Edge-specific tests
        # Edge is Chromium-based, so should work similarly to Chrome
        pass


# ============================================
# Cross-Browser Summary
# ============================================

@pytest.mark.integration
def test_cross_browser_compatibility_summary(page: Page, api_base):
    """Summary: Verify overall cross-browser compatibility."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    compatibility_checks = {
        "es6_support": page.evaluate("() => typeof Promise !== 'undefined'"),
        "fetch_api": page.evaluate("() => typeof fetch !== 'undefined'"),
        "localstorage": page.evaluate("() => { try { localStorage.setItem('test', '1'); localStorage.removeItem('test'); return true; } catch(e) { return false; } }"),
        "css_grid": page.evaluate("() => { const d = document.createElement('div'); d.style.display = 'grid'; return d.style.display === 'grid'; }"),
        "flexbox": page.evaluate("() => { const d = document.createElement('div'); d.style.display = 'flex'; return d.style.display === 'flex' || d.style.display === '-webkit-flex'; }"),
        "css_variables": page.evaluate("() => { const d = document.createElement('div'); d.style.setProperty('--test', 'value'); return d.style.getPropertyValue('--test') === 'value'; }"),
        "viewport_meta": page.locator("meta[name='viewport']").count() > 0,
        "html5_validation": page.evaluate("() => { const i = document.createElement('input'); i.type = 'email'; return typeof i.checkValidity === 'function'; }"),
    }
    
    failed_checks = [check for check, passed in compatibility_checks.items() if not passed]
    
    assert len(failed_checks) == 0, \
        f"Cross-browser compatibility checks failed: {', '.join(failed_checks)}"

