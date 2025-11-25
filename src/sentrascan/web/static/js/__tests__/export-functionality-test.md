# Export Functionality Testing Guide

This document provides comprehensive instructions for testing CSV and JSON export functionality across the SentraScan Platform.

## Overview

The SentraScan Platform provides multiple export options:
1. **Dashboard Export**: Export filtered dashboard data
2. **Scan List Export**: Export filtered scan list
3. **Findings Export**: Export findings for a specific scan
4. **Baseline Comparison Export**: Export baseline comparison results
5. **Selected Findings Export**: Export selected findings from scan detail page

## Export Endpoints

### 1. Dashboard Export
- **Endpoint**: `/api/v1/dashboard/export`
- **Formats**: CSV, JSON
- **Filters**: `type`, `passed`, `time_range`
- **Method**: GET
- **Authentication**: API Key required

### 2. Scan List Export
- **Endpoint**: `/api/v1/scans/export`
- **Formats**: CSV
- **Filters**: `type`, `passed`, `time_range`, `date_from`, `date_to`, `search`
- **Method**: GET
- **Authentication**: API Key required

### 3. Findings Export
- **Endpoint**: `/api/v1/scans/{scan_id}/findings/export`
- **Formats**: CSV, JSON
- **Filters**: None (exports all findings for scan)
- **Method**: GET
- **Authentication**: API Key required

### 4. Baseline Comparison Export
- **Type**: Client-side (JavaScript)
- **Formats**: JSON, Text
- **Method**: JavaScript function `exportComparison(format)`

### 5. Selected Findings Export
- **Type**: Client-side (JavaScript)
- **Formats**: JSON
- **Method**: JavaScript function `exportSelectedFindings()`

## Testing Setup

### Prerequisites
1. **Running Application**: Ensure FastAPI server is running
2. **Test Data**: Have scans and findings available
3. **Browser DevTools**: Open Network tab to monitor requests
4. **File System Access**: Ensure browser allows file downloads

### Test Data Requirements
- At least 3 scans (different types, statuses, dates)
- At least 1 scan with findings
- At least 1 baseline for comparison
- Various filter combinations

## Testing Procedures

### 1. Dashboard Export Testing

#### Test: CSV Export
**Steps**:
1. Navigate to dashboard (`/`)
2. Apply filters (optional): type, passed, time_range
3. Click "Export" dropdown
4. Select "Export as CSV"
5. Verify file downloads
6. Open downloaded CSV file
7. Verify content

**Expected Results**:
- ✅ File downloads with name `sentrascan-dashboard-export.csv`
- ✅ CSV contains header row: `ID, Created At, Type, Target, Passed, Critical, High, Medium, Low, Total Findings`
- ✅ CSV contains data rows matching filtered scans
- ✅ Data matches dashboard display
- ✅ File opens correctly in Excel/Google Sheets
- ✅ Special characters are properly escaped

#### Test: JSON Export
**Steps**:
1. Navigate to dashboard (`/`)
2. Apply filters (optional)
3. Click "Export" dropdown
4. Select "Export as JSON"
5. Verify JSON response
6. Save JSON to file (if needed)
7. Verify JSON structure

**Expected Results**:
- ✅ JSON response received
- ✅ JSON structure includes:
  - `exported_at`: ISO timestamp
  - `filters`: Applied filter values
  - `total_scans`: Number of scans
  - `scans`: Array of scan objects
- ✅ Each scan object contains: `id`, `created_at`, `type`, `target`, `passed`, `critical`, `high`, `medium`, `low`, `total_findings`
- ✅ JSON is valid and parseable
- ✅ Data matches dashboard display

#### Test: Filtered Export
**Steps**:
1. Navigate to dashboard
2. Apply filter: `type=model`
3. Export as CSV
4. Verify only model scans exported
5. Apply filter: `passed=false`
6. Export as CSV
7. Verify only failed scans exported
8. Apply filter: `time_range=7d`
9. Export as CSV
10. Verify only recent scans exported

**Expected Results**:
- ✅ Filters are applied correctly
- ✅ Exported data matches filtered view
- ✅ Filter parameters are included in export URL
- ✅ Multiple filters work together

### 2. Scan List Export Testing

#### Test: CSV Export
**Steps**:
1. Navigate to scan list page (`/`)
2. Apply filters (optional)
3. Click "Export CSV" button
4. Verify file downloads
5. Open downloaded CSV file
6. Verify content

**Expected Results**:
- ✅ File downloads
- ✅ CSV contains scan data
- ✅ Data matches scan list display
- ✅ Filters are applied to export
- ✅ File opens correctly

#### Test: Filtered Export
**Steps**:
1. Navigate to scan list
2. Apply search filter
3. Apply date range filter
4. Apply type filter
5. Export CSV
6. Verify exported data matches filtered list

**Expected Results**:
- ✅ All filters are applied
- ✅ Export URL includes all filter parameters
- ✅ Exported data matches filtered view
- ✅ Filter parameters are URL-encoded correctly

### 3. Findings Export Testing

#### Test: CSV Export
**Steps**:
1. Navigate to scan detail page (`/scan/{scan_id}`)
2. Verify scan has findings
3. Click "Export Findings (CSV)" button
4. Verify file downloads
5. Open downloaded CSV file
6. Verify content

**Expected Results**:
- ✅ File downloads with name `sentrascan-findings-{scan_id[:8]}.csv`
- ✅ CSV contains header row: `ID, Severity, Category, Scanner, Title, Description, Location`
- ✅ CSV contains all findings for the scan
- ✅ Description is truncated to 500 characters (if long)
- ✅ Newlines in description are replaced with spaces
- ✅ File opens correctly

#### Test: JSON Export
**Steps**:
1. Navigate to scan detail page
2. Access export endpoint directly: `/api/v1/scans/{scan_id}/findings/export?format=json`
3. Verify JSON response
4. Verify JSON structure

**Expected Results**:
- ✅ JSON response received
- ✅ JSON structure includes:
  - `scan_id`: Scan identifier
  - `exported_at`: ISO timestamp
  - `total_findings`: Number of findings
  - `findings`: Array of finding objects
- ✅ Each finding object contains: `id`, `severity`, `category`, `scanner`, `title`, `description`, `location`
- ✅ JSON is valid and parseable
- ✅ All findings are included

#### Test: Empty Findings
**Steps**:
1. Navigate to scan detail page with no findings
2. Attempt to export findings
3. Verify export behavior

**Expected Results**:
- ✅ Export succeeds (no error)
- ✅ CSV contains only header row
- ✅ JSON contains empty `findings` array
- ✅ `total_findings` is 0

### 4. Baseline Comparison Export Testing

#### Test: JSON Export
**Steps**:
1. Navigate to baseline comparison page
2. Click "Export JSON" button
3. Verify file downloads
4. Open downloaded JSON file
5. Verify content

**Expected Results**:
- ✅ File downloads with name like `sentrascan-comparison-{timestamp}.json`
- ✅ JSON structure includes:
  - `baseline1_id`: First baseline ID
  - `baseline2_id`: Second baseline ID
  - `exported_at`: ISO timestamp
  - `summary`: Comparison summary
  - `diff`: Detailed differences
- ✅ JSON is valid and parseable
- ✅ Data matches comparison display

#### Test: Text Export
**Steps**:
1. Navigate to baseline comparison page
2. Click "Export Text" button
3. Verify file downloads
4. Open downloaded text file
5. Verify content

**Expected Results**:
- ✅ File downloads
- ✅ Text format is readable
- ✅ Includes comparison summary
- ✅ Includes detailed differences
- ✅ Includes export timestamp

### 5. Selected Findings Export Testing

#### Test: Export Selected Findings
**Steps**:
1. Navigate to scan detail page
2. Select multiple findings using checkboxes
3. Click "Export Selected" button
4. Verify file downloads
5. Open downloaded JSON file
6. Verify content

**Expected Results**:
- ✅ File downloads with name like `sentrascan-findings-{timestamp}.json`
- ✅ JSON contains only selected findings
- ✅ Each finding includes: `id`, `severity`, `category`, `scanner`, `title`, `description`, `location`
- ✅ JSON is valid and parseable
- ✅ Toast notification appears

#### Test: No Selection
**Steps**:
1. Navigate to scan detail page
2. Don't select any findings
3. Click "Export Selected" button
4. Verify error handling

**Expected Results**:
- ✅ Alert message appears: "No findings selected"
- ✅ No file is downloaded
- ✅ No error in console

#### Test: Single Finding
**Steps**:
1. Select one finding
2. Export selected
3. Verify export contains only that finding

**Expected Results**:
- ✅ Export succeeds
- ✅ JSON contains single finding
- ✅ Data is correct

## File Format Testing

### CSV Format
- [ ] Headers are present
- [ ] Data rows match headers
- [ ] Special characters are escaped/quoted
- [ ] Commas in data are handled correctly
- [ ] Newlines in data are handled correctly
- [ ] UTF-8 encoding is correct
- [ ] File opens in Excel/Google Sheets
- [ ] File opens in text editor

### JSON Format
- [ ] JSON is valid (parseable)
- [ ] JSON is properly formatted (indented)
- [ ] All required fields are present
- [ ] Data types are correct (strings, numbers, booleans)
- [ ] Timestamps are ISO format
- [ ] No circular references
- [ ] File size is reasonable

## Error Handling Testing

### Invalid Scan ID
- [ ] Export with invalid scan ID returns 404
- [ ] Error message is clear
- [ ] No file is downloaded

### Missing Authentication
- [ ] Export without API key returns 401/403
- [ ] Error message is clear
- [ ] No file is downloaded

### Network Errors
- [ ] Export fails gracefully on network error
- [ ] User is informed of error
- [ ] No partial file is downloaded

### Large Data Sets
- [ ] Export works with many scans (100+)
- [ ] Export works with many findings (1000+)
- [ ] File size is reasonable
- [ ] Export completes in reasonable time

## Browser Compatibility Testing

### Chrome/Edge
- [ ] CSV downloads work
- [ ] JSON downloads work
- [ ] File names are correct
- [ ] File content is correct

### Firefox
- [ ] CSV downloads work
- [ ] JSON downloads work
- [ ] File names are correct
- [ ] File content is correct

### Safari
- [ ] CSV downloads work
- [ ] JSON downloads work
- [ ] File names are correct
- [ ] File content is correct

### Mobile Browsers
- [ ] Downloads work (may require user interaction)
- [ ] File names are correct
- [ ] File content is correct

## Performance Testing

### Export Speed
- [ ] Small exports (< 100 items) complete quickly (< 1 second)
- [ ] Medium exports (100-1000 items) complete in reasonable time (< 5 seconds)
- [ ] Large exports (1000+ items) complete without timeout (< 30 seconds)

### Memory Usage
- [ ] Export doesn't cause memory issues
- [ ] Large exports don't crash browser
- [ ] Memory is released after export

## Accessibility Testing

### Keyboard Navigation
- [ ] Export buttons are keyboard accessible
- [ ] Export dropdown is keyboard navigable
- [ ] Focus indicators are visible

### Screen Readers
- [ ] Export buttons have descriptive labels
- [ ] Export actions are announced
- [ ] File downloads are announced (if possible)

## Test Results Template

### Test: [Test Name]
**Date**: [Date]
**Tester**: [Name]
**Browser**: [Browser/Version]
**Test Data**: [Description]

#### Export Details
- **Type**: Dashboard / Scan List / Findings / Comparison / Selected
- **Format**: CSV / JSON / Text
- **Filters**: [List filters]
- **Items Exported**: [Number]

#### File Verification
- **File Name**: [Name]
- **File Size**: [Size]
- **File Format**: ✅ Valid / ❌ Invalid
- **Content**: ✅ Correct / ❌ Incorrect

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

1. **Download Issues**
   - File doesn't download
   - File downloads with wrong name
   - File downloads with wrong format
   - Download blocked by browser

2. **Content Issues**
   - Missing data
   - Incorrect data
   - Wrong format
   - Encoding issues
   - Special characters broken

3. **Filter Issues**
   - Filters not applied
   - Wrong filters applied
   - Filter parameters missing
   - Filter parameters incorrect

4. **Performance Issues**
   - Export too slow
   - Export times out
   - Browser becomes unresponsive
   - Memory issues

5. **Error Handling**
   - Errors not caught
   - No error messages
   - Partial files downloaded
   - Unhandled exceptions

## Debugging Tips

### Chrome DevTools
1. **Network Tab**: Monitor export requests
2. **Console**: Check for errors
3. **Application Tab**: Check downloaded files
4. **Performance Tab**: Monitor performance

### Firefox DevTools
1. **Network Tab**: Monitor requests
2. **Console**: Check for errors
3. **Storage Tab**: Check downloads

### Console Commands
```javascript
// Test export endpoint
fetch('/api/v1/dashboard/export?format=json')
  .then(r => r.json())
  .then(data => console.log(data));

// Test findings export
fetch('/api/v1/scans/{scan_id}/findings/export?format=csv')
  .then(r => r.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    console.log('Download URL:', url);
  });
```

## Resources

- [CSV Format Specification](https://tools.ietf.org/html/rfc4180)
- [JSON Format Specification](https://www.json.org/)
- [FastAPI Response Documentation](https://fastapi.tiangolo.com/advanced/custom-response/)

