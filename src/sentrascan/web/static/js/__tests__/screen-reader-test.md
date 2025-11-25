# Manual Screen Reader Testing Guide

This document provides comprehensive instructions for testing the SentraScan Platform with screen readers to ensure WCAG 2.1 AA compliance.

## Screen Readers Overview

### NVDA (NonVisual Desktop Access)
- **Platform**: Windows
- **Cost**: Free, open-source
- **Download**: https://www.nvaccess.org/download/
- **Best for**: General testing, most commonly used free screen reader

### JAWS (Job Access With Speech)
- **Platform**: Windows
- **Cost**: Commercial (trial available)
- **Download**: https://www.freedomscientific.com/products/software/jaws/
- **Best for**: Enterprise testing, most popular commercial screen reader

### VoiceOver
- **Platform**: macOS, iOS, iPadOS
- **Cost**: Built-in (free)
- **Activation**: System Preferences → Accessibility → VoiceOver
- **Best for**: Testing on Apple devices

## Setup Instructions

### NVDA Setup (Windows)

1. **Download and Install**:
   - Visit https://www.nvaccess.org/download/
   - Download latest stable version
   - Run installer and follow prompts

2. **Basic Navigation**:
   - **Start/Stop**: Insert+Q (or Ctrl+Alt+N)
   - **Read All**: Insert+Down Arrow
   - **Stop Reading**: Ctrl
   - **Next Element**: Down Arrow
   - **Previous Element**: Up Arrow
   - **Next Heading**: H
   - **Next Link**: K
   - **Next Button**: B
   - **Next Form Field**: F
   - **Next Table**: T

3. **Testing Mode**:
   - Press Insert+Q to start NVDA
   - Navigate to browser (Chrome recommended)
   - Open SentraScan Platform

### JAWS Setup (Windows)

1. **Download Trial**:
   - Visit https://www.freedomscientific.com/products/software/jaws/
   - Download 40-minute trial version
   - Install and activate trial

2. **Basic Navigation**:
   - **Start/Stop**: Insert+J
   - **Read All**: Insert+Down Arrow
   - **Stop Reading**: Ctrl
   - **Next Element**: Down Arrow
   - **Next Heading**: H
   - **Next Link**: K
   - **Next Button**: B
   - **Next Form Field**: F
   - **Next Table**: T

3. **Testing Mode**:
   - Start JAWS
   - Open browser
   - Navigate to application

### VoiceOver Setup (macOS)

1. **Enable VoiceOver**:
   - System Preferences → Accessibility → VoiceOver
   - Check "Enable VoiceOver" (or press Cmd+F5)
   - Configure settings as needed

2. **Basic Navigation**:
   - **Start/Stop**: Cmd+F5
   - **Read All**: VO+A (VO = Control+Option)
   - **Stop Reading**: Control
   - **Next Element**: VO+Right Arrow
   - **Previous Element**: VO+Left Arrow
   - **Next Heading**: VO+H
   - **Next Link**: VO+L
   - **Next Button**: VO+B
   - **Next Form Field**: VO+F
   - **Next Table**: VO+T

3. **Testing Mode**:
   - Enable VoiceOver
   - Open Safari or Chrome
   - Navigate to application

## General Screen Reader Testing Checklist

### ✅ Page Structure
- [ ] Page title is announced
- [ ] Main heading (h1) is announced
- [ ] Heading hierarchy is logical (h1 → h2 → h3)
- [ ] Landmarks are announced (header, nav, main, footer)
- [ ] Page structure is clear and logical

### ✅ Navigation
- [ ] Navigation menu is announced
- [ ] Links are clearly identified
- [ ] Current page is indicated
- [ ] Skip links work and are announced
- [ ] Breadcrumbs are announced

### ✅ Forms
- [ ] Form labels are announced with inputs
- [ ] Required fields are indicated
- [ ] Error messages are announced
- [ ] Help text is associated with fields
- [ ] Form sections are clearly identified

### ✅ Interactive Elements
- [ ] Buttons are identified as buttons
- [ ] Links are identified as links
- [ ] Checkboxes/radio buttons are identified
- [ ] Dropdowns are identified and navigable
- [ ] Modal dialogs are announced

### ✅ Content
- [ ] Images have descriptive alt text
- [ ] Decorative images are hidden
- [ ] Tables are announced with headers
- [ ] Lists are identified
- [ ] Status updates are announced

## Page-Specific Testing

### 1. Login Page (`/login`)

#### NVDA/JAWS Testing
1. [ ] Page title "Login - SentraScan Platform" is announced
2. [ ] Heading "Welcome Back" is announced
3. [ ] Form is identified
4. [ ] "API Key" label is announced before input
5. [ ] Input field is identified as "edit" or "text"
6. [ ] "Required" is announced for required field
7. [ ] Password toggle button is announced with purpose
8. [ ] "Sign In" button is identified
9. [ ] Help text is announced
10. [ ] Error messages are announced if present

#### VoiceOver Testing
1. [ ] Page title announced
2. [ ] Heading announced
3. [ ] Form fields announced with labels
4. [ ] Button purposes are clear
5. [ ] Error messages are announced

**Expected Announcements:**
- "Login - SentraScan Platform, heading level 1, Welcome Back"
- "API Key, edit, required"
- "Enter your API key to authenticate"
- "Sign In, button"

---

### 2. Dashboard Page (`/`)

#### Navigation Testing
1. [ ] Page title is announced
2. [ ] Main heading is announced
3. [ ] Navigation menu items are announced
4. [ ] Statistics cards are announced with values
5. [ ] Chart titles are announced
6. [ ] Tables are identified with headers
7. [ ] Links are clearly identified

#### Content Testing
1. [ ] Stat cards announce: "Total Scans, 42" (value and label)
2. [ ] Charts have ARIA labels describing content
3. [ ] Table headers are announced before data
4. [ ] Sortable columns indicate sort state
5. [ ] Pagination controls are announced

**Expected Announcements:**
- "Dashboard, heading level 1"
- "Total Scans, 42"
- "Pass Rate, 85 percent"
- "Line chart showing scan trends over time"
- "Table with 5 rows and 8 columns"

---

### 3. Scan List Page (`/`)

#### Form Testing
1. [ ] Filter form is identified
2. [ ] "Scan Type" label is announced with select
3. [ ] "Status" label is announced with select
4. [ ] Date pickers are announced with labels
5. [ ] Search input is announced
6. [ ] "Clear Filters" button is announced when filters are active

#### Table Testing
1. [ ] Table is identified with caption
2. [ ] Column headers are announced
3. [ ] Sortable columns indicate sort direction
4. [ ] Row data is announced with context
5. [ ] Links in rows are identified
6. [ ] Pagination is announced

**Expected Announcements:**
- "All Security Scans, table"
- "Time, column header, sortable"
- "Row 1, Time, 2025-01-15, Type, Model, Status, PASS"
- "View scan, link"

---

### 4. Scan Detail Page (`/scan/{id}`)

#### Findings Testing
1. [ ] Findings groups are announced (Critical, High, Medium, Low)
2. [ ] Finding count is announced for each group
3. [ ] Expand/collapse state is announced
4. [ ] Table headers are announced
5. [ ] Finding titles are announced
6. [ ] Checkboxes are identified
7. [ ] Action buttons are announced with purpose

#### Modal Testing
1. [ ] "Create Baseline" button is announced
2. [ ] Modal opens and is announced as dialog
3. [ ] Modal title is announced
4. [ ] Form fields are announced with labels
5. [ ] Submit and Cancel buttons are identified
6. [ ] Modal closes and focus returns

**Expected Announcements:**
- "CRITICAL, heading level 2, 5 findings, collapsed"
- "Select all critical findings in this group, checkbox, not checked"
- "Security Issue, link"
- "Copy finding data, button"
- "Create Baseline, dialog, Modal Title"

---

### 5. Scan Forms (`/ui/scan`)

#### Tab Navigation Testing
1. [ ] Tab buttons are identified
2. [ ] Active tab is indicated
3. [ ] Tab panel content is announced when switched
4. [ ] Form fields are announced with labels
5. [ ] Checkboxes are identified with labels
6. [ ] "Advanced" section toggle is announced
7. [ ] Submit button is identified

#### Validation Testing
1. [ ] Required field errors are announced
2. [ ] Error messages are associated with fields
3. [ ] Focus moves to first error field
4. [ ] Error is announced when field receives focus

**Expected Announcements:**
- "Model Scan, tab, selected, 1 of 2"
- "Model Path, edit, required"
- "The container path to the model file"
- "Strict Mode, checkbox, checked"
- "Run Model Scan, button"

---

### 6. Baselines Page (`/baselines`)

#### Comparison Form Testing
1. [ ] "Left Baseline" label is announced with select
2. [ ] "Right Baseline" label is announced with select
3. [ ] Options are announced when dropdown opens
4. [ ] "Compare" button is identified
5. [ ] Table is announced with headers

#### Actions Testing
1. [ ] "View" buttons are identified
2. [ ] "Compare" buttons are identified
3. [ ] "Delete" buttons are identified
4. [ ] Confirmation dialog is announced
5. [ ] Dialog buttons are identified

**Expected Announcements:**
- "Security Baselines, table"
- "Baseline 1, row 1, View, button, Compare, button, Delete, button"
- "Are you sure you want to delete this baseline?, dialog"

---

### 7. Baseline Comparison Page (`/baseline/compare`)

#### Diff Testing
1. [ ] Page title is announced
2. [ ] Search input is announced
3. [ ] Filter controls are announced
4. [ ] Diff items are announced with type (added, removed, changed)
5. [ ] Expand/collapse buttons are announced
6. [ ] Copy buttons are identified
7. [ ] Export button is identified

**Expected Announcements:**
- "Baseline Comparison, heading level 1"
- "Search, edit"
- "Added, path: /config.json"
- "Copy JSON, button"

---

## Component-Specific Testing

### Modals/Dialogs

#### Announcements
- [ ] Modal opens and is announced as "dialog"
- [ ] Modal title is announced
- [ ] Modal content is readable
- [ ] Focus moves to first element in modal
- [ ] Modal closes and focus returns

#### Navigation
- [ ] Can navigate all modal elements
- [ ] Can submit/cancel with keyboard
- [ ] Escape key closes modal (announced)

**Expected Announcements:**
- "Create Baseline, dialog"
- "Name, edit, required"
- "Create Baseline, button"
- "Cancel, button"

### Dropdowns/Menus

#### Announcements
- [ ] Dropdown is identified
- [ ] Label is announced
- [ ] Options are announced when opened
- [ ] Selected option is indicated
- [ ] Dropdown closes (announced)

**Expected Announcements:**
- "Scan Type, combo box, collapsed, All Types"
- "Model, option, 1 of 3"
- "MCP, option, 2 of 3"

### Tables

#### Announcements
- [ ] Table is identified
- [ ] Caption is announced
- [ ] Column headers are announced
- [ ] Row and column position is announced
- [ ] Data is announced with context

**Expected Announcements:**
- "All Security Scans, table, 10 rows, 8 columns"
- "Row 1, Column 1, Time, 2025-01-15"
- "Column 2, Type, Model"

### Toast Notifications

#### Announcements
- [ ] Toast appears and is announced
- [ ] Toast type is indicated (success, error, warning, info)
- [ ] Toast message is read
- [ ] Close button is identified (if dismissible)
- [ ] Toast dismisses (announced)

**Expected Announcements:**
- "Copied to clipboard, alert, success"
- "Failed to copy, alert, error"
- "Close notification, button"

### Status Updates

#### Announcements
- [ ] Status changes are announced
- [ ] Progress updates are announced
- [ ] Completion is announced
- [ ] Errors are announced assertively

**Expected Announcements:**
- "Scan is now running, status"
- "Scan completed successfully, status"
- "Scan completed with failures, alert"

## Common Issues to Check

### ❌ Problems to Identify

1. **Missing Labels**
   - Buttons without text or aria-label
   - Form fields without labels
   - Links without descriptive text

2. **Poor Announcements**
   - Unclear button purposes
   - Missing context for links
   - Vague form field descriptions

3. **Structure Issues**
   - Missing headings
   - Illogical heading hierarchy
   - Missing landmarks

4. **Dynamic Content**
   - Updates not announced
   - Focus not managed
   - Status changes not communicated

5. **Tables**
   - Missing headers
   - Headers not associated
   - Complex tables not explained

6. **Images**
   - Missing alt text
   - Decorative images not hidden
   - Images with text not described

## Testing Procedure

### Step-by-Step Process

1. **Start Screen Reader**
   - Launch NVDA, JAWS, or enable VoiceOver
   - Verify it's working (should hear speech)

2. **Navigate to Page**
   - Open browser
   - Navigate to page being tested
   - Listen to page title announcement

3. **Read Page Structure**
   - Use heading navigation (H key)
   - Verify heading hierarchy
   - Check landmarks

4. **Navigate Content**
   - Use arrow keys to read content
   - Verify all content is accessible
   - Check for skipped content

5. **Test Forms**
   - Navigate to form fields (F key)
   - Verify labels are announced
   - Test validation
   - Submit form

6. **Test Interactive Elements**
   - Navigate to buttons (B key)
   - Navigate to links (K key)
   - Test dropdowns
   - Test modals

7. **Test Tables**
   - Navigate to tables (T key)
   - Verify headers are announced
   - Navigate table cells
   - Verify data context

8. **Document Issues**
   - Note any problems
   - Record what was announced
   - Note what should be announced

## Test Results Template

### Page: [Page Name]
**Date**: [Date]
**Tester**: [Name]
**Screen Reader**: [NVDA/JAWS/VoiceOver] [Version]
**Browser**: [Browser/Version]

#### Page Structure
- ✅ Pass / ❌ Fail
- **Heading Hierarchy**: [Notes]
- **Landmarks**: [Notes]
- **Issues**: [List issues]

#### Navigation
- ✅ Pass / ❌ Fail
- **Menu Announcements**: [Notes]
- **Links**: [Notes]
- **Issues**: [List issues]

#### Forms
- ✅ Pass / ❌ Fail
- **Label Announcements**: [Notes]
- **Error Messages**: [Notes]
- **Issues**: [List issues]

#### Interactive Elements
- ✅ Pass / ❌ Fail
- **Button Announcements**: [Notes]
- **Modal Announcements**: [Notes]
- **Issues**: [List issues]

#### Content
- ✅ Pass / ❌ Fail
- **Image Alt Text**: [Notes]
- **Table Announcements**: [Notes]
- **Status Updates**: [Notes]
- **Issues**: [List issues]

#### Overall Assessment
- **Status**: ✅ Pass / ❌ Fail / ⚠️ Needs Improvement
- **Critical Issues**: [List critical issues]
- **Recommendations**: [Suggestions]

## Screen Reader Commands Reference

### NVDA Commands
- **Insert+Q**: Start/Stop NVDA
- **Insert+Down Arrow**: Read from cursor
- **H**: Next heading
- **K**: Next link
- **B**: Next button
- **F**: Next form field
- **T**: Next table
- **Insert+F7**: Elements list
- **Insert+B**: Braille viewer (if available)

### JAWS Commands
- **Insert+J**: Start/Stop JAWS
- **Insert+Down Arrow**: Read from cursor
- **H**: Next heading
- **K**: Next link
- **B**: Next button
- **F**: Next form field
- **T**: Next table
- **Insert+F7**: Elements list
- **Insert+F3**: Forms list

### VoiceOver Commands (macOS)
- **Cmd+F5**: Enable/Disable VoiceOver
- **VO+A**: Read all
- **VO+H**: Next heading
- **VO+L**: Next link
- **VO+B**: Next button
- **VO+F**: Next form field
- **VO+T**: Next table
- **VO+U**: Rotor (element navigation)
- **VO+F1**: VoiceOver help

## Resources

- [NVDA User Guide](https://www.nvaccess.org/about-nvda/)
- [JAWS Documentation](https://www.freedomscientific.com/support/documentation/)
- [VoiceOver User Guide](https://www.apple.com/accessibility/vision/)
- [WebAIM Screen Reader Testing](https://webaim.org/articles/screenreader_testing/)
- [Screen Reader Testing Best Practices](https://www.w3.org/WAI/test-evaluate/)

