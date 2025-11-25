# Manual Accessibility Testing Guide

This document provides instructions for manual accessibility testing using browser-based tools like WAVE and Lighthouse.

## Tools Overview

### 1. axe DevTools (Browser Extension)
- **Chrome**: [axe DevTools Extension](https://chrome.google.com/webstore/detail/axe-devtools-web-accessibility/lhdoppojpmngadmnindnejefpokejbdd)
- **Firefox**: [axe DevTools Extension](https://addons.mozilla.org/en-US/firefox/addon/axe-devtools/)
- **Edge**: Available in Edge DevTools (built-in)

### 2. WAVE (Web Accessibility Evaluation Tool)
- **Browser Extension**: [WAVE Extension](https://wave.webaim.org/extension/)
- **Online Tool**: [WAVE Web Accessibility Evaluator](https://wave.webaim.org/)

### 3. Lighthouse (Built into Chrome DevTools)
- Available in Chrome DevTools → Lighthouse tab
- Can also be run via command line

## Testing Checklist

### Page-by-Page Testing

#### 1. Dashboard Page (`/`)
- [ ] Run axe DevTools scan
- [ ] Run WAVE evaluation
- [ ] Run Lighthouse accessibility audit
- [ ] Check for:
  - Proper heading hierarchy (h1 → h2 → h3)
  - All images have alt text
  - All interactive elements are keyboard accessible
  - Color contrast meets WCAG AA (4.5:1 for normal text, 3:1 for large text)
  - Charts have ARIA labels
  - Statistics cards are properly labeled

#### 2. Scan List Page (`/`)
- [ ] Run automated tools
- [ ] Check for:
  - Table headers with scope attributes
  - Sortable columns have proper ARIA labels
  - Pagination is keyboard accessible
  - Filter form has proper labels
  - Empty state is announced to screen readers

#### 3. Scan Detail Page (`/scan/{id}`)
- [ ] Run automated tools
- [ ] Check for:
  - Findings table accessibility
  - Expand/collapse functionality is keyboard accessible
  - Bulk selection has proper ARIA labels
  - Action buttons have descriptive labels
  - Status badges are properly announced

#### 4. Scan Forms (`/ui/scan`)
- [ ] Run automated tools
- [ ] Check for:
  - All form fields have associated labels
  - Required fields have aria-required
  - Error messages are associated with inputs (aria-describedby)
  - Form validation is announced to screen readers
  - Tab order is logical

#### 5. Baselines Page (`/baselines`)
- [ ] Run automated tools
- [ ] Check for:
  - Table accessibility
  - Comparison form has proper labels
  - Delete confirmation dialog is accessible

#### 6. Baseline Comparison Page (`/baseline/compare`)
- [ ] Run automated tools
- [ ] Check for:
  - Diff display is accessible
  - JSON viewer is keyboard navigable
  - Search functionality has proper labels

#### 7. Login Page (`/login`)
- [ ] Run automated tools
- [ ] Check for:
  - Form accessibility
  - Error messages are properly announced
  - Password toggle button has aria-label

## Running Tests

### Using axe DevTools Extension

1. Install the extension in your browser
2. Navigate to the page you want to test
3. Open DevTools (F12)
4. Click on the "axe DevTools" tab
5. Click "Scan ALL of my page"
6. Review violations and warnings
7. Fix issues and re-scan

### Using WAVE Extension

1. Install the WAVE extension
2. Navigate to the page you want to test
3. Click the WAVE icon in your browser toolbar
4. Review the sidebar for:
   - Errors (red icons)
   - Alerts (orange icons)
   - Features (green icons)
   - Structural elements (blue icons)
   - ARIA labels (purple icons)
5. Click on icons to see details
6. Fix issues and re-evaluate

### Using WAVE Online Tool

1. Go to https://wave.webaim.org/
2. Enter the URL of your page (or use the browser extension)
3. Review the evaluation results
4. Check the "Details" tab for specific issues
5. Review the "Structure" tab for semantic HTML

### Using Lighthouse

1. Open Chrome DevTools (F12)
2. Navigate to the "Lighthouse" tab
3. Select "Accessibility" category
4. Choose "Desktop" or "Mobile"
5. Click "Analyze page load"
6. Review the accessibility score and issues
7. Click on issues to see details and fixes

### Using Command Line (Lighthouse)

```bash
# Install Lighthouse globally
npm install -g lighthouse

# Run accessibility audit
lighthouse http://localhost:8000/ --only-categories=accessibility --output=html --output-path=./lighthouse-report.html

# View report
open lighthouse-report.html
```

## Common Issues to Check

### 1. Color Contrast
- **Tool**: WAVE, Lighthouse, axe DevTools
- **Check**: All text meets WCAG AA contrast ratios
- **Fix**: Adjust colors in CSS variables

### 2. Missing Alt Text
- **Tool**: All tools
- **Check**: All images have alt attributes
- **Fix**: Add alt text or aria-hidden="true" for decorative images

### 3. Missing Labels
- **Tool**: All tools
- **Check**: All form inputs have associated labels
- **Fix**: Add `<label>` elements with `for` attributes

### 4. Keyboard Navigation
- **Tool**: Manual testing + axe DevTools
- **Check**: All interactive elements are keyboard accessible
- **Fix**: Add tabindex, ensure focus indicators are visible

### 5. ARIA Attributes
- **Tool**: WAVE, axe DevTools
- **Check**: Proper use of ARIA labels, roles, and properties
- **Fix**: Add appropriate ARIA attributes

### 6. Heading Hierarchy
- **Tool**: WAVE, axe DevTools
- **Check**: Headings follow logical order (h1 → h2 → h3)
- **Fix**: Restructure heading hierarchy

### 7. Focus Management
- **Tool**: Manual testing
- **Check**: Focus is visible and logical
- **Fix**: Add focus styles, manage focus in modals

## Automated Testing Script

The `accessibility.test.js` file uses axe-core to run automated accessibility tests. To run:

1. Open `test-runner.html` in a browser
2. The accessibility tests will run automatically
3. Review any violations reported

## Reporting Issues

When accessibility issues are found:

1. Document the issue with:
   - Page URL
   - Tool used
   - Issue description
   - WCAG guideline violated
   - Suggested fix

2. Prioritize fixes:
   - **Critical**: Blocks users from accessing content
   - **High**: Significantly impacts usability
   - **Medium**: Minor usability impact
   - **Low**: Best practice improvements

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [axe-core Documentation](https://github.com/dequelabs/axe-core)
- [WAVE Documentation](https://wave.webaim.org/api/)
- [Lighthouse Accessibility](https://developers.google.com/web/tools/lighthouse#accessibility)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

