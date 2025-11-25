# Keyboard Navigation Testing Checklist

Quick reference checklist for keyboard navigation testing.

## Quick Test Procedure

1. **Disable Mouse**: Unplug or disable mouse/trackpad
2. **Open Page**: Navigate to page in browser
3. **Press Tab**: Start tabbing through page
4. **Document Issues**: Note any problems

## Essential Checks (Every Page)

- [ ] Can navigate entire page with Tab key only
- [ ] All interactive elements receive focus
- [ ] Focus indicator is clearly visible
- [ ] Tab order follows logical reading order
- [ ] No keyboard traps (can't escape with Tab)
- [ ] All actions can be performed with keyboard
- [ ] Escape key closes modals/dropdowns
- [ ] Enter/Space activates buttons and links

## Page-Specific Quick Checks

### Login Page
- [ ] Tab to input field
- [ ] Type with keyboard
- [ ] Tab to submit button
- [ ] Submit with Enter

### Dashboard
- [ ] Tab through navigation
- [ ] Tab through filters
- [ ] Tab through table
- [ ] Tab through pagination

### Scan List
- [ ] Tab through filters
- [ ] Open dropdowns with Enter
- [ ] Navigate dropdowns with arrows
- [ ] Sort table with Enter on header
- [ ] Navigate table rows

### Scan Detail
- [ ] Tab through action buttons
- [ ] Expand findings groups with Enter
- [ ] Navigate findings table
- [ ] Open modal with keyboard
- [ ] Navigate modal form

### Scan Forms
- [ ] Switch tabs with keyboard
- [ ] Tab through all form fields
- [ ] Toggle checkboxes with Space
- [ ] Expand advanced sections
- [ ] Submit form

### Baselines
- [ ] Navigate comparison form
- [ ] Navigate table
- [ ] Open comparison dialog
- [ ] Delete with confirmation

## Component Checks

### Modals
- [ ] Focus trapped in modal
- [ ] Can close with Escape
- [ ] Can navigate all elements
- [ ] Focus returns on close

### Dropdowns
- [ ] Open with Enter/Space
- [ ] Navigate with arrows
- [ ] Select with Enter
- [ ] Close with Escape

### Tables
- [ ] Navigate with Tab
- [ ] Sort with Enter on header
- [ ] Activate links with Enter

### Forms
- [ ] All fields accessible
- [ ] Labels associated
- [ ] Errors announced
- [ ] Can submit with Enter

## Critical Issues (Must Fix)

- [ ] Elements not reachable with keyboard
- [ ] Focus disappears
- [ ] Keyboard traps
- [ ] No focus indicators
- [ ] Actions require mouse
- [ ] Tab order illogical

## Test Results

**Page**: _________________
**Date**: _________________
**Tester**: _________________
**Browser**: _________________

**Status**: ✅ Pass / ❌ Fail

**Issues**:
1. 
2. 
3. 

