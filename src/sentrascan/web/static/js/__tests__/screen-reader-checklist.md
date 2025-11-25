# Screen Reader Testing Quick Checklist

Quick reference for screen reader testing.

## Quick Test Setup

1. **Start Screen Reader**
   - NVDA: Insert+Q
   - JAWS: Insert+J
   - VoiceOver: Cmd+F5

2. **Open Browser**
   - Navigate to page
   - Listen to page title

3. **Test Navigation**
   - Press H to navigate headings
   - Press K to navigate links
   - Press B to navigate buttons
   - Press F to navigate form fields

## Essential Checks (Every Page)

- [ ] Page title is announced
- [ ] Main heading (h1) is announced
- [ ] All headings are announced in order
- [ ] Navigation menu is announced
- [ ] Links are clearly identified
- [ ] Buttons are identified as buttons
- [ ] Form fields have labels announced
- [ ] Images have alt text or are hidden
- [ ] Tables are identified with headers
- [ ] Status updates are announced

## Page-Specific Quick Checks

### Login Page
- [ ] "API Key" label announced with input
- [ ] "Required" is announced
- [ ] Password toggle button purpose is clear
- [ ] "Sign In" button is identified
- [ ] Error messages are announced

### Dashboard
- [ ] Statistics are announced with values
- [ ] Charts have descriptive labels
- [ ] Table headers are announced
- [ ] Links are identified

### Scan List
- [ ] Filter labels are announced
- [ ] Table caption is announced
- [ ] Column headers are announced
- [ ] Row data has context
- [ ] Pagination is announced

### Scan Detail
- [ ] Findings groups are announced
- [ ] Finding counts are announced
- [ ] Expand/collapse state is clear
- [ ] Table headers are announced
- [ ] Action buttons have clear purposes

### Scan Forms
- [ ] Tab buttons are identified
- [ ] Form fields have labels
- [ ] Checkboxes are identified
- [ ] Error messages are announced
- [ ] Submit button is identified

### Baselines
- [ ] Comparison form labels are announced
- [ ] Table is identified
- [ ] Action buttons are clear
- [ ] Confirmation dialog is announced

## Component Checks

### Modals
- [ ] Modal is announced as "dialog"
- [ ] Modal title is announced
- [ ] Form fields are announced
- [ ] Buttons are identified
- [ ] Modal closes and focus returns

### Dropdowns
- [ ] Dropdown is identified
- [ ] Label is announced
- [ ] Options are announced
- [ ] Selected option is indicated

### Tables
- [ ] Table is identified
- [ ] Caption is announced
- [ ] Headers are announced
- [ ] Data has context

### Toasts
- [ ] Toast type is announced
- [ ] Message is read
- [ ] Close button is identified

## Critical Issues (Must Fix)

- [ ] Buttons without labels
- [ ] Form fields without labels
- [ ] Images without alt text
- [ ] Tables without headers
- [ ] Missing headings
- [ ] Unclear announcements
- [ ] Dynamic content not announced
- [ ] Focus not managed

## Test Results

**Page**: _________________
**Date**: _________________
**Tester**: _________________
**Screen Reader**: _________________
**Browser**: _________________

**Status**: ✅ Pass / ❌ Fail

**Issues**:
1. 
2. 
3. 

**Notes**:
- 

