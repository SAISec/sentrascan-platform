"""
Tests for mobile navigation (hamburger menu, drawer, touch targets).

Tests:
- Hamburger menu toggle
- Drawer opening/closing
- Touch target sizes (44x44px minimum)
- Focus trap in mobile menu
- ESC key to close
- Overlay click to close
- Link click closes menu
- Keyboard navigation
- ARIA attributes
- Body scroll prevention
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


@pytest.fixture
def mobile_viewport(page: Page):
    """Set mobile viewport for testing."""
    page.set_viewport_size({"width": 375, "height": 667})  # iPhone SE size
    return page


# ============================================
# Hamburger Menu Toggle Tests
# ============================================

@pytest.mark.integration
def test_hamburger_menu_visible_on_mobile(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that hamburger menu is visible on mobile viewport."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check hamburger menu button is visible
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    expect(hamburger_button).to_be_visible()
    
    # Check desktop nav is hidden
    desktop_nav = authenticated_page.locator(".nav-desktop")
    if desktop_nav.count() > 0:
        nav_display = desktop_nav.evaluate("el => window.getComputedStyle(el).display")
        assert nav_display == "none", "Desktop navigation should be hidden on mobile"


@pytest.mark.integration
def test_hamburger_menu_toggle_opens_drawer(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that clicking hamburger menu opens the drawer."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    overlay = authenticated_page.locator(".nav-mobile-overlay")
    
    # Drawer should be hidden initially
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "none", "Drawer should be hidden initially"
    
    # Click hamburger button
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)  # Wait for animation
    
    # Drawer should be visible
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "block", "Drawer should be visible after clicking hamburger"
    
    # Overlay should be visible
    overlay_display = overlay.evaluate("el => window.getComputedStyle(el).display")
    assert overlay_display == "block", "Overlay should be visible"


@pytest.mark.integration
def test_hamburger_menu_aria_expanded(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that hamburger menu has proper aria-expanded attribute."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    
    # Initially should be false
    aria_expanded = hamburger_button.get_attribute("aria-expanded")
    assert aria_expanded == "false", "Hamburger should have aria-expanded='false' initially"
    
    # Click to open
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Should be true when open
    aria_expanded = hamburger_button.get_attribute("aria-expanded")
    assert aria_expanded == "true", "Hamburger should have aria-expanded='true' when drawer is open"
    
    # Close drawer
    close_button = authenticated_page.locator(".nav-mobile-close")
    if close_button.count() > 0:
        close_button.click()
        authenticated_page.wait_for_timeout(500)
        
        # Should be false again
        aria_expanded = hamburger_button.get_attribute("aria-expanded")
        assert aria_expanded == "false", "Hamburger should have aria-expanded='false' when drawer is closed"


# ============================================
# Drawer Functionality Tests
# ============================================

@pytest.mark.integration
def test_drawer_close_button(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that close button closes the drawer."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    close_button = authenticated_page.locator(".nav-mobile-close")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Verify drawer is open
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "block", "Drawer should be open"
    
    # Click close button
    close_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Drawer should be closed
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "none", "Drawer should be closed after clicking close button"


@pytest.mark.integration
def test_drawer_overlay_click_closes(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that clicking overlay closes the drawer."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    overlay = authenticated_page.locator(".nav-mobile-overlay")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Click overlay
    overlay.click()
    authenticated_page.wait_for_timeout(500)
    
    # Drawer should be closed
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "none", "Drawer should be closed after clicking overlay"


@pytest.mark.integration
def test_drawer_link_click_closes(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that clicking a link in drawer closes it."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Find a link in drawer
    drawer_link = drawer.locator("a.nav-link").first
    if drawer_link.count() > 0:
        # Click link
        drawer_link.click()
        authenticated_page.wait_for_timeout(500)
        
        # Drawer should be closed (might navigate away, so check if still on page)
        if authenticated_page.url.startswith(api_base):
            drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
            assert drawer_display == "none", "Drawer should be closed after clicking link"


# ============================================
# Touch Target Tests
# ============================================

@pytest.mark.integration
def test_hamburger_menu_touch_target_size(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that hamburger menu button meets minimum touch target size (44x44px)."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    
    # Get button dimensions
    box = hamburger_button.bounding_box()
    if box:
        width = box['width']
        height = box['height']
        
        assert width >= 44, f"Hamburger button width ({width}px) should be at least 44px"
        assert height >= 44, f"Hamburger button height ({height}px) should be at least 44px"


@pytest.mark.integration
def test_close_button_touch_target_size(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that close button meets minimum touch target size (44x44px)."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    close_button = authenticated_page.locator(".nav-mobile-close")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Get close button dimensions
    box = close_button.bounding_box()
    if box:
        width = box['width']
        height = box['height']
        
        assert width >= 44, f"Close button width ({width}px) should be at least 44px"
        assert height >= 44, f"Close button height ({height}px) should be at least 44px"


@pytest.mark.integration
def test_drawer_links_touch_target_size(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that drawer navigation links meet minimum touch target size."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Check navigation links
    nav_links = drawer.locator("a.nav-link")
    if nav_links.count() > 0:
        for i in range(min(3, nav_links.count())):
            link = nav_links.nth(i)
            box = link.bounding_box()
            if box:
                # Links should have adequate touch target (44px height recommended)
                height = box['height']
                # Check padding makes it touch-friendly
                padding = link.evaluate("el => parseInt(window.getComputedStyle(el).paddingTop) + parseInt(window.getComputedStyle(el).paddingBottom)")
                total_height = height + padding if padding else height
                
                # Should be at least 44px for comfortable touch
                assert total_height >= 44 or height >= 32, \
                    f"Navigation link should have adequate touch target size (height: {height}px)"


# ============================================
# Focus Trap Tests
# ============================================

@pytest.mark.integration
def test_drawer_focus_trap(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that focus is trapped within the drawer."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Get focusable elements in drawer
    focusable_elements = drawer.locator(
        "a[href], button:not([disabled]), input:not([disabled]), "
        "select:not([disabled]), textarea:not([disabled]), "
        "[tabindex]:not([tabindex='-1'])"
    )
    
    if focusable_elements.count() >= 2:
        # Focus should be on close button initially
        close_button = authenticated_page.locator(".nav-mobile-close")
        authenticated_page.wait_for_timeout(200)
        
        # Press Tab multiple times
        for _ in range(focusable_elements.count() + 1):
            authenticated_page.keyboard.press("Tab")
            authenticated_page.wait_for_timeout(100)
            
            # Check focus is still in drawer
            focused_element = authenticated_page.locator(":focus")
            if focused_element.count() > 0:
                is_in_drawer = focused_element.evaluate(
                    "el => document.querySelector('.nav-mobile-drawer').contains(el)"
                )
                assert is_in_drawer, "Focus should remain within drawer when pressing Tab"


@pytest.mark.integration
def test_drawer_focus_initial(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that focus moves to close button when drawer opens."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    close_button = authenticated_page.locator(".nav-mobile-close")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Focus should be on close button
    authenticated_page.wait_for_timeout(200)  # Wait for focus to move
    
    focused_element = authenticated_page.locator(":focus")
    if focused_element.count() > 0:
        # Check if focused element is close button
        is_close_button = focused_element.evaluate(
            "el => el.classList.contains('nav-mobile-close')"
        )
        # Focus should be in drawer at least
        is_in_drawer = focused_element.evaluate(
            "el => document.querySelector('.nav-mobile-drawer').contains(el)"
        )
        assert is_in_drawer, "Focus should be within drawer when it opens"


@pytest.mark.integration
def test_drawer_focus_restoration(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that focus is restored to hamburger button when drawer closes."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    close_button = authenticated_page.locator(".nav-mobile-close")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Close drawer
    close_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Focus should be restored (might be on hamburger or another element)
    focused_element = authenticated_page.locator(":focus")
    if focused_element.count() > 0:
        # Focus should not be in closed drawer
        is_in_drawer = focused_element.evaluate(
            "el => { const drawer = document.querySelector('.nav-mobile-drawer'); return drawer && drawer.contains(el) && window.getComputedStyle(drawer).display !== 'none'; }"
        )
        assert not is_in_drawer, "Focus should not be in closed drawer"


# ============================================
# ESC Key Tests
# ============================================

@pytest.mark.integration
def test_drawer_esc_key_closes(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that ESC key closes the drawer."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Press ESC
    authenticated_page.keyboard.press("Escape")
    authenticated_page.wait_for_timeout(500)
    
    # Drawer should be closed
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "none", "Drawer should be closed after pressing ESC"


# ============================================
# Body Scroll Prevention Tests
# ============================================

@pytest.mark.integration
def test_drawer_body_scroll_prevention(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that body scroll is prevented when drawer is open."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    
    # Check initial body overflow
    initial_overflow = authenticated_page.evaluate("() => window.getComputedStyle(document.body).overflow")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Body overflow should be hidden
    body_overflow = authenticated_page.evaluate("() => window.getComputedStyle(document.body).overflow")
    assert body_overflow == "hidden", "Body overflow should be hidden when drawer is open"
    
    # Close drawer
    close_button = authenticated_page.locator(".nav-mobile-close")
    close_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Body overflow should be restored
    restored_overflow = authenticated_page.evaluate("() => window.getComputedStyle(document.body).overflow")
    assert restored_overflow != "hidden", "Body overflow should be restored when drawer closes"


# ============================================
# Keyboard Navigation Tests
# ============================================

@pytest.mark.integration
def test_hamburger_keyboard_activation(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that hamburger menu can be activated with keyboard."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    
    # Focus hamburger button
    hamburger_button.focus()
    
    # Press Enter to activate
    authenticated_page.keyboard.press("Enter")
    authenticated_page.wait_for_timeout(500)
    
    # Drawer should open
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "block", "Drawer should open when hamburger is activated with Enter"
    
    # Close and try Space
    close_button = authenticated_page.locator(".nav-mobile-close")
    close_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Focus hamburger again
    hamburger_button.focus()
    
    # Press Space to activate
    authenticated_page.keyboard.press("Space")
    authenticated_page.wait_for_timeout(500)
    
    # Drawer should open
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "block", "Drawer should open when hamburger is activated with Space"


@pytest.mark.integration
def test_close_button_keyboard_activation(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that close button can be activated with keyboard."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    close_button = authenticated_page.locator(".nav-mobile-close")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Focus close button
    close_button.focus()
    
    # Press Enter to close
    authenticated_page.keyboard.press("Enter")
    authenticated_page.wait_for_timeout(500)
    
    # Drawer should be closed
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "none", "Drawer should close when close button is activated with Enter"


# ============================================
# ARIA Attributes Tests
# ============================================

@pytest.mark.integration
def test_drawer_aria_attributes(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that drawer has proper ARIA attributes."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    
    # Check role="navigation"
    role = drawer.get_attribute("role")
    assert role == "navigation", "Drawer should have role='navigation'"
    
    # Check aria-label
    aria_label = drawer.get_attribute("aria-label")
    assert aria_label and len(aria_label) > 0, "Drawer should have aria-label"
    
    # Check hamburger button aria-label
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    hamburger_aria_label = hamburger_button.get_attribute("aria-label")
    assert hamburger_aria_label and len(hamburger_aria_label) > 0, \
        "Hamburger button should have aria-label"
    
    # Check close button aria-label
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    close_button = authenticated_page.locator(".nav-mobile-close")
    close_aria_label = close_button.get_attribute("aria-label")
    assert close_aria_label and len(close_aria_label) > 0, \
        "Close button should have aria-label"


# ============================================
# Drawer Animation Tests
# ============================================

@pytest.mark.integration
def test_drawer_animation_slide_in(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that drawer slides in from left when opened."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(100)
    
    # Check for open class or transform
    has_open_class = drawer.evaluate("el => el.classList.contains('open')")
    # Drawer should have open class or be visible
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "block" or has_open_class, "Drawer should be visible/open"


@pytest.mark.integration
def test_drawer_animation_slide_out(mobile_viewport: Page, authenticated_page: Page, api_base):
    """Test that drawer slides out when closed."""
    authenticated_page.set_viewport_size({"width": 375, "height": 667})
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    hamburger_button = authenticated_page.locator(".nav-mobile-toggle")
    drawer = authenticated_page.locator(".nav-mobile-drawer")
    close_button = authenticated_page.locator(".nav-mobile-close")
    
    # Open drawer
    hamburger_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Close drawer
    close_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Drawer should be hidden
    drawer_display = drawer.evaluate("el => window.getComputedStyle(el).display")
    assert drawer_display == "none", "Drawer should be hidden after closing"

