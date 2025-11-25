# Export Functionality Testing Quick Checklist

Quick reference for export functionality testing.

## Quick Test Setup

1. **Start Server**: Ensure FastAPI server is running
2. **Open DevTools**: Network tab and Console
3. **Prepare Data**: Have scans and findings available
4. **Test Downloads**: Ensure browser allows downloads

## Essential Checks

### Dashboard Export
- [ ] CSV export downloads
- [ ] JSON export works
- [ ] Filters are applied
- [ ] File content is correct

### Scan List Export
- [ ] CSV export downloads
- [ ] Filters are applied
- [ ] File content matches list

### Findings Export
- [ ] CSV export downloads
- [ ] JSON export works
- [ ] All findings included
- [ ] File content is correct

### Baseline Comparison Export
- [ ] JSON export downloads
- [ ] Text export downloads
- [ ] Content matches comparison

### Selected Findings Export
- [ ] Export selected works
- [ ] Only selected findings exported
- [ ] No selection shows alert

## Format Verification

### CSV
- [ ] Headers present
- [ ] Data rows correct
- [ ] Opens in Excel/Sheets
- [ ] Special characters handled

### JSON
- [ ] Valid JSON
- [ ] Properly formatted
- [ ] All fields present
- [ ] Parseable

## Error Handling

- [ ] Invalid scan ID handled
- [ ] Missing auth handled
- [ ] Network errors handled
- [ ] Large datasets handled

## Browser Testing

- [ ] Chrome: All exports work
- [ ] Firefox: All exports work
- [ ] Safari: All exports work
- [ ] Mobile: Downloads work

## Test Results

**Date**: _________________
**Tester**: _________________
**Browser**: _________________

**Dashboard Export**: ✅ Pass / ❌ Fail
**Scan List Export**: ✅ Pass / ❌ Fail
**Findings Export**: ✅ Pass / ❌ Fail
**Comparison Export**: ✅ Pass / ❌ Fail
**Selected Export**: ✅ Pass / ❌ Fail

**Issues**:
1. 
2. 
3. 

