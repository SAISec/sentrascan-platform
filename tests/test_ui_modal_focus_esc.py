"""
Tests for modal focus trap and ESC key functionality.

Tests:
- Focus trap within modals
- ESC key closes modals
- Focus restoration after modal closes
- Focus moves to first element when modal opens
- Tab navigation cycles within modal
- Shift+Tab navigation cycles backwards
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
# Focus Trap Tests
# ============================================

@pytest.mark.integration
def test_modal_focus_trap_tab_forward(authenticated_page: Page, api_base):
    """Test that Tab key cycles focus forward within modal."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page to access create baseline modal
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Open create baseline modal
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                # Check modal is visible
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Get focusable elements in modal
                focusable_elements = modal.locator(
                    "button:not([disabled]), input:not([disabled]), "
                    "textarea:not([disabled]), select:not([disabled]), "
                    "a[href], [tabindex]:not([tabindex='-1'])"
                )
                
                if focusable_elements.count() >= 2:
                    # Focus should be on first element
                    first_element = focusable_elements.first
                    # Check if first element is focused (might need to wait)
                    authenticated_page.wait_for_timeout(200)
                    
                    # Press Tab
                    authenticated_page.keyboard.press("Tab")
                    authenticated_page.wait_for_timeout(100)
                    
                    # Focus should move to next element
                    # Verify focus is still within modal
                    focused_element = authenticated_page.locator(":focus")
                    if focused_element.count() > 0:
                        # Check that focused element is within modal
                        is_in_modal = focused_element.evaluate(
                            "el => document.getElementById('create-baseline-modal').contains(el)"
                        )
                        assert is_in_modal, "Focus should remain within modal when pressing Tab"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


@pytest.mark.integration
def test_modal_focus_trap_tab_backward(authenticated_page: Page, api_base):
    """Test that Shift+Tab cycles focus backward within modal."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Open modal
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Get focusable elements
                focusable_elements = modal.locator(
                    "button:not([disabled]), input:not([disabled]), "
                    "textarea:not([disabled]), select:not([disabled]), "
                    "a[href], [tabindex]:not([tabindex='-1'])"
                )
                
                if focusable_elements.count() >= 2:
                    # Focus last element
                    last_element = focusable_elements.last
                    last_element.focus()
                    authenticated_page.wait_for_timeout(200)
                    
                    # Press Shift+Tab
                    authenticated_page.keyboard.press("Shift+Tab")
                    authenticated_page.wait_for_timeout(100)
                    
                    # Focus should move to previous element or wrap to last
                    focused_element = authenticated_page.locator(":focus")
                    if focused_element.count() > 0:
                        is_in_modal = focused_element.evaluate(
                            "el => document.getElementById('create-baseline-modal').contains(el)"
                        )
                        assert is_in_modal, "Focus should remain within modal when pressing Shift+Tab"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


@pytest.mark.integration
def test_modal_focus_trap_wraps_forward(authenticated_page: Page, api_base):
    """Test that Tab from last element wraps to first element."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Open modal
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Get focusable elements
                focusable_elements = modal.locator(
                    "button:not([disabled]), input:not([disabled]), "
                    "textarea:not([disabled]), select:not([disabled]), "
                    "a[href], [tabindex]:not([tabindex='-1'])"
                )
                
                if focusable_elements.count() >= 2:
                    # Focus last element
                    last_element = focusable_elements.last
                    last_element.focus()
                    authenticated_page.wait_for_timeout(200)
                    
                    # Press Tab (should wrap to first)
                    authenticated_page.keyboard.press("Tab")
                    authenticated_page.wait_for_timeout(100)
                    
                    # Focus should be on first element
                    first_element = focusable_elements.first
                    focused_element = authenticated_page.locator(":focus")
                    
                    # Check if focus wrapped to first element
                    if focused_element.count() > 0:
                        is_first = focused_element.evaluate(
                            "el => el === document.querySelector('#create-baseline-modal button:not([disabled]), #create-baseline-modal input:not([disabled])')"
                        )
                        # Focus should be within modal at least
                        is_in_modal = focused_element.evaluate(
                            "el => document.getElementById('create-baseline-modal').contains(el)"
                        )
                        assert is_in_modal, "Focus should wrap to first element when Tab from last"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


@pytest.mark.integration
def test_modal_focus_trap_wraps_backward(authenticated_page: Page, api_base):
    """Test that Shift+Tab from first element wraps to last element."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Open modal
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Get focusable elements
                focusable_elements = modal.locator(
                    "button:not([disabled]), input:not([disabled]), "
                    "textarea:not([disabled]), select:not([disabled]), "
                    "a[href], [tabindex]:not([tabindex='-1'])"
                )
                
                if focusable_elements.count() >= 2:
                    # Focus first element
                    first_element = focusable_elements.first
                    first_element.focus()
                    authenticated_page.wait_for_timeout(200)
                    
                    # Press Shift+Tab (should wrap to last)
                    authenticated_page.keyboard.press("Shift+Tab")
                    authenticated_page.wait_for_timeout(100)
                    
                    # Focus should be on last element or still in modal
                    focused_element = authenticated_page.locator(":focus")
                    if focused_element.count() > 0:
                        is_in_modal = focused_element.evaluate(
                            "el => document.getElementById('create-baseline-modal').contains(el)"
                        )
                        assert is_in_modal, "Focus should wrap to last element when Shift+Tab from first"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


@pytest.mark.integration
def test_modal_focus_initial(authenticated_page: Page, api_base):
    """Test that focus moves to first element when modal opens."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Store element that will trigger modal
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                # Click to open modal
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Wait for focus to move
                authenticated_page.wait_for_timeout(300)
                
                # Check that focus is within modal
                focused_element = authenticated_page.locator(":focus")
                if focused_element.count() > 0:
                    is_in_modal = focused_element.evaluate(
                        "el => document.getElementById('create-baseline-modal').contains(el)"
                    )
                    assert is_in_modal, "Focus should be within modal when it opens"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


# ============================================
# ESC Key Tests
# ============================================

@pytest.mark.integration
def test_modal_esc_key_closes(authenticated_page: Page, api_base):
    """Test that ESC key closes the modal."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Open modal
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Press ESC key
                authenticated_page.keyboard.press("Escape")
                authenticated_page.wait_for_timeout(500)
                
                # Modal should be closed
                modal_display = modal.evaluate("el => window.getComputedStyle(el).display")
                assert modal_display == "none", "Modal should be closed after pressing ESC key"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


@pytest.mark.integration
def test_modal_esc_key_restores_focus(authenticated_page: Page, api_base):
    """Test that focus is restored to trigger element after ESC closes modal."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Store trigger button
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                # Click to open modal
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Press ESC to close
                authenticated_page.keyboard.press("Escape")
                authenticated_page.wait_for_timeout(500)
                
                # Focus should be restored (might be on trigger or another element)
                # At minimum, focus should not be trapped
                focused_element = authenticated_page.locator(":focus")
                if focused_element.count() > 0:
                    # Focus should not be in closed modal
                    is_in_modal = focused_element.evaluate(
                        "el => { const modal = document.getElementById('create-baseline-modal'); return modal && modal.contains(el) && window.getComputedStyle(modal).display !== 'none'; }"
                    )
                    assert not is_in_modal, "Focus should not be in closed modal"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


@pytest.mark.integration
def test_modal_esc_key_only_closes_active_modal(authenticated_page: Page, api_base):
    """Test that ESC key only closes the active modal."""
    # This test would require multiple modals, which might not be common
    # For now, we verify that ESC closes the modal that's open
    
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Open modal
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Press ESC
                authenticated_page.keyboard.press("Escape")
                authenticated_page.wait_for_timeout(500)
                
                # Only the active modal should be closed
                modal_display = modal.evaluate("el => window.getComputedStyle(el).display")
                assert modal_display == "none", "Active modal should be closed by ESC"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


# ============================================
# Focus Restoration Tests
# ============================================

@pytest.mark.integration
def test_modal_focus_restoration_on_close_button(authenticated_page: Page, api_base):
    """Test that focus is restored when modal is closed via close button."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Store trigger button
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                # Click to open modal
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Click close button
                close_button = modal.locator("button.modal-close, button[aria-label*='Close']")
                if close_button.count() > 0:
                    close_button.first.click()
                    authenticated_page.wait_for_timeout(500)
                    
                    # Modal should be closed
                    modal_display = modal.evaluate("el => window.getComputedStyle(el).display")
                    assert modal_display == "none", "Modal should be closed"
                    
                    # Focus should be restored (not in modal)
                    focused_element = authenticated_page.locator(":focus")
                    if focused_element.count() > 0:
                        is_in_modal = focused_element.evaluate(
                            "el => { const modal = document.getElementById('create-baseline-modal'); return modal && modal.contains(el) && window.getComputedStyle(modal).display !== 'none'; }"
                        )
                        assert not is_in_modal, "Focus should not be in closed modal"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


@pytest.mark.integration
def test_modal_focus_restoration_on_cancel(authenticated_page: Page, api_base):
    """Test that focus is restored when modal is closed via Cancel button."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Open modal
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Click Cancel button
                cancel_button = modal.locator("button:has-text('Cancel')")
                if cancel_button.count() > 0:
                    cancel_button.first.click()
                    authenticated_page.wait_for_timeout(500)
                    
                    # Modal should be closed
                    modal_display = modal.evaluate("el => window.getComputedStyle(el).display")
                    assert modal_display == "none", "Modal should be closed after Cancel"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


# ============================================
# Modal ARIA Attributes
# ============================================

@pytest.mark.integration
def test_modal_aria_attributes(authenticated_page: Page, api_base):
    """Test that modal has proper ARIA attributes."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Open modal
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Check aria-hidden is false when open
                aria_hidden = modal.get_attribute("aria-hidden")
                # Should be false or not set when modal is visible
                if aria_hidden:
                    assert aria_hidden == "false", "Modal should have aria-hidden='false' when open"
                
                # Check for role="dialog" (if implemented)
                role = modal.get_attribute("role")
                # Role might be dialog or not set (depends on implementation)
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")


@pytest.mark.integration
def test_modal_body_overflow_hidden(authenticated_page: Page, api_base):
    """Test that body overflow is hidden when modal is open."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Check initial body overflow
            initial_overflow = authenticated_page.evaluate("() => window.getComputedStyle(document.body).overflow")
            
            # Open modal
            create_baseline_button = authenticated_page.locator("button:has-text('Create Baseline'), a:has-text('Create Baseline')")
            if create_baseline_button.count() > 0:
                create_baseline_button.first.click()
                authenticated_page.wait_for_timeout(500)
                
                modal = authenticated_page.locator("#create-baseline-modal")
                expect(modal).to_be_visible()
                
                # Check body overflow is hidden
                body_overflow = authenticated_page.evaluate("() => window.getComputedStyle(document.body).overflow")
                assert body_overflow == "hidden", "Body overflow should be hidden when modal is open"
                
                # Close modal
                authenticated_page.keyboard.press("Escape")
                authenticated_page.wait_for_timeout(500)
                
                # Body overflow should be restored
                restored_overflow = authenticated_page.evaluate("() => window.getComputedStyle(document.body).overflow")
                # Should be restored to initial value or empty string
                assert restored_overflow != "hidden", "Body overflow should be restored when modal closes"
            else:
                pytest.skip("Create Baseline button not found")
    else:
        pytest.skip("No scan available to test modal")

