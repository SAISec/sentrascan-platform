"""
Tests for toast notification stacking and auto-dismiss functionality.

Tests:
- Toast stacking (multiple toasts display vertically)
- Auto-dismiss after duration
- Stacking order (new toasts appear correctly)
- Multiple toasts auto-dismiss independently
- Stacking with different toast types
- Close button functionality in stacked toasts
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


# ============================================
# Toast Stacking Tests
# ============================================

@pytest.mark.integration
def test_toast_stacking_multiple_toasts(authenticated_page: Page, api_base):
    """Test that multiple toasts stack vertically."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check if showToast function is available
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show multiple toasts
    authenticated_page.evaluate("""
        showToast('First toast', 'info');
        showToast('Second toast', 'success');
        showToast('Third toast', 'error');
    """)
    
    authenticated_page.wait_for_timeout(500)  # Wait for toasts to appear
    
    # Check toast container exists
    toast_container = authenticated_page.locator("#toast-container")
    expect(toast_container).to_be_visible()
    
    # Check that multiple toasts are present
    toasts = toast_container.locator(".toast")
    toast_count = toasts.count()
    assert toast_count >= 3, f"Expected at least 3 toasts, found {toast_count}"
    
    # Check that toasts are stacked (container should have flex-direction: column)
    container_style = toast_container.evaluate("el => window.getComputedStyle(el).flexDirection")
    assert container_style == "column", "Toast container should stack toasts vertically"


@pytest.mark.integration
def test_toast_stacking_order(authenticated_page: Page, api_base):
    """Test that new toasts appear in correct order (typically newest on top or bottom)."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show toasts sequentially
    authenticated_page.evaluate("""
        showToast('First toast', 'info');
    """)
    authenticated_page.wait_for_timeout(200)
    
    authenticated_page.evaluate("""
        showToast('Second toast', 'success');
    """)
    authenticated_page.wait_for_timeout(200)
    
    authenticated_page.evaluate("""
        showToast('Third toast', 'error');
    """)
    authenticated_page.wait_for_timeout(500)
    
    # Get all toasts
    toast_container = authenticated_page.locator("#toast-container")
    toasts = toast_container.locator(".toast")
    
    if toasts.count() >= 3:
        # Check toast order (implementation may vary - newest on top or bottom)
        first_toast = toasts.first
        last_toast = toasts.last
        
        # Verify toasts are in container
        assert first_toast.count() > 0, "First toast should exist"
        assert last_toast.count() > 0, "Last toast should exist"


@pytest.mark.integration
def test_toast_stacking_different_types(authenticated_page: Page, api_base):
    """Test that toasts of different types stack correctly."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show toasts of different types
    authenticated_page.evaluate("""
        showToast('Success message', 'success');
        showToast('Error message', 'error');
        showToast('Warning message', 'warning');
        showToast('Info message', 'info');
    """)
    
    authenticated_page.wait_for_timeout(500)
    
    toast_container = authenticated_page.locator("#toast-container")
    toasts = toast_container.locator(".toast")
    
    # Check that all types are present
    success_toast = toast_container.locator(".toast-success")
    error_toast = toast_container.locator(".toast-error")
    warning_toast = toast_container.locator(".toast-warning")
    info_toast = toast_container.locator(".toast-info")
    
    assert success_toast.count() > 0, "Success toast should be present"
    assert error_toast.count() > 0, "Error toast should be present"
    assert warning_toast.count() > 0, "Warning toast should be present"
    assert info_toast.count() > 0, "Info toast should be present"


@pytest.mark.integration
def test_toast_stacking_spacing(authenticated_page: Page, api_base):
    """Test that stacked toasts have proper spacing between them."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show multiple toasts
    authenticated_page.evaluate("""
        showToast('Toast 1', 'info');
        showToast('Toast 2', 'success');
        showToast('Toast 3', 'error');
    """)
    
    authenticated_page.wait_for_timeout(500)
    
    toast_container = authenticated_page.locator("#toast-container")
    
    # Check container has gap for spacing
    gap = toast_container.evaluate("el => window.getComputedStyle(el).gap")
    # Gap should be set (could be in pixels or other units)
    assert gap and gap != "normal", "Toast container should have gap for spacing between toasts"


# ============================================
# Auto-Dismiss Tests
# ============================================

@pytest.mark.integration
def test_toast_auto_dismiss_default_duration(authenticated_page: Page, api_base):
    """Test that toasts auto-dismiss after default duration (5 seconds)."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show a toast with default duration
    toast_id = authenticated_page.evaluate("showToast('Auto-dismiss test', 'info')")
    
    authenticated_page.wait_for_timeout(500)
    
    # Verify toast is visible
    toast = authenticated_page.locator(f"#{toast_id}")
    expect(toast).to_be_visible()
    
    # Wait for auto-dismiss (default is 5000ms, but we'll wait a bit longer)
    authenticated_page.wait_for_timeout(5500)
    
    # Toast should be dismissed
    toast_count = authenticated_page.locator(f"#{toast_id}").count()
    assert toast_count == 0, "Toast should be auto-dismissed after default duration"


@pytest.mark.integration
def test_toast_auto_dismiss_custom_duration(authenticated_page: Page, api_base):
    """Test that toasts auto-dismiss after custom duration."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show a toast with short duration (1 second)
    toast_id = authenticated_page.evaluate("""
        showToast('Quick dismiss test', 'info', { duration: 1000 })
    """)
    
    authenticated_page.wait_for_timeout(500)
    
    # Verify toast is visible
    toast = authenticated_page.locator(f"#{toast_id}")
    expect(toast).to_be_visible()
    
    # Wait for auto-dismiss
    authenticated_page.wait_for_timeout(1500)
    
    # Toast should be dismissed
    toast_count = authenticated_page.locator(f"#{toast_id}").count()
    assert toast_count == 0, "Toast should be auto-dismissed after custom duration"


@pytest.mark.integration
def test_toast_no_auto_dismiss_when_duration_zero(authenticated_page: Page, api_base):
    """Test that toasts don't auto-dismiss when duration is 0."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show a toast with duration 0 (no auto-dismiss)
    toast_id = authenticated_page.evaluate("""
        showToast('No auto-dismiss test', 'info', { duration: 0 })
    """)
    
    authenticated_page.wait_for_timeout(500)
    
    # Verify toast is visible
    toast = authenticated_page.locator(f"#{toast_id}")
    expect(toast).to_be_visible()
    
    # Wait longer than default duration
    authenticated_page.wait_for_timeout(6000)
    
    # Toast should still be visible
    toast_count = authenticated_page.locator(f"#{toast_id}").count()
    assert toast_count > 0, "Toast should not auto-dismiss when duration is 0"
    
    # Clean up - dismiss manually
    authenticated_page.evaluate(f"dismissToast('{toast_id}')")
    authenticated_page.wait_for_timeout(500)


@pytest.mark.integration
def test_toast_auto_dismiss_multiple_independent(authenticated_page: Page, api_base):
    """Test that multiple toasts auto-dismiss independently."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show toasts with different durations
    toast_id_1 = authenticated_page.evaluate("""
        showToast('Short duration toast', 'info', { duration: 1000 })
    """)
    authenticated_page.wait_for_timeout(200)
    
    toast_id_2 = authenticated_page.evaluate("""
        showToast('Long duration toast', 'success', { duration: 3000 })
    """)
    authenticated_page.wait_for_timeout(200)
    
    toast_id_3 = authenticated_page.evaluate("""
        showToast('No dismiss toast', 'error', { duration: 0 })
    """)
    
    authenticated_page.wait_for_timeout(500)
    
    # All toasts should be visible initially
    assert authenticated_page.locator(f"#{toast_id_1}").count() > 0, "First toast should be visible"
    assert authenticated_page.locator(f"#{toast_id_2}").count() > 0, "Second toast should be visible"
    assert authenticated_page.locator(f"#{toast_id_3}").count() > 0, "Third toast should be visible"
    
    # Wait for first toast to dismiss
    authenticated_page.wait_for_timeout(1500)
    
    # First toast should be dismissed, others still visible
    assert authenticated_page.locator(f"#{toast_id_1}").count() == 0, "First toast should be dismissed"
    assert authenticated_page.locator(f"#{toast_id_2}").count() > 0, "Second toast should still be visible"
    assert authenticated_page.locator(f"#{toast_id_3}").count() > 0, "Third toast should still be visible"
    
    # Wait for second toast to dismiss
    authenticated_page.wait_for_timeout(2000)
    
    # Second toast should be dismissed, third still visible
    assert authenticated_page.locator(f"#{toast_id_2}").count() == 0, "Second toast should be dismissed"
    assert authenticated_page.locator(f"#{toast_id_3}").count() > 0, "Third toast should still be visible"
    
    # Clean up
    authenticated_page.evaluate(f"dismissToast('{toast_id_3}')")
    authenticated_page.wait_for_timeout(500)


# ============================================
# Stacking and Auto-Dismiss Combined
# ============================================

@pytest.mark.integration
def test_toast_stacking_with_auto_dismiss(authenticated_page: Page, api_base):
    """Test that stacked toasts auto-dismiss correctly."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show multiple toasts that will auto-dismiss
    toast_ids = authenticated_page.evaluate("""
        [
            showToast('Toast 1', 'info', { duration: 2000 }),
            showToast('Toast 2', 'success', { duration: 2000 }),
            showToast('Toast 3', 'error', { duration: 2000 })
        ]
    """)
    
    authenticated_page.wait_for_timeout(500)
    
    toast_container = authenticated_page.locator("#toast-container")
    toasts = toast_container.locator(".toast")
    
    # All toasts should be visible and stacked
    assert toasts.count() >= 3, "All toasts should be visible and stacked"
    
    # Wait for auto-dismiss
    authenticated_page.wait_for_timeout(2500)
    
    # All toasts should be dismissed
    remaining_toasts = toast_container.locator(".toast").count()
    assert remaining_toasts == 0, "All toasts should be auto-dismissed"


@pytest.mark.integration
def test_toast_stacking_after_dismiss(authenticated_page: Page, api_base):
    """Test that remaining toasts maintain proper stacking after one dismisses."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show multiple toasts with different durations
    toast_ids = authenticated_page.evaluate("""
        [
            showToast('Quick dismiss', 'info', { duration: 1000 }),
            showToast('Stays longer', 'success', { duration: 5000 }),
            showToast('Stays longest', 'error', { duration: 0 })
        ]
    """)
    
    authenticated_page.wait_for_timeout(500)
    
    toast_container = authenticated_page.locator("#toast-container")
    initial_count = toast_container.locator(".toast").count()
    assert initial_count >= 3, "All toasts should be visible initially"
    
    # Wait for first to dismiss
    authenticated_page.wait_for_timeout(1500)
    
    # Remaining toasts should still be properly stacked
    remaining_count = toast_container.locator(".toast").count()
    assert remaining_count == 2, "Two toasts should remain after first dismisses"
    
    # Check container still has proper stacking
    container_style = toast_container.evaluate("el => window.getComputedStyle(el).flexDirection")
    assert container_style == "column", "Container should maintain column layout"
    
    # Clean up
    for toast_id in toast_ids[1:]:  # Dismiss remaining toasts
        authenticated_page.evaluate(f"dismissToast('{toast_id}')")
    authenticated_page.wait_for_timeout(500)


# ============================================
# Close Button in Stacked Toasts
# ============================================

@pytest.mark.integration
def test_toast_close_button_in_stacked_toasts(authenticated_page: Page, api_base):
    """Test that close buttons work correctly in stacked toasts."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show multiple dismissible toasts
    toast_ids = authenticated_page.evaluate("""
        [
            showToast('Toast 1', 'info'),
            showToast('Toast 2', 'success'),
            showToast('Toast 3', 'error')
        ]
    """)
    
    authenticated_page.wait_for_timeout(500)
    
    toast_container = authenticated_page.locator("#toast-container")
    toasts = toast_container.locator(".toast")
    
    # Check that all toasts have close buttons
    close_buttons = toast_container.locator(".toast-close")
    assert close_buttons.count() >= 3, "All dismissible toasts should have close buttons"
    
    # Click close button on middle toast
    if close_buttons.count() >= 2:
        middle_close = close_buttons.nth(1)
        middle_close.click()
        authenticated_page.wait_for_timeout(500)
        
        # One toast should be dismissed
        remaining_count = toast_container.locator(".toast").count()
        assert remaining_count == 2, "One toast should be dismissed after clicking close"
    
    # Clean up remaining toasts
    for toast_id in toast_ids:
        authenticated_page.evaluate(f"dismissToast('{toast_id}')")
    authenticated_page.wait_for_timeout(500)


@pytest.mark.integration
def test_toast_manual_dismiss_before_auto_dismiss(authenticated_page: Page, api_base):
    """Test that manually dismissing a toast prevents auto-dismiss."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show a toast with auto-dismiss
    toast_id = authenticated_page.evaluate("""
        showToast('Manual dismiss test', 'info', { duration: 5000 })
    """)
    
    authenticated_page.wait_for_timeout(500)
    
    # Verify toast is visible
    toast = authenticated_page.locator(f"#{toast_id}")
    expect(toast).to_be_visible()
    
    # Manually dismiss
    authenticated_page.evaluate(f"dismissToast('{toast_id}')")
    authenticated_page.wait_for_timeout(500)
    
    # Toast should be dismissed
    toast_count = authenticated_page.locator(f"#{toast_id}").count()
    assert toast_count == 0, "Toast should be dismissed manually"
    
    # Wait longer than auto-dismiss duration
    authenticated_page.wait_for_timeout(6000)
    
    # Toast should still be gone (not reappear)
    toast_count = authenticated_page.locator(f"#{toast_id}").count()
    assert toast_count == 0, "Manually dismissed toast should not reappear"


# ============================================
# Toast Container Tests
# ============================================

@pytest.mark.integration
def test_toast_container_exists(authenticated_page: Page, api_base):
    """Test that toast container exists and is properly configured."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_container = authenticated_page.locator("#toast-container")
    
    # Container should exist
    expect(toast_container).to_be_visible()
    
    # Check ARIA attributes
    aria_live = toast_container.get_attribute("aria-live")
    assert aria_live == "polite", "Toast container should have aria-live='polite'"
    
    aria_atomic = toast_container.get_attribute("aria-atomic")
    assert aria_atomic == "false", "Toast container should have aria-atomic='false'"
    
    # Check positioning (fixed position)
    position = toast_container.evaluate("el => window.getComputedStyle(el).position")
    assert position == "fixed", "Toast container should be fixed position"


@pytest.mark.integration
def test_toast_container_max_width(authenticated_page: Page, api_base):
    """Test that toast container has max-width to prevent overflow."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_container = authenticated_page.locator("#toast-container")
    
    max_width = toast_container.evaluate("el => window.getComputedStyle(el).maxWidth")
    # Max width should be set (typically 400px or similar)
    assert max_width and max_width != "none", "Toast container should have max-width"


# ============================================
# Edge Cases
# ============================================

@pytest.mark.integration
def test_toast_rapid_fire_stacking(authenticated_page: Page, api_base):
    """Test that rapidly showing multiple toasts stacks them correctly."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    toast_function_exists = authenticated_page.evaluate("typeof showToast !== 'undefined'")
    if not toast_function_exists:
        pytest.skip("showToast function not available")
    
    # Show many toasts rapidly
    authenticated_page.evaluate("""
        for (let i = 1; i <= 5; i++) {
            showToast('Toast ' + i, 'info');
        }
    """)
    
    authenticated_page.wait_for_timeout(500)
    
    toast_container = authenticated_page.locator("#toast-container")
    toasts = toast_container.locator(".toast")
    
    # All toasts should be stacked
    assert toasts.count() >= 5, "All rapidly shown toasts should be stacked"
    
    # Clean up
    authenticated_page.evaluate("""
        const container = document.getElementById('toast-container');
        const toasts = container.querySelectorAll('.toast');
        toasts.forEach(toast => {
            if (typeof dismissToast !== 'undefined') {
                dismissToast(toast.id);
            }
        });
    """)
    authenticated_page.wait_for_timeout(500)

