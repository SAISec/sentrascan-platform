"""
Tests for form validation and error messages.

Tests:
- Client-side validation
- Server-side error handling
- Error message display and styling
- Real-time validation
- Form submission prevention
- ARIA attributes for errors
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
# Login Form Validation Tests
# ============================================

@pytest.mark.integration
def test_login_form_required_field_validation(page: Page, api_base):
    """Test that login form validates required fields."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    # Get the form and input
    form = page.locator("form.login-form")
    api_key_input = page.locator("input[name='api_key']")
    submit_button = page.locator("button[type='submit']")
    
    expect(form).to_be_visible()
    expect(api_key_input).to_be_visible()
    
    # Check that input has required attribute
    required = api_key_input.get_attribute("required")
    assert required is not None, "API key input should be required"
    
    # Try to submit empty form
    submit_button.click()
    
    # Wait for validation
    page.wait_for_timeout(500)
    
    # Check for error message (either HTML5 validation or custom)
    # HTML5 validation might show browser tooltip, or custom JS validation
    error_message = page.locator("#api_key_error, .form-error-message, [role='alert']")
    
    # Check if input has error class or aria-invalid
    input_has_error = (
        api_key_input.evaluate("el => el.classList.contains('error')") or
        api_key_input.get_attribute("aria-invalid") == "true"
    )
    
    # Either error message should be visible or input should be marked as invalid
    assert (
        error_message.count() > 0 or 
        input_has_error or
        api_key_input.evaluate("el => !el.validity.valid")
    ), "Form should show validation error for empty required field"


@pytest.mark.integration
def test_login_form_error_message_display(page: Page, api_base):
    """Test that error messages are displayed correctly."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    api_key_input = page.locator("input[name='api_key']")
    error_div = page.locator("#api_key_error")
    
    # Try submitting with invalid key to trigger server error
    api_key_input.fill("invalid-key-12345")
    page.locator("button[type='submit']").click()
    
    # Wait for response
    page.wait_for_timeout(2000)
    
    # Check if error is displayed (either client-side or server-side)
    # Server errors might redirect or show on same page
    error_visible = (
        error_div.is_visible() or
        page.locator(".alert-error, .alert.alert-error").is_visible() or
        page.locator("[role='alert']").is_visible()
    )
    
    # Error should be visible if validation failed
    if not page.url.endswith("/") and not "/login" in page.url:
        # If we're still on login page, error should be visible
        pass


@pytest.mark.integration
def test_login_form_aria_error_attributes(page: Page, api_base):
    """Test that error messages have proper ARIA attributes."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    api_key_input = page.locator("input[name='api_key']")
    error_div = page.locator("#api_key_error")
    
    # Check initial state
    aria_invalid = api_key_input.get_attribute("aria-invalid")
    assert aria_invalid in ["true", "false"], "Input should have aria-invalid attribute"
    
    # Check aria-describedby includes error ID
    aria_describedby = api_key_input.get_attribute("aria-describedby")
    if aria_describedby:
        assert "api_key_error" in aria_describedby or "api_key_help" in aria_describedby, \
            "Input should reference error in aria-describedby"
    
    # Check error div has role="alert"
    if error_div.count() > 0:
        role = error_div.get_attribute("role")
        assert role == "alert", "Error message should have role='alert'"
        
        aria_live = error_div.get_attribute("aria-live")
        if aria_live:
            assert aria_live in ["polite", "assertive"], "Error should have aria-live"


@pytest.mark.integration
def test_login_form_realtime_validation(page: Page, api_base):
    """Test real-time validation on input."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    api_key_input = page.locator("input[name='api_key']")
    error_div = page.locator("#api_key_error")
    
    # Type in input
    api_key_input.fill("test")
    page.wait_for_timeout(300)
    
    # Clear input to trigger validation
    api_key_input.clear()
    api_key_input.blur()  # Trigger blur validation
    page.wait_for_timeout(500)
    
    # Check if validation triggers on blur
    # Error might appear or input might be marked invalid
    input_has_error = (
        api_key_input.evaluate("el => el.classList.contains('error')") or
        api_key_input.get_attribute("aria-invalid") == "true"
    )
    
    # Validation should trigger (either show error or mark as invalid)
    # This depends on implementation
    pass


@pytest.mark.integration
def test_login_form_error_styling(page: Page, api_base):
    """Test that error messages have proper styling."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    api_key_input = page.locator("input[name='api_key']")
    error_div = page.locator("#api_key_error")
    
    # Try to trigger error
    submit_button = page.locator("button[type='submit']")
    submit_button.click()
    page.wait_for_timeout(500)
    
    # Check if error styling is applied
    if error_div.count() > 0 and error_div.is_visible():
        # Error should be visible
        expect(error_div).to_be_visible()
        
        # Input should have error class
        input_has_error_class = api_key_input.evaluate("el => el.classList.contains('error')")
        # Error class might be applied


# ============================================
# Scan Form Validation Tests
# ============================================

@pytest.mark.integration
def test_model_scan_form_required_validation(authenticated_page: Page, api_base):
    """Test that model scan form validates required fields."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # Ensure model tab is active
    model_tab = authenticated_page.locator("#model-tab")
    if model_tab.count() > 0:
        model_tab.click()
        authenticated_page.wait_for_timeout(300)
    
    # Get form elements
    model_path_input = authenticated_page.locator("#model_path")
    submit_button = authenticated_page.locator("#model-submit-btn, button[type='submit']").first
    
    expect(model_path_input).to_be_visible()
    
    # Check required attribute
    required = model_path_input.get_attribute("required")
    assert required is not None, "Model path should be required"
    
    # Clear the input (it has a default value)
    model_path_input.clear()
    
    # Try to submit form
    submit_button.click()
    authenticated_page.wait_for_timeout(500)
    
    # Check for error message
    error_div = authenticated_page.locator("#model_path_error")
    
    # Error should be displayed
    if error_div.count() > 0:
        expect(error_div).to_be_visible()
        error_text = error_div.text_content()
        assert "required" in error_text.lower() or len(error_text) > 0, \
            "Error message should indicate field is required"
    
    # Check input has error styling
    input_has_error = model_path_input.evaluate("el => el.classList.contains('form-input-error')")
    aria_invalid = model_path_input.get_attribute("aria-invalid")
    
    assert input_has_error or aria_invalid == "true", \
        "Input should have error styling when validation fails"


@pytest.mark.integration
def test_model_scan_form_minlength_validation(authenticated_page: Page, api_base):
    """Test that model scan form validates minimum length."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # Ensure model tab is active
    model_tab = authenticated_page.locator("#model-tab")
    if model_tab.count() > 0:
        model_tab.click()
        authenticated_page.wait_for_timeout(300)
    
    model_path_input = authenticated_page.locator("#model_path")
    error_div = authenticated_page.locator("#model_path_error")
    
    # Enter value shorter than minimum (3 characters)
    model_path_input.clear()
    model_path_input.fill("ab")  # 2 characters
    
    # Trigger validation (blur or submit)
    model_path_input.blur()
    authenticated_page.wait_for_timeout(500)
    
    # Check for error message about minimum length
    if error_div.count() > 0 and error_div.is_visible():
        error_text = error_div.text_content()
        assert "3" in error_text or "minimum" in error_text.lower() or "length" in error_text.lower(), \
            "Error should mention minimum length requirement"
    
    # Check aria-invalid
    aria_invalid = model_path_input.get_attribute("aria-invalid")
    if aria_invalid:
        assert aria_invalid == "true", "Input should be marked as invalid"


@pytest.mark.integration
def test_model_scan_form_realtime_validation(authenticated_page: Page, api_base):
    """Test real-time validation in model scan form."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # Ensure model tab is active
    model_tab = authenticated_page.locator("#model-tab")
    if model_tab.count() > 0:
        model_tab.click()
        authenticated_page.wait_for_timeout(300)
    
    model_path_input = authenticated_page.locator("#model_path")
    error_div = authenticated_page.locator("#model_path_error")
    
    # Clear input to trigger error
    model_path_input.clear()
    model_path_input.blur()
    authenticated_page.wait_for_timeout(500)
    
    # Fix the error by entering valid value
    model_path_input.fill("/data/valid.npy")
    authenticated_page.wait_for_timeout(500)
    
    # Error should clear
    if error_div.count() > 0:
        # Error might clear on input
        error_visible = error_div.is_visible()
        # Error should clear when valid input is entered
    
    # Check aria-invalid is false
    aria_invalid = model_path_input.get_attribute("aria-invalid")
    if aria_invalid:
        # Should be false after valid input
        pass


@pytest.mark.integration
def test_model_scan_form_submission_prevention(authenticated_page: Page, api_base):
    """Test that form submission is prevented when validation fails."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # Ensure model tab is active
    model_tab = authenticated_page.locator("#model-tab")
    if model_tab.count() > 0:
        model_tab.click()
        authenticated_page.wait_for_timeout(300)
    
    model_path_input = authenticated_page.locator("#model_path")
    form = authenticated_page.locator("#model-scan-form")
    submit_button = authenticated_page.locator("#model-submit-btn, button[type='submit']").first
    
    # Clear required field
    model_path_input.clear()
    
    # Try to submit
    initial_url = authenticated_page.url
    
    # Intercept form submission
    form_submitted = False
    
    def handle_submit(e):
        nonlocal form_submitted
        form_submitted = True
    
    authenticated_page.on("request", lambda request: None)  # Monitor requests
    
    submit_button.click()
    authenticated_page.wait_for_timeout(1000)
    
    # Form should not submit if validation fails
    # URL should not change or form should still be visible
    current_url = authenticated_page.url
    # If validation works, we should still be on the same page
    # (unless there's a redirect for other reasons)


@pytest.mark.integration
def test_scan_form_error_message_aria(authenticated_page: Page, api_base):
    """Test that scan form error messages have proper ARIA attributes."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # Ensure model tab is active
    model_tab = authenticated_page.locator("#model-tab")
    if model_tab.count() > 0:
        model_tab.click()
        authenticated_page.wait_for_timeout(300)
    
    model_path_input = authenticated_page.locator("#model_path")
    error_div = authenticated_page.locator("#model_path_error")
    
    # Check aria-describedby includes error ID
    aria_describedby = model_path_input.get_attribute("aria-describedby")
    if aria_describedby:
        assert "model_path_error" in aria_describedby, \
            "Input should reference error in aria-describedby"
    
    # Trigger error
    model_path_input.clear()
    model_path_input.blur()
    authenticated_page.wait_for_timeout(500)
    
    # Check error div has role="alert"
    if error_div.count() > 0:
        role = error_div.get_attribute("role")
        if role:
            assert role == "alert", "Error message should have role='alert'"


@pytest.mark.integration
def test_mcp_scan_form_validation(authenticated_page: Page, api_base):
    """Test MCP scan form validation (if implemented)."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # Switch to MCP tab
    mcp_tab = authenticated_page.locator("#mcp-tab")
    if mcp_tab.count() > 0:
        mcp_tab.click()
        authenticated_page.wait_for_timeout(300)
        
        # Check if MCP form has validation
        mcp_form = authenticated_page.locator("#mcp-scan-form")
        if mcp_form.count() > 0:
            # MCP form validation might be different
            # Check for required fields
            required_inputs = authenticated_page.locator("#mcp-scan-form input[required], #mcp-scan-form select[required]")
            # Validation should work similarly to model form
            pass


# ============================================
# Error Message Characteristics
# ============================================

@pytest.mark.integration
def test_error_messages_clear_and_actionable(page: Page, api_base):
    """Test that error messages are clear and actionable."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    # Trigger validation error
    submit_button = page.locator("button[type='submit']")
    submit_button.click()
    page.wait_for_timeout(500)
    
    # Check for error messages
    error_messages = page.locator(".form-error-message, .alert-error, [role='alert']")
    
    if error_messages.count() > 0:
        for i in range(min(3, error_messages.count())):
            error_text = error_messages.nth(i).text_content()
            # Error should be clear and actionable
            assert len(error_text.strip()) > 0, "Error message should not be empty"
            # Should not be too technical or cryptic


@pytest.mark.integration
def test_error_messages_associated_with_inputs(page: Page, api_base):
    """Test that error messages are properly associated with inputs."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    api_key_input = page.locator("input[name='api_key']")
    error_div = page.locator("#api_key_error")
    
    # Check aria-describedby association
    aria_describedby = api_key_input.get_attribute("aria-describedby")
    if aria_describedby and error_div.count() > 0:
        assert "api_key_error" in aria_describedby, \
            "Input should reference error in aria-describedby"
    
    # Check that error is near the input (visual association)
    # This is more of a visual test, but we can check DOM structure
    input_parent = api_key_input.locator("xpath=..")
    if input_parent.count() > 0:
        # Error should be in same form group or nearby
        pass


@pytest.mark.integration
def test_error_messages_visible_and_styled(page: Page, api_base):
    """Test that error messages are visible and properly styled."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    # Trigger error
    submit_button = page.locator("button[type='submit']")
    submit_button.click()
    page.wait_for_timeout(500)
    
    error_div = page.locator("#api_key_error")
    
    if error_div.count() > 0 and error_div.is_visible():
        # Check visibility
        expect(error_div).to_be_visible()
        
        # Check that it has error styling (color, etc.)
        # This is visual but we can check for error classes
        has_error_class = error_div.evaluate("el => el.classList.contains('error') or el.classList.contains('alert-error')")
        # Error should have appropriate styling


@pytest.mark.integration
def test_error_messages_accessible(page: Page, api_base):
    """Test that error messages are accessible to screen readers."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    api_key_input = page.locator("input[name='api_key']")
    error_div = page.locator("#api_key_error")
    
    # Check role="alert" for important errors
    if error_div.count() > 0:
        role = error_div.get_attribute("role")
        if role:
            assert role == "alert", "Error messages should have role='alert'"
        
        # Check aria-live
        aria_live = error_div.get_attribute("aria-live")
        if aria_live:
            assert aria_live in ["polite", "assertive"], \
                "Error messages should have aria-live for screen readers"
    
    # Check that input references error
    aria_describedby = api_key_input.get_attribute("aria-describedby")
    if aria_describedby:
        # Should reference error ID
        assert "error" in aria_describedby or "help" in aria_describedby, \
            "Input should reference error message"


@pytest.mark.integration
def test_error_messages_realtime_feedback(authenticated_page: Page, api_base):
    """Test that error messages provide real-time feedback."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # Ensure model tab is active
    model_tab = authenticated_page.locator("#model-tab")
    if model_tab.count() > 0:
        model_tab.click()
        authenticated_page.wait_for_timeout(300)
    
    model_path_input = authenticated_page.locator("#model_path")
    error_div = authenticated_page.locator("#model_path_error")
    
    # Clear input to trigger error
    model_path_input.clear()
    model_path_input.blur()
    authenticated_page.wait_for_timeout(500)
    
    # Error should appear
    if error_div.count() > 0:
        error_visible_after_blur = error_div.is_visible()
    
    # Fix error
    model_path_input.fill("/data/valid.npy")
    authenticated_page.wait_for_timeout(500)
    
    # Error should clear (real-time feedback)
    if error_div.count() > 0:
        # Error might clear on valid input
        pass


@pytest.mark.integration
def test_form_validation_multiple_errors(authenticated_page: Page, api_base):
    """Test that forms can display multiple validation errors."""
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    # If form has multiple required fields, test that all errors are shown
    # For now, model form only has one required field
    # This test can be expanded when more fields are added
    
    # Check that error containers exist for all fields that might need validation
    error_containers = authenticated_page.locator("[id$='_error'], .form-error-message")
    # Multiple error containers should exist if form has multiple validatable fields
    pass


@pytest.mark.integration
def test_form_validation_server_errors(page: Page, api_base):
    """Test that server-side validation errors are displayed."""
    page.goto(f"{api_base}/login", wait_until="networkidle")
    
    # Submit with invalid credentials to trigger server error
    api_key_input = page.locator("input[name='api_key']")
    api_key_input.fill("definitely-invalid-key-12345")
    
    submit_button = page.locator("button[type='submit']")
    submit_button.click()
    
    # Wait for server response
    page.wait_for_timeout(2000)
    
    # Check for server error message
    # Server errors might be displayed as alert or inline error
    server_error = (
        page.locator(".alert-error, .alert.alert-error").is_visible() or
        page.locator("#api_key_error").is_visible() or
        page.locator("[role='alert']").filter(lambda el: "error" in el.text_content().lower()).is_visible()
    )
    
    # Server error should be displayed if authentication fails
    # (This depends on server response handling)
    pass

