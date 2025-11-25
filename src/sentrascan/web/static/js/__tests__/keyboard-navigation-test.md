# Manual Keyboard Navigation Testing Guide

This document provides a comprehensive checklist for manual keyboard navigation testing to ensure WCAG 2.1 AA compliance.

## Testing Environment Setup

### Prerequisites
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **No Mouse**: Disconnect or disable mouse/trackpad during testing
- **Screen Reader** (optional): NVDA (Windows), JAWS (Windows), or VoiceOver (macOS/iOS) for additional validation

### Keyboard Shortcuts Reference
- **Tab**: Move forward through focusable elements
- **Shift + Tab**: Move backward through focusable elements
- **Enter/Space**: Activate buttons, links, form controls
- **Arrow Keys**: Navigate within components (menus, tabs, dropdowns)
- **Escape**: Close modals, dropdowns, cancel actions
- **Home/End**: Navigate to first/last item in lists
- **Page Up/Down**: Scroll page content

## General Keyboard Navigation Checklist

### ✅ Tab Order
- [ ] Tab order follows visual reading order (left-to-right, top-to-bottom)
- [ ] No elements are skipped in tab order
- [ ] No elements appear twice in tab order
- [ ] Hidden elements are not in tab order (tabindex="-1" or display:none)
- [ ] Focus moves logically through page sections

### ✅ Focus Indicators
- [ ] All focusable elements have visible focus indicators
- [ ] Focus indicators are clearly visible (2px+ outline)
- [ ] Focus indicators have sufficient contrast (3:1 minimum)
- [ ] Focus indicators don't obscure content
- [ ] Custom focus styles match or exceed default browser styles

### ✅ Focus Management
- [ ] Focus is trapped within modals/dialogs
- [ ] Focus returns to trigger element when modal closes
- [ ] Focus moves to new content when dynamically loaded
- [ ] Focus doesn't jump unexpectedly
- [ ] Focus is visible at all times

## Page-Specific Testing

### 1. Login Page (`/login`)

#### Tab Order Test
1. [ ] Tab to API Key input field
2. [ ] Tab to password toggle button
3. [ ] Tab to Sign In button
4. [ ] Verify order is logical

#### Form Interaction
- [ ] Can type in API Key field with keyboard
- [ ] Can toggle password visibility with Enter/Space
- [ ] Can submit form with Enter key
- [ ] Error messages are announced to screen readers
- [ ] Focus moves to error field when validation fails

#### Keyboard Shortcuts
- [ ] Enter key submits form
- [ ] Escape key (if applicable) cancels or clears

**Expected Tab Order:**
1. API Key input
2. Password toggle button
3. Sign In button

---

### 2. Dashboard Page (`/`)

#### Tab Order Test
1. [ ] Tab to navigation menu items
2. [ ] Tab to filter controls
3. [ ] Tab to chart elements (if interactive)
4. [ ] Tab to table headers (if sortable)
5. [ ] Tab to table rows/links
6. [ ] Tab to pagination controls
7. [ ] Tab to footer links

#### Interactive Elements
- [ ] Can navigate filter dropdowns with arrow keys
- [ ] Can activate filter buttons with Enter/Space
- [ ] Can sort table columns with Enter/Space
- [ ] Can navigate pagination with keyboard
- [ ] Can interact with charts (if keyboard accessible)

#### Skip Links
- [ ] Skip link appears on first Tab
- [ ] Skip link moves focus to main content
- [ ] Skip link is visible when focused

**Expected Tab Order:**
1. Skip link (if present)
2. Navigation menu
3. Filter controls
4. Chart controls (if any)
5. Table headers
6. Table rows/actions
7. Pagination
8. Footer

---

### 3. Scan List Page (`/`)

#### Tab Order Test
1. [ ] Tab to "Run New Scan" button
2. [ ] Tab to filter controls (type, status, time range)
3. [ ] Tab to date pickers
4. [ ] Tab to search input
5. [ ] Tab to "Clear Filters" button
6. [ ] Tab to table headers (sortable)
7. [ ] Tab to table rows
8. [ ] Tab to action links in rows
9. [ ] Tab to pagination controls

#### Table Navigation
- [ ] Can sort columns with Enter/Space on header
- [ ] Can navigate table rows with Tab
- [ ] Can activate row links with Enter
- [ ] Can navigate pagination with Tab
- [ ] Can change page size with keyboard

#### Filter Controls
- [ ] Can open dropdowns with Enter/Space
- [ ] Can navigate dropdown options with arrow keys
- [ ] Can select options with Enter
- [ ] Can close dropdowns with Escape
- [ ] Can navigate date pickers with keyboard
- [ ] Can type in search input

**Expected Tab Order:**
1. Page header
2. "Run New Scan" button
3. Filter section controls
4. Table headers
5. Table rows (each row's interactive elements)
6. Pagination controls

---

### 4. Scan Detail Page (`/scan/{id}`)

#### Tab Order Test
1. [ ] Tab to breadcrumb navigation
2. [ ] Tab to action buttons (Download, Export, Compare Baseline)
3. [ ] Tab to findings filter controls
4. [ ] Tab to findings group headers (expandable)
5. [ ] Tab to findings table headers
6. [ ] Tab to findings checkboxes
7. [ ] Tab to finding toggle buttons
8. [ ] Tab to action buttons in findings
9. [ ] Tab to bulk actions (when visible)

#### Findings Interaction
- [ ] Can expand/collapse finding groups with Enter/Space
- [ ] Can navigate findings table with Tab
- [ ] Can select findings with Space on checkbox
- [ ] Can expand finding details with Enter/Space
- [ ] Can copy finding data with Enter/Space
- [ ] Can use bulk actions with keyboard

#### Modal/Dialog
- [ ] Can open "Create Baseline" modal with keyboard
- [ ] Focus is trapped in modal
- [ ] Can navigate modal form fields with Tab
- [ ] Can submit/cancel modal with keyboard
- [ ] Focus returns to trigger when modal closes

**Expected Tab Order:**
1. Breadcrumb
2. Action buttons
3. Findings filters
4. Findings group headers
5. Findings table (checkboxes, toggles, actions)
6. Bulk actions (when visible)

---

### 5. Scan Forms (`/ui/scan`)

#### Tab Order Test
1. [ ] Tab to tab buttons (Model Scan / MCP Scan)
2. [ ] Tab to form fields in order
3. [ ] Tab to checkboxes
4. [ ] Tab to "Advanced" expandable sections
5. [ ] Tab to submit button
6. [ ] Tab to Cancel link

#### Form Navigation
- [ ] Can switch tabs with arrow keys or Tab + Enter
- [ ] Can navigate all form fields with Tab
- [ ] Can check/uncheck checkboxes with Space
- [ ] Can expand/collapse advanced sections with Enter/Space
- [ ] Can submit form with Enter on submit button
- [ ] Can cancel with Escape or Tab to Cancel link

#### Validation
- [ ] Focus moves to first invalid field on submit
- [ ] Error messages are announced
- [ ] Can navigate to error messages with Tab
- [ ] Can correct errors and resubmit

**Expected Tab Order:**
1. Tab buttons
2. Form fields (in logical order)
3. Checkboxes
4. Advanced section toggle
5. Advanced fields (when expanded)
6. Submit button
7. Cancel link

---

### 6. Baselines Page (`/baselines`)

#### Tab Order Test
1. [ ] Tab to "Create Baseline" button
2. [ ] Tab to comparison form controls
3. [ ] Tab to table headers
4. [ ] Tab to table rows
5. [ ] Tab to action buttons (View, Compare, Delete)

#### Comparison Form
- [ ] Can navigate select dropdowns with keyboard
- [ ] Can select baselines with arrow keys + Enter
- [ ] Can submit comparison with Enter
- [ ] Can navigate form fields with Tab

#### Table Actions
- [ ] Can activate "View" with Enter
- [ ] Can activate "Compare" with Enter
- [ ] Can activate "Delete" with Enter (opens confirmation)
- [ ] Can navigate confirmation dialog with keyboard

**Expected Tab Order:**
1. Create Baseline button
2. Comparison form
3. Table headers
4. Table rows and actions

---

### 7. Baseline Comparison Page (`/baseline/compare`)

#### Tab Order Test
1. [ ] Tab to navigation controls
2. [ ] Tab to search input
3. [ ] Tab to filter controls
4. [ ] Tab to diff items (if interactive)
5. [ ] Tab to expand/collapse buttons
6. [ ] Tab to copy buttons
7. [ ] Tab to export button

#### Diff Navigation
- [ ] Can navigate diff items with Tab
- [ ] Can expand/collapse sections with Enter/Space
- [ ] Can search with keyboard
- [ ] Can filter with keyboard
- [ ] Can copy JSON with keyboard
- [ ] Can export with keyboard

**Expected Tab Order:**
1. Page header
2. Search input
3. Filter controls
4. Diff items and controls
5. Export button

---

## Component-Specific Testing

### Modals/Dialogs

#### Focus Trap
- [ ] Focus cannot escape modal with Tab
- [ ] Focus wraps from last to first element
- [ ] Focus wraps from first to last element with Shift+Tab
- [ ] Focus stays within modal boundaries

#### Modal Controls
- [ ] Can close modal with Escape key
- [ ] Can navigate all modal elements with Tab
- [ ] Can submit/cancel with keyboard
- [ ] Focus returns to trigger element on close

### Dropdowns/Menus

#### Navigation
- [ ] Can open dropdown with Enter/Space
- [ ] Can navigate options with arrow keys
- [ ] Can select option with Enter
- [ ] Can close dropdown with Escape
- [ ] Focus returns to trigger on close

### Tabs

#### Tab Navigation
- [ ] Can navigate tabs with arrow keys (left/right)
- [ ] Can activate tab with Enter/Space
- [ ] Focus moves to tab panel content
- [ ] Tab panel is keyboard accessible

### Tables

#### Table Navigation
- [ ] Can navigate cells with Tab
- [ ] Can sort columns with Enter/Space on header
- [ ] Can activate row links with Enter
- [ ] Can navigate pagination with Tab
- [ ] Can change page size with keyboard

### Tooltips

#### Tooltip Accessibility
- [ ] Tooltips appear on focus (not just hover)
- [ ] Tooltip content is accessible to screen readers
- [ ] Can dismiss tooltip with Escape (if applicable)

## Keyboard Shortcuts Testing

### Global Shortcuts
- [ ] **Tab**: Moves focus forward
- [ ] **Shift+Tab**: Moves focus backward
- [ ] **Enter**: Activates buttons, submits forms
- [ ] **Space**: Activates buttons, toggles checkboxes
- [ ] **Escape**: Closes modals, cancels actions
- [ ] **Arrow Keys**: Navigate within components

### Component Shortcuts
- [ ] **Dropdowns**: Arrow keys navigate, Enter selects, Escape closes
- [ ] **Tabs**: Arrow keys navigate, Enter activates
- [ ] **Modals**: Escape closes, Tab cycles through elements
- [ ] **Tables**: Tab navigates, Enter sorts/activates

## Screen Reader Testing (Optional but Recommended)

### NVDA (Windows)
1. Download and install NVDA
2. Start NVDA (Insert+Z)
3. Navigate pages with Tab
4. Verify all content is announced
5. Verify form labels are announced
6. Verify button purposes are clear

### VoiceOver (macOS)
1. Enable VoiceOver (Cmd+F5)
2. Navigate with VO+Arrow keys
3. Verify content announcements
4. Verify form interactions

### JAWS (Windows)
1. Start JAWS
2. Navigate with Tab
3. Verify announcements
4. Test form interactions

## Common Issues to Check

### ❌ Problems to Identify

1. **Focus Trap Issues**
   - Focus escapes modal
   - Focus jumps unexpectedly
   - Focus disappears

2. **Tab Order Issues**
   - Elements skipped
   - Elements appear twice
   - Order doesn't match visual layout

3. **Focus Indicator Issues**
   - No visible focus indicator
   - Focus indicator too subtle
   - Focus indicator obscures content

4. **Keyboard Shortcut Issues**
   - Shortcuts don't work
   - Shortcuts conflict with browser
   - No keyboard alternative to mouse actions

5. **Component Issues**
   - Dropdowns don't open with keyboard
   - Tabs don't switch with keyboard
   - Modals can't be closed with Escape

## Test Results Template

### Page: [Page Name]
**Date**: [Date]
**Tester**: [Name]
**Browser**: [Browser/Version]

#### Tab Order
- ✅ Pass / ❌ Fail
- **Issues Found**: [List issues]

#### Focus Indicators
- ✅ Pass / ❌ Fail
- **Issues Found**: [List issues]

#### Keyboard Shortcuts
- ✅ Pass / ❌ Fail
- **Issues Found**: [List issues]

#### Component Accessibility
- ✅ Pass / ❌ Fail
- **Issues Found**: [List issues]

#### Overall Assessment
- **Status**: ✅ Pass / ❌ Fail / ⚠️ Needs Improvement
- **Priority Issues**: [List critical issues]
- **Recommendations**: [Suggestions for improvement]

## Reporting Issues

When keyboard navigation issues are found:

1. **Document the Issue**:
   - Page URL
   - Element/component affected
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Browser/OS combination

2. **Priority Level**:
   - **Critical**: Blocks keyboard users completely
   - **High**: Significantly impacts usability
   - **Medium**: Minor usability impact
   - **Low**: Enhancement opportunity

3. **Fix Recommendations**:
   - Specific code changes needed
   - ARIA attributes to add
   - Focus management improvements
   - Keyboard event handlers needed

## Resources

- [WCAG 2.1 Keyboard Accessible](https://www.w3.org/WAI/WCAG21/Understanding/keyboard.html)
- [WebAIM Keyboard Accessibility](https://webaim.org/techniques/keyboard/)
- [MDN Keyboard Navigation](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Keyboard-navigable_JavaScript_widgets)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)

