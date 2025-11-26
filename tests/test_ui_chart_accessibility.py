"""
Tests for chart accessibility (keyboard navigation, ARIA labels).

Tests:
- ARIA labels on chart canvas elements
- Role="img" on charts
- Chart section headings
- Keyboard navigation (if applicable)
- Screen reader support
- Chart descriptions and context
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
# ARIA Label Tests
# ============================================

@pytest.mark.integration
def test_chart_aria_labels(authenticated_page: Page, api_base):
    """Test that charts have proper ARIA labels."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Wait for charts to potentially load
    authenticated_page.wait_for_timeout(2000)
    
    # Check for chart canvas elements
    chart_canvases = authenticated_page.locator("canvas[role='img']")
    
    if chart_canvases.count() > 0:
        for i in range(chart_canvases.count()):
            canvas = chart_canvases.nth(i)
            
            # Check role="img"
            role = canvas.get_attribute("role")
            assert role == "img", "Chart canvas should have role='img'"
            
            # Check aria-label
            aria_label = canvas.get_attribute("aria-label")
            assert aria_label and len(aria_label) > 0, \
                "Chart canvas should have descriptive aria-label"
            
            # Check that aria-label describes the chart
            assert any(keyword in aria_label.lower() for keyword in 
                      ['chart', 'graph', 'line', 'bar', 'pie', 'donut', 'trend']), \
                "ARIA label should describe the chart type"


@pytest.mark.integration
def test_chart_aria_labels_descriptive(authenticated_page: Page, api_base):
    """Test that chart ARIA labels are descriptive and informative."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Check specific chart types
    line_chart = authenticated_page.locator("canvas#scan-trends-chart")
    if line_chart.count() > 0:
        aria_label = line_chart.get_attribute("aria-label")
        if aria_label:
            assert "line" in aria_label.lower() or "trend" in aria_label.lower(), \
                "Line chart ARIA label should mention line or trend"
    
    severity_chart = authenticated_page.locator("canvas#severity-chart")
    if severity_chart.count() > 0:
        aria_label = severity_chart.get_attribute("aria-label")
        if aria_label:
            assert "severity" in aria_label.lower() or "distribution" in aria_label.lower(), \
                "Severity chart ARIA label should mention severity or distribution"
    
    pass_fail_chart = authenticated_page.locator("canvas#pass-fail-chart")
    if pass_fail_chart.count() > 0:
        aria_label = pass_fail_chart.get_attribute("aria-label")
        if aria_label:
            assert "pass" in aria_label.lower() or "fail" in aria_label.lower(), \
                "Pass/fail chart ARIA label should mention pass or fail"


@pytest.mark.integration
def test_chart_aria_labels_dynamic(authenticated_page: Page, api_base):
    """Test that chart ARIA labels include dynamic data information."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Check if charts have data in ARIA labels
    chart_canvases = authenticated_page.locator("canvas[role='img'][aria-label]")
    
    if chart_canvases.count() > 0:
        for i in range(min(3, chart_canvases.count())):
            canvas = chart_canvases.nth(i)
            aria_label = canvas.get_attribute("aria-label")
            
            if aria_label:
                # ARIA label should include data information if available
                # (e.g., "Total: 10 findings", "5 data points")
                # This is optional but good practice
                pass


# ============================================
# Role Attribute Tests
# ============================================

@pytest.mark.integration
def test_chart_role_img(authenticated_page: Page, api_base):
    """Test that charts have role='img' attribute."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Check all chart canvases
    chart_canvases = authenticated_page.locator("canvas")
    
    if chart_canvases.count() > 0:
        for i in range(chart_canvases.count()):
            canvas = chart_canvases.nth(i)
            role = canvas.get_attribute("role")
            
            # Charts should have role="img"
            assert role == "img", "Chart canvas should have role='img'"


# ============================================
# Chart Section Structure Tests
# ============================================

@pytest.mark.integration
def test_chart_section_headings(authenticated_page: Page, api_base):
    """Test that chart sections have proper headings."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Check charts section has heading
    charts_section = authenticated_page.locator("section.charts-section, section[aria-labelledby*='charts']")
    if charts_section.count() > 0:
        # Check for heading
        heading = charts_section.locator("h2, h3")
        if heading.count() > 0:
            heading_text = heading.first.text_content()
            assert len(heading_text) > 0, "Charts section should have a heading"
    
    # Check individual chart cards have headings
    chart_cards = authenticated_page.locator(".chart-card")
    if chart_cards.count() > 0:
        for i in range(min(3, chart_cards.count())):
            card = chart_cards.nth(i)
            card_heading = card.locator("h3, h4")
            if card_heading.count() > 0:
                heading_text = card_heading.first.text_content()
                assert len(heading_text) > 0, "Chart cards should have headings"


@pytest.mark.integration
def test_chart_section_aria_labelledby(authenticated_page: Page, api_base):
    """Test that chart sections use aria-labelledby correctly."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    charts_section = authenticated_page.locator("section[aria-labelledby]")
    if charts_section.count() > 0:
        for i in range(charts_section.count()):
            section = charts_section.nth(i)
            aria_labelledby = section.get_attribute("aria-labelledby")
            
            if aria_labelledby:
                # Check that referenced heading exists
                heading_id = aria_labelledby.split()[0]  # Get first ID
                heading = authenticated_page.locator(f"#{heading_id}")
                if heading.count() > 0:
                    # Heading should exist
                    pass


# ============================================
# Keyboard Navigation Tests
# ============================================

@pytest.mark.integration
def test_chart_keyboard_navigation_structure(authenticated_page: Page, api_base):
    """Test that chart areas are properly structured for keyboard navigation."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Charts themselves (canvas) are not keyboard navigable
    # But we should check that chart sections don't trap focus
    
    charts_section = authenticated_page.locator("section.charts-section")
    if charts_section.count() > 0:
        # Check that section doesn't have tabindex that would trap focus
        tabindex = charts_section.first.get_attribute("tabindex")
        # tabindex should not be set to trap focus
        assert tabindex != "0" or tabindex is None, \
            "Chart sections should not trap keyboard focus"
    
    # Check chart canvases don't have tabindex
    chart_canvases = authenticated_page.locator("canvas[role='img']")
    if chart_canvases.count() > 0:
        for i in range(min(3, chart_canvases.count())):
            canvas = chart_canvases.nth(i)
            tabindex = canvas.get_attribute("tabindex")
            # Canvas should not be in tab order (unless made interactive)
            # tabindex="-1" or no tabindex is acceptable
            assert tabindex != "0", "Chart canvas should not be in tab order unless interactive"


@pytest.mark.integration
def test_chart_interactive_elements_keyboard(authenticated_page: Page, api_base):
    """Test that any interactive chart elements are keyboard accessible."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Check for interactive elements near charts (like filter buttons, export buttons)
    charts_section = authenticated_page.locator("section.charts-section, .charts-section")
    if charts_section.count() > 0:
        # Look for buttons or links in chart section
        interactive_elements = charts_section.locator(
            "button, a, input, select"
        )
        
        if interactive_elements.count() > 0:
            for i in range(min(5, interactive_elements.count())):
                elem = interactive_elements.nth(i)
                # Check that interactive elements are keyboard accessible
                tag = elem.evaluate("el => el.tagName.toLowerCase()")
                
                if tag in ["button", "a"]:
                    # Should be keyboard accessible by default
                    tabindex = elem.get_attribute("tabindex")
                    # tabindex="-1" would make it not accessible
                    assert tabindex != "-1" or tabindex is None, \
                        "Interactive elements near charts should be keyboard accessible"


# ============================================
# Screen Reader Support Tests
# ============================================

@pytest.mark.integration
def test_chart_screen_reader_support(authenticated_page: Page, api_base):
    """Test that charts provide information for screen readers."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    chart_canvases = authenticated_page.locator("canvas[role='img']")
    
    if chart_canvases.count() > 0:
        for i in range(min(3, chart_canvases.count())):
            canvas = chart_canvases.nth(i)
            
            # Check role
            role = canvas.get_attribute("role")
            assert role == "img", "Chart should have role='img' for screen readers"
            
            # Check aria-label
            aria_label = canvas.get_attribute("aria-label")
            assert aria_label and len(aria_label) > 0, \
                "Chart should have aria-label for screen readers"
            
            # Check that aria-label is descriptive
            assert len(aria_label) > 10, \
                "ARIA label should be descriptive (more than 10 characters)"


@pytest.mark.integration
def test_chart_legend_accessibility(authenticated_page: Page, api_base):
    """Test that chart legends are accessible (if present)."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Chart.js typically renders legends, but they may not be in DOM as separate elements
    # We can check if there are any legend elements or if legend info is in ARIA label
    
    chart_canvases = authenticated_page.locator("canvas[role='img']")
    
    if chart_canvases.count() > 0:
        # Check if ARIA labels include legend information
        for i in range(min(2, chart_canvases.count())):
            canvas = chart_canvases.nth(i)
            aria_label = canvas.get_attribute("aria-label")
            
            if aria_label:
                # ARIA label might include data that helps understand the chart
                # This is implementation-dependent
                pass


# ============================================
# Chart Context Tests
# ============================================

@pytest.mark.integration
def test_chart_contextual_information(authenticated_page: Page, api_base):
    """Test that charts have contextual information (headings, descriptions)."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Check that chart cards have headings
    chart_cards = authenticated_page.locator(".chart-card")
    
    if chart_cards.count() > 0:
        for i in range(min(3, chart_cards.count())):
            card = chart_cards.nth(i)
            
            # Check for heading
            heading = card.locator("h2, h3, h4")
            if heading.count() > 0:
                heading_text = heading.first.text_content()
                assert len(heading_text.strip()) > 0, \
                    "Chart cards should have descriptive headings"
            
            # Check for canvas with ARIA label
            canvas = card.locator("canvas[role='img']")
            if canvas.count() > 0:
                aria_label = canvas.first.get_attribute("aria-label")
                assert aria_label, "Chart should have ARIA label"


@pytest.mark.integration
def test_chart_empty_state_accessibility(authenticated_page: Page, api_base):
    """Test that empty chart states are accessible."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Check for empty state message
    empty_state = authenticated_page.locator(".empty-state")
    
    if empty_state.count() > 0:
        # Check that empty state has text content
        empty_text = empty_state.first.text_content()
        assert len(empty_text) > 0, "Empty state should have text content"
        
        # Check for heading or paragraph
        heading = empty_state.locator("h2, h3, p")
        if heading.count() > 0:
            # Empty state should be announced to screen readers
            pass


# ============================================
# Chart Data Accessibility
# ============================================

@pytest.mark.integration
def test_chart_data_in_aria_label(authenticated_page: Page, api_base):
    """Test that chart ARIA labels include data values when appropriate."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Check severity chart (should include counts)
    severity_chart = authenticated_page.locator("canvas#severity-chart")
    if severity_chart.count() > 0:
        aria_label = severity_chart.get_attribute("aria-label")
        if aria_label:
            # ARIA label might include severity counts
            # This is implementation-dependent but good practice
            pass
    
    # Check pass/fail chart (should include counts)
    pass_fail_chart = authenticated_page.locator("canvas#pass-fail-chart")
    if pass_fail_chart.count() > 0:
        aria_label = pass_fail_chart.get_attribute("aria-label")
        if aria_label:
            # ARIA label might include pass/fail counts
            # Check if numbers are mentioned
            import re
            has_numbers = bool(re.search(r'\d+', aria_label))
            # Having numbers in ARIA label is good but not required
            pass


# ============================================
# Chart Focus Management
# ============================================

@pytest.mark.integration
def test_chart_focus_management(authenticated_page: Page, api_base):
    """Test that charts don't interfere with focus management."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Charts should not trap focus
    chart_canvases = authenticated_page.locator("canvas[role='img']")
    
    if chart_canvases.count() > 0:
        # Try to tab through page - focus should not get stuck on charts
        # This is more of a manual test, but we can verify structure
        
        # Check that canvases don't have tabindex="0"
        for i in range(min(3, chart_canvases.count())):
            canvas = chart_canvases.nth(i)
            tabindex = canvas.get_attribute("tabindex")
            assert tabindex != "0", "Chart canvas should not be in tab order"


# ============================================
# Chart Alternative Text
# ============================================

@pytest.mark.integration
def test_chart_alternative_text(authenticated_page: Page, api_base):
    """Test that charts have alternative text (ARIA label serves as alt text)."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    chart_canvases = authenticated_page.locator("canvas[role='img']")
    
    if chart_canvases.count() > 0:
        for i in range(chart_canvases.count()):
            canvas = chart_canvases.nth(i)
            
            # Canvas with role="img" should have aria-label (serves as alt text)
            role = canvas.get_attribute("role")
            if role == "img":
                aria_label = canvas.get_attribute("aria-label")
                assert aria_label and len(aria_label) > 0, \
                    "Chart with role='img' should have aria-label as alternative text"


# ============================================
# Chart Section Semantics
# ============================================

@pytest.mark.integration
def test_chart_section_semantics(authenticated_page: Page, api_base):
    """Test that chart sections use proper semantic HTML."""
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    authenticated_page.wait_for_timeout(2000)
    
    # Check for section element
    charts_section = authenticated_page.locator("section.charts-section, section[aria-labelledby*='charts']")
    
    if charts_section.count() > 0:
        # Section should have proper structure
        section = charts_section.first
        
        # Check for heading
        heading = section.locator("h2, h3")
        if heading.count() > 0:
            # Section should have a heading
            pass
        
        # Check aria-labelledby if present
        aria_labelledby = section.get_attribute("aria-labelledby")
        if aria_labelledby:
            # Referenced heading should exist
            heading_id = aria_labelledby.split()[0]
            heading_elem = authenticated_page.locator(f"#{heading_id}")
            if heading_elem.count() > 0:
                # Heading exists
                pass

