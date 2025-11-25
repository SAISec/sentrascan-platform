# End-to-End Testing Guide for Critical User Flows

This document provides comprehensive instructions for testing critical user flows in the SentraScan Platform.

## Overview

End-to-end (E2E) testing validates complete user workflows from start to finish, ensuring all components work together correctly.

## Critical User Flows

1. **Login Flow**: User authentication and session management
2. **Trigger Scan Flow**: Creating and executing scans (Model and MCP)
3. **View Results Flow**: Viewing scan results and findings
4. **Baseline Management Flow**: Creating, viewing, and comparing baselines
5. **Dashboard Navigation Flow**: Navigating between pages and using filters

## Testing Setup

### Prerequisites
1. **Running Application**: FastAPI server running on `http://localhost:8200`
2. **Test Data**: 
   - Valid API key with admin role
   - Test model files (for model scans)
   - Test MCP config files (for MCP scans)
3. **Browser**: Chrome, Firefox, or Safari (latest versions)
4. **DevTools**: Open Network tab and Console for monitoring

### Test Environment
- **Base URL**: `http://localhost:8200`
- **Test User**: Admin role with valid API key
- **Test Files**: Sample model and MCP config files

## Flow 1: Login Flow

### Test: Successful Login
**Objective**: Verify user can log in with valid API key

**Steps**:
1. Navigate to `/login` or root URL
2. Verify login page loads
3. Enter valid API key
4. Click "Sign In" button
5. Verify redirect to dashboard
6. Verify session is established
7. Verify user menu shows logged-in state

**Expected Results**:
- ✅ Login page displays correctly
- ✅ Form validation works
- ✅ API key input accepts value
- ✅ Password toggle works (show/hide)
- ✅ Submit button shows loading state
- ✅ Redirect to dashboard after successful login
- ✅ Session cookie is set
- ✅ User menu shows logged-in state
- ✅ No errors in console

**Validation Points**:
- Form fields are accessible (keyboard navigation)
- Error messages display for invalid input
- Loading state is visible during submission
- Screen reader announces status changes

### Test: Failed Login
**Objective**: Verify error handling for invalid API key

**Steps**:
1. Navigate to login page
2. Enter invalid API key
3. Click "Sign In"
4. Verify error message displays
5. Verify form remains on login page
6. Verify error is accessible (screen reader)

**Expected Results**:
- ✅ Error message displays: "Invalid API key"
- ✅ Error is associated with input field (aria-describedby)
- ✅ Input field has error styling
- ✅ Form does not submit
- ✅ User remains on login page
- ✅ Error is announced to screen readers
- ✅ User can correct and retry

### Test: Empty API Key
**Objective**: Verify client-side validation

**Steps**:
1. Navigate to login page
2. Leave API key field empty
3. Click "Sign In"
4. Verify validation error

**Expected Results**:
- ✅ Client-side validation prevents submission
- ✅ Error message: "API key is required"
- ✅ Input field is highlighted
- ✅ Focus moves to input field
- ✅ Error is announced to screen readers

### Test: Session Persistence
**Objective**: Verify session persists across page reloads

**Steps**:
1. Log in successfully
2. Navigate to dashboard
3. Reload page (F5)
4. Verify user remains logged in
5. Close browser tab
6. Reopen and navigate to dashboard
7. Verify user remains logged in

**Expected Results**:
- ✅ Session persists after page reload
- ✅ Session persists after closing/reopening tab
- ✅ User doesn't need to log in again
- ✅ Session expires after appropriate timeout (if implemented)

## Flow 2: Trigger Scan Flow

### Test: Model Scan - Basic
**Objective**: Verify user can trigger a model scan

**Steps**:
1. Log in successfully
2. Navigate to "Run New Scan" (`/ui/scan`)
3. Verify "Model Scan" tab is active
4. Enter model path (e.g., `/data/sample.npy`)
5. Leave defaults for other fields
6. Click "Run Scan" button
7. Verify redirect to scan detail page
8. Verify scan status is "queued" or "running"
9. Verify scan appears in scan list

**Expected Results**:
- ✅ Scan form loads correctly
- ✅ Model Scan tab is selected by default
- ✅ Form fields are accessible
- ✅ Validation works (required fields)
- ✅ Submit button shows loading state
- ✅ Redirect to scan detail page
- ✅ Scan status displays correctly
- ✅ Scan appears in scan list
- ✅ Toast notification appears (if implemented)

**Validation Points**:
- Form validation prevents invalid submissions
- Loading states are visible
- Error messages are clear
- Success feedback is provided

### Test: Model Scan - With Options
**Objective**: Verify scan with advanced options

**Steps**:
1. Navigate to scan form
2. Select "Model Scan" tab
3. Enter model path
4. Uncheck "Strict Mode"
5. Check "Generate SBOM"
6. Check "Run Async"
7. Click "Run Scan"
8. Verify scan is created with options
9. Verify scan detail shows correct options

**Expected Results**:
- ✅ All form fields work correctly
- ✅ Checkboxes toggle properly
- ✅ Options are saved with scan
- ✅ Scan detail reflects selected options
- ✅ Async scan shows "queued" status

### Test: MCP Scan - Basic
**Objective**: Verify user can trigger an MCP scan

**Steps**:
1. Navigate to scan form
2. Click "MCP Scan" tab
3. Verify tab switches correctly
4. Leave "Auto-discover" checked
5. Click "Run Scan"
6. Verify redirect to scan detail page
7. Verify scan status

**Expected Results**:
- ✅ Tab switching works (keyboard and mouse)
- ✅ MCP form displays correctly
- ✅ Auto-discover option works
- ✅ Scan is created successfully
- ✅ Scan detail page loads

### Test: MCP Scan - Manual Config Paths
**Objective**: Verify MCP scan with manual config paths

**Steps**:
1. Navigate to scan form
2. Select "MCP Scan" tab
3. Uncheck "Auto-discover"
4. Enter config paths (one per line)
5. Click "Run Scan"
6. Verify scan uses manual paths

**Expected Results**:
- ✅ Auto-discover can be disabled
- ✅ Config paths textarea accepts input
- ✅ Multiple paths are processed
- ✅ Scan uses provided paths

### Test: Form Validation
**Objective**: Verify form validation prevents invalid submissions

**Steps**:
1. Navigate to scan form
2. Leave required fields empty
3. Click "Run Scan"
4. Verify validation errors
5. Enter invalid data
6. Verify validation errors

**Expected Results**:
- ✅ Required field validation works
- ✅ Error messages are clear
- ✅ Error styling is applied
- ✅ Focus moves to first error
- ✅ Errors are announced to screen readers

### Test: Form Reset
**Objective**: Verify form can be reset

**Steps**:
1. Fill out scan form
2. Click "Reset" or clear form
3. Verify form returns to defaults

**Expected Results**:
- ✅ Form resets correctly
- ✅ All fields return to default values
- ✅ Validation errors are cleared

## Flow 3: View Results Flow

### Test: View Scan Detail
**Objective**: Verify user can view scan results

**Steps**:
1. Navigate to scan list
2. Click on a scan row
3. Verify scan detail page loads
4. Verify scan information displays:
   - Scan ID
   - Status
   - Created date
   - Findings count
   - Severity breakdown
5. Verify findings table displays
6. Verify findings are sortable/filterable

**Expected Results**:
- ✅ Scan detail page loads
- ✅ All scan metadata displays correctly
- ✅ Status badge shows correct status
- ✅ Findings table displays
- ✅ Findings are sortable
- ✅ Findings are filterable
- ✅ Findings can be expanded/collapsed
- ✅ Export button works

**Validation Points**:
- Page loads quickly
- Data is accurate
- Interactive elements work
- Accessibility features work

### Test: View Findings
**Objective**: Verify findings display correctly

**Steps**:
1. Navigate to scan detail page
2. Verify findings table displays
3. Click to expand a finding
4. Verify finding details display:
   - Severity
   - Category
   - Scanner
   - Title
   - Description
   - Location
5. Verify findings can be filtered by severity
6. Verify findings can be sorted

**Expected Results**:
- ✅ Findings table displays all findings
- ✅ Finding details are complete
- ✅ Expand/collapse works
- ✅ Filtering works
- ✅ Sorting works
- ✅ Copy-to-clipboard works (if implemented)
- ✅ Export works

### Test: Real-Time Status Updates
**Objective**: Verify scan status updates in real-time

**Steps**:
1. Navigate to scan detail page for running scan
2. Verify initial status displays
3. Wait for status update
4. Verify status updates automatically
5. Verify progress indicator (if running)
6. Verify page reloads on completion (if implemented)

**Expected Results**:
- ✅ Status updates automatically
- ✅ Badge updates correctly
- ✅ Progress indicator shows (if running)
- ✅ Toast notification on completion
- ✅ Page reloads after completion (if implemented)
- ✅ Screen reader announces updates

### Test: Export Findings
**Objective**: Verify findings can be exported

**Steps**:
1. Navigate to scan detail page
2. Click "Export Findings (CSV)" button
3. Verify file downloads
4. Verify file contains findings
5. Test JSON export (if available)

**Expected Results**:
- ✅ Export button works
- ✅ File downloads correctly
- ✅ File contains all findings
- ✅ File format is correct
- ✅ File name is descriptive

### Test: Create Baseline from Scan
**Objective**: Verify baseline can be created from scan

**Steps**:
1. Navigate to completed scan detail page
2. Click "Create Baseline" button
3. Verify modal opens
4. Enter baseline name
5. Click "Create"
6. Verify baseline is created
7. Verify redirect or success message

**Expected Results**:
- ✅ Create Baseline button works
- ✅ Modal opens correctly
- ✅ Form validation works
- ✅ Baseline is created
- ✅ Success feedback is provided
- ✅ User is redirected or notified

## Flow 4: Baseline Management Flow

### Test: View Baselines List
**Objective**: Verify user can view all baselines

**Steps**:
1. Navigate to baselines page (`/ui/baselines`)
2. Verify baselines table displays
3. Verify baseline information:
   - Name
   - Created date
   - Scan ID
   - Actions (View, Compare, Delete)
4. Verify table is sortable
5. Verify pagination works (if implemented)

**Expected Results**:
- ✅ Baselines page loads
- ✅ Table displays all baselines
- ✅ Information is accurate
- ✅ Sorting works
- ✅ Pagination works (if implemented)

### Test: View Baseline Detail
**Objective**: Verify user can view baseline details

**Steps**:
1. Navigate to baselines page
2. Click "View" on a baseline
3. Verify baseline detail displays
4. Verify baseline content is shown
5. Verify JSON is formatted correctly

**Expected Results**:
- ✅ Baseline detail page loads
- ✅ Baseline content displays
- ✅ JSON is formatted/readable
- ✅ Copy-to-clipboard works (if implemented)

### Test: Compare Baselines
**Objective**: Verify user can compare two baselines

**Steps**:
1. Navigate to baselines page
2. Click "Compare" on a baseline
3. Select second baseline
4. Click "Compare"
5. Verify comparison page loads
6. Verify differences are highlighted
7. Verify side-by-side view works
8. Verify export works

**Expected Results**:
- ✅ Compare button works
- ✅ Baseline selection works
- ✅ Comparison page loads
- ✅ Differences are highlighted
- ✅ Side-by-side view works
- ✅ Synchronized scrolling works (if implemented)
- ✅ Export works

### Test: Delete Baseline
**Objective**: Verify user can delete a baseline

**Steps**:
1. Navigate to baselines page
2. Click "Delete" on a baseline
3. Verify confirmation dialog appears
4. Click "Cancel"
5. Verify baseline is not deleted
6. Click "Delete" again
7. Click "Confirm"
8. Verify baseline is deleted
9. Verify success message

**Expected Results**:
- ✅ Delete button works
- ✅ Confirmation dialog appears
- ✅ Cancel works
- ✅ Confirm deletes baseline
- ✅ Success feedback is provided
- ✅ Baseline is removed from list

## Flow 5: Dashboard Navigation Flow

### Test: Navigate Dashboard
**Objective**: Verify dashboard navigation works

**Steps**:
1. Log in successfully
2. Verify dashboard loads
3. Verify statistics display:
   - Total scans
   - Pass rate
   - Findings count
   - Severity breakdown
4. Verify recent scans table
5. Verify filters work
6. Navigate to scan list
7. Navigate back to dashboard

**Expected Results**:
- ✅ Dashboard loads correctly
- ✅ Statistics are accurate
- ✅ Charts display (if implemented)
- ✅ Filters work
- ✅ Navigation works
- ✅ Breadcrumbs work

### Test: Filter Scans
**Objective**: Verify filtering works across pages

**Steps**:
1. Navigate to dashboard
2. Apply filter (e.g., type=model)
3. Verify filtered results display
4. Navigate to scan list
5. Apply same filter
6. Verify filtered results
7. Clear filters
8. Verify all results display

**Expected Results**:
- ✅ Filters work on dashboard
- ✅ Filters work on scan list
- ✅ Filter state persists (if implemented)
- ✅ Clear filters works
- ✅ Filter chips display (if implemented)

### Test: Search Functionality
**Objective**: Verify search works

**Steps**:
1. Navigate to scan list
2. Enter search term
3. Verify results filter
4. Clear search
5. Verify all results display
6. Test global search (if implemented)

**Expected Results**:
- ✅ Search filters results
- ✅ Search is debounced (if implemented)
- ✅ Clear search works
- ✅ Global search works (if implemented)

### Test: Export Dashboard Data
**Objective**: Verify dashboard export works

**Steps**:
1. Navigate to dashboard
2. Apply filters (optional)
3. Click "Export" dropdown
4. Select "Export as CSV"
5. Verify file downloads
6. Select "Export as JSON"
7. Verify JSON response

**Expected Results**:
- ✅ Export dropdown works
- ✅ CSV export works
- ✅ JSON export works
- ✅ Filters are applied to export
- ✅ File content is correct

## Cross-Flow Testing

### Test: Complete Workflow
**Objective**: Verify complete user workflow from login to viewing results

**Steps**:
1. Log in
2. Navigate to scan form
3. Create a model scan
4. Wait for scan to complete (or use existing completed scan)
5. View scan results
6. Create baseline from scan
7. View baselines list
8. Compare baselines
9. Export findings
10. Log out (if implemented)

**Expected Results**:
- ✅ All steps complete successfully
- ✅ No errors occur
- ✅ Data persists correctly
- ✅ Navigation is smooth
- ✅ User experience is consistent

### Test: Error Recovery
**Objective**: Verify application handles errors gracefully

**Steps**:
1. Log in
2. Trigger scan with invalid data
3. Verify error handling
4. Correct data and retry
5. Verify recovery works
6. Test network errors
7. Verify error messages

**Expected Results**:
- ✅ Errors are caught
- ✅ Error messages are clear
- ✅ User can recover from errors
- ✅ Application doesn't crash
- ✅ Data is not corrupted

## Browser Compatibility Testing

### Chrome/Edge
- [ ] All flows work correctly
- [ ] No console errors
- [ ] Performance is acceptable
- [ ] UI renders correctly

### Firefox
- [ ] All flows work correctly
- [ ] No console errors
- [ ] Performance is acceptable
- [ ] UI renders correctly

### Safari
- [ ] All flows work correctly
- [ ] No console errors
- [ ] Performance is acceptable
- [ ] UI renders correctly

### Mobile Browsers
- [ ] Login works
- [ ] Navigation works
- [ ] Forms are usable
- [ ] Touch targets are adequate

## Performance Testing

### Page Load Times
- [ ] Login page loads < 1 second
- [ ] Dashboard loads < 2 seconds
- [ ] Scan list loads < 2 seconds
- [ ] Scan detail loads < 2 seconds

### Interaction Response
- [ ] Form submissions respond quickly
- [ ] Navigation is smooth
- [ ] Filters apply quickly
- [ ] Exports complete in reasonable time

## Accessibility Testing

### Keyboard Navigation
- [ ] All flows are keyboard accessible
- [ ] Tab order is logical
- [ ] Focus indicators are visible
- [ ] Keyboard shortcuts work (if implemented)

### Screen Readers
- [ ] All flows are announced correctly
- [ ] Form labels are associated
- [ ] Error messages are announced
- [ ] Status changes are announced

## Test Results Template

### Test: [Flow Name]
**Date**: [Date]
**Tester**: [Name]
**Browser**: [Browser/Version]
**Test Data**: [Description]

#### Flow Steps
1. [Step 1]: ✅ Pass / ❌ Fail
2. [Step 2]: ✅ Pass / ❌ Fail
3. [Step 3]: ✅ Pass / ❌ Fail

#### Issues
1. 
2. 
3. 

#### Overall Assessment
- **Status**: ✅ Pass / ❌ Fail / ⚠️ Needs Improvement
- **Critical Issues**: [List issues]
- **Recommendations**: [Suggestions]

## Common Issues to Check

### ❌ Problems to Identify

1. **Navigation Issues**
   - Links don't work
   - Redirects fail
   - Breadcrumbs incorrect
   - Back button issues

2. **Form Issues**
   - Validation doesn't work
   - Submissions fail
   - Data not saved
   - Error messages unclear

3. **Data Issues**
   - Data doesn't display
   - Data is incorrect
   - Data doesn't update
   - Data is lost

4. **Performance Issues**
   - Pages load slowly
   - Interactions are slow
   - Timeouts occur
   - Memory leaks

5. **Error Handling**
   - Errors not caught
   - Error messages unclear
   - Recovery doesn't work
   - Application crashes

## Debugging Tips

### Chrome DevTools
1. **Network Tab**: Monitor API requests
2. **Console**: Check for errors
3. **Application Tab**: Check cookies/session
4. **Performance Tab**: Monitor performance

### Common Debugging Steps
1. Check console for errors
2. Verify API responses
3. Check network requests
4. Verify session/cookies
5. Test with different data
6. Test with different browsers

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

