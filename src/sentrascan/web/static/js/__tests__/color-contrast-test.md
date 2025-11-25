# Color Contrast Testing Guide

This document provides comprehensive instructions for testing color contrast ratios to ensure WCAG 2.1 AA compliance.

## WCAG 2.1 AA Requirements

### Contrast Ratios
- **Normal Text** (smaller than 18pt/24px): **4.5:1** minimum
- **Large Text** (18pt/24px or larger, or 14pt/18.67px bold): **3:1** minimum
- **UI Components** (buttons, form controls): **3:1** minimum
- **Graphical Objects** (icons, charts): **3:1** minimum

### Text Size Reference
- **Normal Text**: < 18pt (24px) regular weight, or < 14pt (18.67px) bold
- **Large Text**: ≥ 18pt (24px) regular weight, or ≥ 14pt (18.67px) bold

## Testing Tools

### 1. WebAIM Contrast Checker
- **URL**: https://webaim.org/resources/contrastchecker/
- **Usage**: Enter foreground and background colors (hex, RGB, or named)
- **Features**: Shows ratio, passes/fails WCAG AA and AAA
- **Best for**: Quick checks of specific color combinations

### 2. Colour Contrast Analyser (CCA)
- **Platform**: Windows, macOS, Linux
- **Download**: https://www.tpgi.com/color-contrast-checker/
- **Features**: Eye dropper tool, real-time checking, multiple standards
- **Best for**: Testing actual rendered pages

### 3. axe DevTools
- **Browser Extension**: Available for Chrome, Firefox, Edge
- **Features**: Automated contrast checking on entire pages
- **Best for**: Comprehensive page scans

### 4. WAVE
- **Browser Extension**: Available for Chrome, Firefox, Edge
- **Features**: Highlights contrast issues on page
- **Best for**: Visual identification of contrast problems

### 5. Lighthouse
- **Built into Chrome DevTools**
- **Features**: Accessibility audit includes contrast checking
- **Best for**: Automated audits with scores

### 6. Browser DevTools
- **Chrome/Firefox**: Inspect element → Computed styles → Check contrast
- **Features**: Shows computed colors, can test different combinations
- **Best for**: Developer debugging

## Testing Procedure

### Step 1: Identify Text Elements

Test the following text elements on each page:

1. **Body Text**
   - Paragraphs
   - List items
   - Table cell text
   - Form labels

2. **Headings**
   - H1, H2, H3, H4, H5, H6
   - Check both normal and large sizes

3. **Links**
   - Default link color
   - Visited link color
   - Hover state
   - Focus state

4. **Buttons**
   - Button text
   - Button text on hover
   - Button text on focus
   - Disabled button text

5. **Form Elements**
   - Input text
   - Placeholder text
   - Error messages
   - Help text

6. **Status Indicators**
   - Badge text
   - Status messages
   - Toast notifications
   - Alert messages

### Step 2: Test Each Element

For each text element:

1. **Identify Colors**:
   - Use browser DevTools to inspect element
   - Note foreground color (text)
   - Note background color
   - Check computed styles for actual colors

2. **Check Contrast**:
   - Use WebAIM Contrast Checker or CCA
   - Enter foreground and background colors
   - Verify ratio meets requirements

3. **Document Results**:
   - Record element, colors, ratio, pass/fail
   - Note if it's normal or large text
   - Document any failures

## Page-Specific Testing

### 1. Login Page (`/login`)

#### Elements to Test
- [ ] Page title (h1) - "Welcome Back"
- [ ] Subtitle text
- [ ] Form label "API Key"
- [ ] Input text
- [ ] Placeholder text
- [ ] Help text
- [ ] Error message text
- [ ] "Sign In" button text
- [ ] Footer text
- [ ] Links

#### Expected Contrast Ratios
- **Headings**: ≥ 3:1 (large text)
- **Body text**: ≥ 4.5:1
- **Button text**: ≥ 4.5:1
- **Error text**: ≥ 4.5:1

---

### 2. Dashboard Page (`/`)

#### Elements to Test
- [ ] Page heading
- [ ] Stat card values
- [ ] Stat card labels
- [ ] Chart labels
- [ ] Chart legends
- [ ] Table headers
- [ ] Table cell text
- [ ] Link text
- [ ] Badge text (status badges)
- [ ] Filter labels
- [ ] Button text

#### Expected Contrast Ratios
- **Stat values**: ≥ 4.5:1 (if normal) or ≥ 3:1 (if large)
- **Chart text**: ≥ 4.5:1
- **Table text**: ≥ 4.5:1
- **Badge text**: ≥ 4.5:1

---

### 3. Scan List Page (`/`)

#### Elements to Test
- [ ] Page heading
- [ ] Filter labels
- [ ] Select dropdown text
- [ ] Input text
- [ ] Table headers
- [ ] Table cell text
- [ ] Status badge text
- [ ] Link text
- [ ] Pagination text
- [ ] Button text

#### Expected Contrast Ratios
- **All text**: ≥ 4.5:1 (normal) or ≥ 3:1 (large)
- **Badge text on colored backgrounds**: ≥ 4.5:1

---

### 4. Scan Detail Page (`/scan/{id}`)

#### Elements to Test
- [ ] Page heading
- [ ] Status badge text
- [ ] Findings group headers
- [ ] Finding count text
- [ ] Table headers
- [ ] Finding titles
- [ ] Finding descriptions
- [ ] Button text
- [ ] Badge text (severity badges)
- [ ] Modal text (if applicable)

#### Expected Contrast Ratios
- **Severity badges**: 
  - Critical: Text on red background ≥ 4.5:1
  - High: Text on orange background ≥ 4.5:1
  - Medium: Text on yellow background ≥ 4.5:1
  - Low: Text on blue background ≥ 4.5:1

---

### 5. Scan Forms (`/ui/scan`)

#### Elements to Test
- [ ] Tab button text
- [ ] Active tab text
- [ ] Form labels
- [ ] Input text
- [ ] Placeholder text
- [ ] Help text
- [ ] Error messages
- [ ] Checkbox labels
- [ ] Button text
- [ ] Section headings

#### Expected Contrast Ratios
- **All form text**: ≥ 4.5:1
- **Error messages**: ≥ 4.5:1 (often on colored background)

---

### 6. Baselines Page (`/baselines`)

#### Elements to Test
- [ ] Page heading
- [ ] Form labels
- [ ] Table headers
- [ ] Table cell text
- [ ] Badge text
- [ ] Button text
- [ ] Link text

#### Expected Contrast Ratios
- **All text**: ≥ 4.5:1 (normal) or ≥ 3:1 (large)

---

### 7. Baseline Comparison Page (`/baseline/compare`)

#### Elements to Test
- [ ] Page heading
- [ ] Search input text
- [ ] Filter labels
- [ ] Diff item text
- [ ] JSON syntax highlighting
- [ ] Button text
- [ ] Link text

#### Expected Contrast Ratios
- **All text**: ≥ 4.5:1
- **JSON syntax colors**: ≥ 4.5:1 against background

## Component-Specific Testing

### Buttons

#### Test States
- [ ] Default state text
- [ ] Hover state text
- [ ] Focus state text
- [ ] Active/pressed state text
- [ ] Disabled state text

#### Expected Ratios
- **All states**: ≥ 4.5:1
- **Disabled**: ≥ 4.5:1 (may be lower opacity, but still must meet ratio)

### Badges

#### Test Each Badge Type
- [ ] Success badge (green background)
- [ ] Error badge (red background)
- [ ] Warning badge (yellow/orange background)
- [ ] Info badge (blue background)
- [ ] Neutral badge (gray background)

#### Expected Ratios
- **All badge text**: ≥ 4.5:1 against badge background

### Links

#### Test States
- [ ] Default link color
- [ ] Visited link color
- [ ] Hover state
- [ ] Focus state
- [ ] Active state

#### Expected Ratios
- **All states**: ≥ 4.5:1

### Form Elements

#### Input Fields
- [ ] Input text
- [ ] Placeholder text
- [ ] Label text
- [ ] Help text
- [ ] Error message text

#### Expected Ratios
- **Input text**: ≥ 4.5:1
- **Placeholder**: ≥ 4.5:1 (or clearly distinguishable)
- **Labels**: ≥ 4.5:1
- **Help text**: ≥ 4.5:1
- **Error text**: ≥ 4.5:1

### Status Messages

#### Test Types
- [ ] Success messages
- [ ] Error messages
- [ ] Warning messages
- [ ] Info messages

#### Expected Ratios
- **All message text**: ≥ 4.5:1 against message background

## Using Testing Tools

### WebAIM Contrast Checker

1. **Navigate to**: https://webaim.org/resources/contrastchecker/
2. **Enter Colors**:
   - Foreground color (text)
   - Background color
3. **Check Results**:
   - Ratio displayed
   - Pass/fail for WCAG AA
   - Pass/fail for WCAG AAA
4. **Adjust if Needed**:
   - Try different shades
   - Test until ratio passes

### Colour Contrast Analyser (CCA)

1. **Install CCA**
2. **Open Application**
3. **Use Eye Dropper**:
   - Click foreground color picker
   - Click on text in browser
   - Click background color picker
   - Click on background in browser
4. **Review Results**:
   - Ratio displayed
   - Pass/fail indicators
   - Visual preview

### axe DevTools

1. **Install Extension**
2. **Open Page**
3. **Run Scan**:
   - Open DevTools
   - Go to axe DevTools tab
   - Click "Scan ALL of my page"
4. **Review Contrast Issues**:
   - Look for "color-contrast" violations
   - Click to see element details
   - Note required ratio vs actual ratio

### WAVE

1. **Install Extension**
2. **Open Page**
3. **Run WAVE**:
   - Click WAVE icon
   - Review sidebar
4. **Check Contrast**:
   - Look for contrast errors (red icons)
   - Click to see details
   - Note element and colors

### Lighthouse

1. **Open Chrome DevTools**
2. **Go to Lighthouse Tab**
3. **Run Audit**:
   - Select "Accessibility"
   - Click "Analyze page load"
4. **Review Contrast Issues**:
   - Check "Contrast" section
   - Review failing elements
   - Note required improvements

## Common Issues and Fixes

### Issue: Text Too Light on Background
**Problem**: Ratio below 4.5:1 for normal text
**Fix**: Darken text color or lighten background

### Issue: Placeholder Text Too Light
**Problem**: Placeholder doesn't meet contrast
**Fix**: Increase placeholder opacity or use darker color

### Issue: Disabled Button Text
**Problem**: Disabled state doesn't meet contrast
**Fix**: Ensure disabled text still meets 4.5:1 (may need darker text)

### Issue: Badge Text on Colored Background
**Problem**: Text on colored badge doesn't meet contrast
**Fix**: Adjust text color or badge background color

### Issue: Link Hover State
**Problem**: Hover color doesn't meet contrast
**Fix**: Ensure hover state maintains 4.5:1 ratio

### Issue: Focus Indicators
**Problem**: Focus outline doesn't meet contrast
**Fix**: Ensure focus outline is 3:1 against adjacent colors

## Test Results Template

### Page: [Page Name]
**Date**: [Date]
**Tester**: [Name]
**Tool Used**: [Tool Name]

#### Text Elements Tested

| Element | Foreground | Background | Ratio | Required | Status | Notes |
|---------|-----------|-----------|-------|----------|--------|-------|
| Heading 1 | #333 | #FFF | 12.6:1 | 3:1 | ✅ Pass | Large text |
| Body text | #666 | #FFF | 5.7:1 | 4.5:1 | ✅ Pass | Normal text |
| Link text | #2196F3 | #FFF | 4.5:1 | 4.5:1 | ✅ Pass | Meets minimum |
| Button text | #FFF | #2196F3 | 4.5:1 | 4.5:1 | ✅ Pass | Primary button |
| Error text | #D32F2F | #FFF | 5.1:1 | 4.5:1 | ✅ Pass | Error message |
| Badge text | #FFF | #4CAF50 | 4.5:1 | 4.5:1 | ✅ Pass | Success badge |

#### Issues Found
1. [Issue description]
2. [Issue description]

#### Recommendations
1. [Recommendation]
2. [Recommendation]

## Automated Testing

### Using axe-core (in accessibility.test.js)

The accessibility tests include color contrast checking. Run the tests to get automated contrast validation.

### CSS Variables to Check

Review these CSS variables in `main.css`:

```css
--color-text-primary: var(--color-gray-800);      /* Check against backgrounds */
--color-text-secondary: var(--color-text-secondary); /* Check against backgrounds */
--color-primary: #2196F3;                        /* Check text on this */
--color-success: #4CAF50;                        /* Check text on this */
--color-error: #F44336;                          /* Check text on this */
--color-warning: #FF9800;                        /* Check text on this */
```

## Resources

- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [WCAG 2.1 Contrast Requirements](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [Colour Contrast Analyser](https://www.tpgi.com/color-contrast-checker/)
- [Contrast Ratio Calculator](https://contrast-ratio.com/)
- [WebAIM Contrast Article](https://webaim.org/articles/contrast/)

