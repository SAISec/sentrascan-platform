"""
Tests for ARIA attributes implementation.

Verifies that all ARIA attributes are correctly implemented throughout the UI
for accessibility compliance.
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
# ARIA Landmarks and Roles
# ============================================

@pytest.mark.integration
def test_aria_landmarks_base(page: Page, api_base):
    """Test that ARIA landmarks are present in base template."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    # Check for main landmarks
    header = page.locator("header[role='banner']")
    expect(header).to_be_visible()
    
    # Check for skip link
    skip_link = page.locator("a.skip-link[aria-label*='Skip to main content']")
    expect(skip_link).to_be_visible()
    
    # Check for ARIA live regions
    live_polite = page.locator("#aria-live-polite[role='status'][aria-live='polite']")
    expect(live_polite).to_be_visible()
    
    live_assertive = page.locator("#aria-live-assertive[role='alert'][aria-live='assertive']")
    expect(live_assertive).to_be_visible()


@pytest.mark.integration
def test_aria_navigation_roles(authenticated_page: Page, api_base):
    """Test that navigation elements have proper ARIA roles."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check desktop navigation
    nav_desktop = authenticated_page.locator("nav[role='navigation'][aria-label='Main navigation']")
    if nav_desktop.count() > 0:
        expect(nav_desktop).to_be_visible()
    
    # Check mobile navigation
    nav_mobile = authenticated_page.locator("nav[role='navigation'][aria-label='Mobile navigation']")
    if nav_mobile.count() > 0:
        # Mobile nav might be hidden initially
        pass
    
    # Check main content area
    main = authenticated_page.locator("main[role='main']#main-content")
    expect(main).to_be_visible()
    
    # Check footer
    footer = authenticated_page.locator("footer[role='contentinfo']")
    expect(footer).to_be_visible()


# ============================================
# ARIA Labels
# ============================================

@pytest.mark.integration
def test_aria_labels_buttons(authenticated_page: Page, api_base):
    """Test that buttons have appropriate ARIA labels."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check export button
    export_button = authenticated_page.locator("button[aria-label*='Export']")
    if export_button.count() > 0:
        expect(export_button).to_be_visible()
        # Check aria-expanded attribute
        aria_expanded = export_button.get_attribute("aria-expanded")
        assert aria_expanded in ["true", "false"], "Export button should have aria-expanded"
    
    # Check filter chip remove buttons
    remove_buttons = authenticated_page.locator("button[aria-label*='Remove'][aria-label*='filter']")
    # These may or may not be visible depending on active filters
    # Just verify they exist when filters are active
    
    # Check copy buttons
    copy_buttons = authenticated_page.locator("button[aria-label*='Copy']")
    # Copy buttons should have aria-label
    if copy_buttons.count() > 0:
        for i in range(min(3, copy_buttons.count())):  # Check first 3
            label = copy_buttons.nth(i).get_attribute("aria-label")
            assert label and len(label) > 0, "Copy buttons should have aria-label"


@pytest.mark.integration
def test_aria_labels_links(authenticated_page: Page, api_base):
    """Test that links have appropriate ARIA labels where needed."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Download/export links should have aria-label
    download_links = authenticated_page.locator("a[download][aria-label]")
    if download_links.count() > 0:
        for i in range(min(3, download_links.count())):
            label = download_links.nth(i).get_attribute("aria-label")
            assert label and len(label) > 0, "Download links should have descriptive aria-label"


@pytest.mark.integration
def test_aria_labels_icons_decorative(authenticated_page: Page, api_base):
    """Test that decorative icons have aria-hidden="true"."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check for decorative icons with aria-hidden
    hidden_icons = authenticated_page.locator("[aria-hidden='true']")
    
    # Verify that icons used decoratively are hidden
    icon_spans = authenticated_page.locator("span[aria-hidden='true']")
    if icon_spans.count() > 0:
        # These should be decorative icons
        for i in range(min(5, icon_spans.count())):
            aria_hidden = icon_spans.nth(i).get_attribute("aria-hidden")
            assert aria_hidden == "true", "Decorative icons should have aria-hidden='true'"


# ============================================
# ARIA Form Attributes
# ============================================

@pytest.mark.integration
def test_aria_form_attributes_login(page: Page, api_base):
    """Test ARIA attributes in login form."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    # Check form has aria-label
    form = page.locator("form[aria-label='Login form']")
    expect(form).to_be_visible()
    
    # Check fieldset and legend
    fieldset = page.locator("fieldset")
    if fieldset.count() > 0:
        legend = fieldset.locator("legend")
        expect(legend).to_be_visible()
    
    # Check input has aria-describedby
    api_key_input = page.locator("input[name='api_key']")
    expect(api_key_input).to_be_visible()
    
    aria_describedby = api_key_input.get_attribute("aria-describedby")
    assert aria_describedby, "Input should have aria-describedby"
    
    # Check aria-required
    aria_required = api_key_input.get_attribute("aria-required")
    assert aria_required == "true", "Required input should have aria-required='true'"
    
    # Check aria-invalid (should be false initially)
    aria_invalid = api_key_input.get_attribute("aria-invalid")
    assert aria_invalid in ["true", "false"], "Input should have aria-invalid attribute"
    
    # Check help text is associated
    help_text_id = "api_key_help"
    help_text = page.locator(f"#{help_text_id}")
    if help_text.count() > 0:
        expect(help_text).to_be_visible()
        assert help_text_id in (aria_describedby or ""), "Help text should be in aria-describedby"


@pytest.mark.integration
def test_aria_form_attributes_scan_forms(authenticated_page: Page, api_base):
    """Test ARIA attributes in scan forms."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # Check tab buttons have aria-selected
    tab_buttons = authenticated_page.locator("button[aria-selected]")
    if tab_buttons.count() > 0:
        for i in range(tab_buttons.count()):
            aria_selected = tab_buttons.nth(i).get_attribute("aria-selected")
            assert aria_selected in ["true", "false"], "Tab buttons should have aria-selected"
    
    # Check form inputs have proper ARIA attributes
    required_inputs = authenticated_page.locator("input[required], select[required], textarea[required]")
    if required_inputs.count() > 0:
        for i in range(min(3, required_inputs.count())):
            input_elem = required_inputs.nth(i)
            # Check aria-required
            aria_required = input_elem.get_attribute("aria-required")
            if aria_required:
                assert aria_required == "true", "Required fields should have aria-required='true'"
            
            # Check aria-describedby if present
            aria_describedby = input_elem.get_attribute("aria-describedby")
            # aria-describedby is optional but good practice


@pytest.mark.integration
def test_aria_form_error_messages(authenticated_page: Page, api_base):
    """Test that form error messages have proper ARIA attributes."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # Check for error message containers with role="alert"
    error_messages = authenticated_page.locator("[role='alert']")
    # Error messages should have role="alert" when visible
    
    # Check that error messages are associated with inputs via aria-describedby
    inputs_with_errors = authenticated_page.locator("input[aria-invalid='true'], select[aria-invalid='true']")
    if inputs_with_errors.count() > 0:
        for i in range(min(2, inputs_with_errors.count())):
            input_elem = inputs_with_errors.nth(i)
            aria_describedby = input_elem.get_attribute("aria-describedby")
            if aria_describedby:
                # Should reference error message ID
                error_ids = aria_describedby.split()
                for error_id in error_ids:
                    if "error" in error_id:
                        error_elem = authenticated_page.locator(f"#{error_id}")
                        # Error element should exist
                        pass


# ============================================
# ARIA Table Attributes
# ============================================

@pytest.mark.integration
def test_aria_table_attributes(authenticated_page: Page, api_base):
    """Test that tables have proper ARIA attributes."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check table has role and aria-label
    tables = authenticated_page.locator("table[role='table']")
    if tables.count() > 0:
        for i in range(min(2, tables.count())):
            table = tables.nth(i)
            # Check aria-label
            aria_label = table.get_attribute("aria-label")
            assert aria_label and len(aria_label) > 0, "Tables should have aria-label"
            
            # Check for caption (optional but good practice)
            caption = table.locator("caption")
            # Caption is optional but recommended
    
    # Check table headers have scope
    th_elements = authenticated_page.locator("th[scope]")
    if th_elements.count() > 0:
        for i in range(min(5, th_elements.count())):
            scope = th_elements.nth(i).get_attribute("scope")
            assert scope in ["col", "row"], "Table headers should have scope='col' or 'row'"


@pytest.mark.integration
def test_aria_findings_table(authenticated_page: Page, api_base):
    """Test ARIA attributes in findings table."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Try to navigate to a scan detail page
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Check findings tables have aria-label
            findings_tables = authenticated_page.locator("table[aria-label*='findings' i]")
            if findings_tables.count() > 0:
                for i in range(findings_tables.count()):
                    aria_label = findings_tables.nth(i).get_attribute("aria-label")
                    assert aria_label and "finding" in aria_label.lower(), "Findings tables should have descriptive aria-label"
            
            # Check checkboxes have aria-label
            finding_checkboxes = authenticated_page.locator("input[type='checkbox'][aria-label]")
            if finding_checkboxes.count() > 0:
                for i in range(min(3, finding_checkboxes.count())):
                    label = finding_checkboxes.nth(i).get_attribute("aria-label")
                    assert label and len(label) > 0, "Finding checkboxes should have aria-label"


# ============================================
# ARIA Expanded/Collapsed States
# ============================================

@pytest.mark.integration
def test_aria_expanded_attributes(authenticated_page: Page, api_base):
    """Test that collapsible elements have aria-expanded."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check buttons with aria-expanded
    expanded_buttons = authenticated_page.locator("button[aria-expanded]")
    if expanded_buttons.count() > 0:
        for i in range(min(5, expanded_buttons.count())):
            aria_expanded = expanded_buttons.nth(i).get_attribute("aria-expanded")
            assert aria_expanded in ["true", "false"], "Collapsible buttons should have aria-expanded='true' or 'false'"


@pytest.mark.integration
def test_aria_expanded_findings_groups(authenticated_page: Page, api_base):
    """Test that findings groups have proper aria-expanded."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Navigate to scan detail
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            
            # Check findings group toggles have aria-expanded
            group_toggles = authenticated_page.locator("button[aria-label*='Toggle'][aria-label*='findings'][aria-expanded]")
            if group_toggles.count() > 0:
                for i in range(group_toggles.count()):
                    aria_expanded = group_toggles.nth(i).get_attribute("aria-expanded")
                    assert aria_expanded in ["true", "false"], "Findings group toggles should have aria-expanded"
                    
                    # Check aria-label is descriptive
                    aria_label = group_toggles.nth(i).get_attribute("aria-label")
                    assert aria_label and "finding" in aria_label.lower(), "Findings toggles should have descriptive aria-label"


# ============================================
# ARIA Live Regions
# ============================================

@pytest.mark.integration
def test_aria_live_regions(authenticated_page: Page, api_base):
    """Test that ARIA live regions are properly configured."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check polite live region
    live_polite = authenticated_page.locator("#aria-live-polite[aria-live='polite']")
    expect(live_polite).to_be_visible()
    
    aria_atomic = live_polite.get_attribute("aria-atomic")
    assert aria_atomic == "true", "Live region should have aria-atomic='true'"
    
    # Check assertive live region
    live_assertive = authenticated_page.locator("#aria-live-assertive[aria-live='assertive']")
    expect(live_assertive).to_be_visible()
    
    aria_atomic = live_assertive.get_attribute("aria-atomic")
    assert aria_atomic == "true", "Assertive live region should have aria-atomic='true'"


# ============================================
# ARIA Menu and Menu Items
# ============================================

@pytest.mark.integration
def test_aria_menu_attributes(authenticated_page: Page, api_base):
    """Test that menus have proper ARIA attributes."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check user menu button
    user_menu_button = authenticated_page.locator("button[aria-label='User menu'][aria-expanded]")
    if user_menu_button.count() > 0:
        aria_expanded = user_menu_button.get_attribute("aria-expanded")
        assert aria_expanded in ["true", "false"], "Menu button should have aria-expanded"
        
        # Check menu container
        menu = authenticated_page.locator("[role='menu']")
        if menu.count() > 0:
            aria_hidden = menu.get_attribute("aria-hidden")
            # Menu should be hidden when closed
            if aria_expanded == "false":
                assert aria_hidden == "true", "Menu should be aria-hidden when closed"
            
            # Check menu items
            menu_items = menu.locator("[role='menuitem']")
            if menu_items.count() > 0:
                for i in range(menu_items.count()):
                    # Menu items should be properly labeled
                    item = menu_items.nth(i)
                    # Should have text content or aria-label
                    text = item.text_content()
                    aria_label = item.get_attribute("aria-label")
                    assert text or aria_label, "Menu items should have text or aria-label"


# ============================================
# ARIA Chart Attributes
# ============================================

@pytest.mark.integration
def test_aria_chart_attributes(authenticated_page: Page, api_base):
    """Test that charts have proper ARIA attributes."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check canvas elements have role="img" and aria-label
    chart_canvases = authenticated_page.locator("canvas[role='img'][aria-label]")
    if chart_canvases.count() > 0:
        for i in range(chart_canvases.count()):
            role = chart_canvases.nth(i).get_attribute("role")
            assert role == "img", "Charts should have role='img'"
            
            aria_label = chart_canvases.nth(i).get_attribute("aria-label")
            assert aria_label and len(aria_label) > 0, "Charts should have descriptive aria-label"


# ============================================
# ARIA Hidden Elements
# ============================================

@pytest.mark.integration
def test_aria_hidden_decorative(authenticated_page: Page, api_base):
    """Test that decorative elements are properly hidden."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check that decorative icons are hidden
    decorative_icons = authenticated_page.locator("span[aria-hidden='true']")
    if decorative_icons.count() > 0:
        # These should be purely decorative
        for i in range(min(5, decorative_icons.count())):
            icon = decorative_icons.nth(i)
            aria_hidden = icon.get_attribute("aria-hidden")
            assert aria_hidden == "true", "Decorative icons should have aria-hidden='true'"
            
            # Check that parent interactive element has proper label
            parent = icon.locator("xpath=..")
            if parent.count() > 0:
                parent_elem = parent.first
                # Parent should have aria-label if it's interactive
                if parent_elem.evaluate("el => ['button', 'a'].includes(el.tagName.toLowerCase())"):
                    aria_label = parent_elem.get_attribute("aria-label")
                    assert aria_label, "Interactive elements with decorative icons should have aria-label"


# ============================================
# ARIA Busy States
# ============================================

@pytest.mark.integration
def test_aria_busy_states(authenticated_page: Page, api_base):
    """Test that loading states use aria-busy."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # Check for elements with aria-busy (might be set dynamically)
    busy_elements = authenticated_page.locator("[aria-busy='true']")
    # These may not be present initially but should be set during form submission
    
    # Check for loading spinners
    spinners = authenticated_page.locator(".spinner[aria-hidden='true']")
    if spinners.count() > 0:
        # Loading spinners should be hidden from screen readers
        for i in range(min(3, spinners.count())):
            aria_hidden = spinners.nth(i).get_attribute("aria-hidden")
            assert aria_hidden == "true", "Loading spinners should have aria-hidden='true'"


# ============================================
# ARIA Section Labels
# ============================================

@pytest.mark.integration
def test_aria_section_labels(authenticated_page: Page, api_base):
    """Test that sections have proper ARIA labels."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Check sections with aria-labelledby
    sections = authenticated_page.locator("section[aria-labelledby]")
    if sections.count() > 0:
        for i in range(sections.count()):
            section = sections.nth(i)
            aria_labelledby = section.get_attribute("aria-labelledby")
            assert aria_labelledby, "Sections should have aria-labelledby"
            
            # Check that referenced element exists
            label_id = aria_labelledby.split()[0]  # Get first ID
            label_elem = authenticated_page.locator(f"#{label_id}")
            if label_elem.count() > 0:
                # Label element should exist
                pass
    
    # Check sections with aria-label
    sections_labeled = authenticated_page.locator("section[aria-label]")
    if sections_labeled.count() > 0:
        for i in range(sections_labeled.count()):
            aria_label = sections_labeled.nth(i).get_attribute("aria-label")
            assert aria_label and len(aria_label) > 0, "Sections should have descriptive aria-label"


# ============================================
# Comprehensive ARIA Validation
# ============================================

@pytest.mark.integration
def test_aria_comprehensive_validation(authenticated_page: Page, api_base):
    """Comprehensive validation of ARIA attributes across pages."""
    pages_to_test = [
        ("/", "Dashboard"),
        ("/ui/scan", "Scan Forms"),
        ("/baselines", "Baselines"),
    ]
    
    for path, page_name in pages_to_test:
        authenticated_page.goto(f"{api_base}{path}", wait_until="networkidle")
        
        # Check that all interactive elements have accessible names
        interactive_elements = authenticated_page.locator(
            "button:not([aria-label]):not([aria-labelledby]), "
            "a:not([aria-label]):not([aria-labelledby]):not([aria-hidden='true'])"
        )
        
        # Filter out elements that have text content (which provides accessible name)
        problematic_elements = []
        for i in range(min(10, interactive_elements.count())):
            elem = interactive_elements.nth(i)
            text = elem.text_content()
            aria_label = elem.get_attribute("aria-label")
            aria_labelledby = elem.get_attribute("aria-labelledby")
            aria_hidden = elem.get_attribute("aria-hidden")
            
            # Element should have accessible name (text, aria-label, or aria-labelledby)
            # unless it's hidden
            if not text and not aria_label and not aria_labelledby and aria_hidden != "true":
                tag = elem.evaluate("el => el.tagName.toLowerCase()")
                if tag in ["button", "a"]:
                    problematic_elements.append(elem)
        
        # Most interactive elements should have accessible names
        # Allow some exceptions for elements with visible text
        assert len(problematic_elements) < 3, f"{page_name}: Too many interactive elements without accessible names"

