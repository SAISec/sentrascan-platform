# Unit Tests for SentraScan Platform JavaScript

This directory contains unit tests for the JavaScript modules in the SentraScan Platform.

## Running Tests

### Browser-based Testing (Jasmine)

The tests use Jasmine, a behavior-driven development (BDD) testing framework for JavaScript.

1. **Open the test runner in a browser:**
   - Navigate to `src/sentrascan/web/static/js/__tests__/test-runner.html`
   - Open this file in a web browser (Chrome, Firefox, Safari, or Edge)
   - The tests will run automatically and display results

2. **Or serve via HTTP:**
   ```bash
   # From the project root
   cd src/sentrascan/web/static/js/__tests__
   python -m http.server 8000
   # Then open http://localhost:8000/test-runner.html in your browser
   ```

## Test Files

- `utils.test.js` - Tests for utility functions:
  - `copyToClipboard()` - Clipboard API and fallback methods
  - `showToast()` fallback - Toast notification fallback
  - `initTooltips()` - Tooltip initialization and positioning

- `filters.test.js` - Tests for filter functionality:
  - Table sorting (`filters.js`) - Sort direction toggling, URL parameter handling
  - Filter chips (`filtering.js`) - Add, remove, clear filter chips
  - Multi-select components - Option selection handling
  - Date pickers - Min/max date initialization
  - Global search - Debounced search, form submission, URL encoding
  - Helper functions - HTML escaping

- `modal.test.js` - Tests for modal/dialog component:
  - `openModal()` - Modal creation, title handling, content insertion
  - `closeModal()` - Modal removal, body scroll restoration, focus restoration
  - ESC key support - Keyboard accessibility
  - `showConfirmDialog()` - Confirmation dialogs with callbacks
  - ARIA attributes - Role, aria-modal, aria-labelledby
  - Focus management - Focus trap, focus restoration
  - Multiple modals - Handling multiple modal instances

- `toast.test.js` - Tests for toast notification system:
  - `showToast()` - Toast creation, types, icons, messages
  - `dismissToast()` - Toast removal, animations
  - Auto-dismiss functionality - Duration-based dismissal
  - Dismissible toasts - Close button functionality
  - Action buttons - Custom action handling
  - Toast stacking - Multiple toasts display
  - ARIA attributes - Role, aria-live for accessibility

- `realtime.test.js` - Tests for real-time update handling:
  - `connectScanStatusStream()` - EventSource connection, callbacks
  - `disconnectScanStatusStream()` - Connection cleanup
  - `pollScanStatus()` - Polling fallback, status updates
  - `autoUpdateScanStatus()` - UI updates, status changes
  - Error handling - Connection errors, fallback mechanisms
  - Screen reader announcements - Accessibility updates

- `charts.test.js` - Tests for chart rendering:
  - `createScanTrendsChart()` - Line chart creation
  - `createSeverityChart()` - Pie/donut chart creation
  - `createPassFailChart()` - Bar chart creation
  - Chart accessibility - ARIA attributes, role="img"
  - Error handling - Missing canvas elements

- `integration.test.js` - Integration tests for UI pages:
  - Dashboard page (6.7) - Statistics display, charts, empty states
  - Scan list page (6.8) - Table sorting, pagination, filtering
  - Scan detail page (6.9) - Findings display, expand/collapse, bulk selection
  - Scan forms (6.10) - Form validation, submission, error handling
  - Baselines page (6.11) - Baseline list, comparison, deletion, creation

- `accessibility.test.js` - Automated accessibility tests using axe-core
- `accessibility-manual.md` - Manual accessibility testing guide (WAVE, Lighthouse, axe DevTools)
- `keyboard-navigation-test.md` - Comprehensive keyboard navigation testing guide
- `keyboard-navigation-checklist.md` - Quick reference checklist for keyboard testing
- `screen-reader-test.md` - Comprehensive screen reader testing guide (NVDA, JAWS, VoiceOver)
- `screen-reader-checklist.md` - Quick reference checklist for screen reader testing
- `color-contrast-test.md` - Comprehensive color contrast testing guide
- `color-contrast-checklist.md` - Quick reference checklist for color contrast testing
- `color-contrast-values.md` - Reference document with CSS color values and expected contrast ratios
- `responsive-design-test.md` - Comprehensive responsive design testing guide
- `responsive-checklist.md` - Quick reference checklist for responsive design testing
- `realtime-update-test.md` - Comprehensive real-time update functionality testing guide
- `realtime-checklist.md` - Quick reference checklist for real-time update testing
- `export-functionality-test.md` - Comprehensive export functionality testing guide
- `export-checklist.md` - Quick reference checklist for export testing
- `e2e-test-guide.md` - Comprehensive end-to-end testing guide for critical user flows
- `e2e-checklist.md` - Quick reference checklist for end-to-end testing
- `cross-browser-test.md` - Comprehensive cross-browser compatibility testing guide
- `cross-browser-checklist.md` - Quick reference checklist for cross-browser testing

## Test Coverage

### copyToClipboard
- ✅ Modern Clipboard API success
- ✅ Modern Clipboard API error handling
- ✅ Fallback execCommand method
- ✅ Fallback error handling
- ✅ Callback functionality (with and without)
- ✅ Textarea styling for fallback

### showToast fallback
- ✅ Alert fallback when toast system not loaded

### initTooltips
- ✅ Tooltip initialization
- ✅ Mouse events (mouseenter/mouseleave)
- ✅ Keyboard events (focus/blur)
- ✅ Tooltip positioning (top, bottom, left, right)
- ✅ Viewport bounds checking
- ✅ Empty tooltip handling
- ✅ Tooltip removal

## Adding New Tests

To add tests for a new module:

1. Create a new test file: `[module-name].test.js`
2. Follow the same structure as `utils.test.js`
3. Add a test runner section in `test-runner.html` or create a separate runner
4. Use Jasmine's BDD syntax:
   ```javascript
   describe('Module Name', function() {
     beforeEach(function() {
       // Setup
     });
     
     it('should do something', function() {
       // Test
     });
   });
   ```

## Dependencies

- **Jasmine 5.1.1** - Loaded via CDN in test-runner.html
- **axe-core 4.8.0** - Loaded via CDN for accessibility testing
- No build step required - tests run directly in the browser

## Accessibility Testing

### Automated Tests (axe-core)

The `accessibility.test.js` file contains automated accessibility tests using axe-core. These tests check for:
- Semantic HTML structure
- Form accessibility (labels, ARIA attributes)
- Interactive elements (buttons, links, modals)
- Images and icons (alt text, aria-hidden)
- Tables (headers, scope attributes)
- Color contrast (WCAG AA)
- ARIA live regions
- Skip links
- Landmarks

### Manual Testing Tools

See `accessibility-manual.md` for detailed instructions on using:
- **axe DevTools** - Browser extension for accessibility testing
- **WAVE** - Web Accessibility Evaluation Tool (browser extension and online)
- **Lighthouse** - Built into Chrome DevTools

### Running Accessibility Tests

1. **Automated (axe-core)**:
   - Open `test-runner.html` in a browser
   - Accessibility tests run automatically
   - Review violations in test results

2. **Manual (Browser Extensions)**:
   - Install WAVE or axe DevTools extension
   - Navigate to any page
   - Run the extension
   - Review and fix issues

3. **Lighthouse**:
   - Open Chrome DevTools
   - Go to Lighthouse tab
   - Select "Accessibility" category
   - Click "Analyze page load"

## Notes

- Tests use Jasmine spies for mocking
- DOM manipulation is tested with actual DOM elements
- Async operations use `setTimeout` for testing
- Tests clean up after themselves in `afterEach` hooks

