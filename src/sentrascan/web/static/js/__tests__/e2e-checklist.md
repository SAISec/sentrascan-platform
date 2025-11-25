# End-to-End Testing Quick Checklist

Quick reference for critical user flow testing.

## Quick Test Setup

1. **Start Server**: Ensure FastAPI server is running
2. **Open Browser**: Chrome/Firefox/Safari
3. **Open DevTools**: Network tab and Console
4. **Prepare Data**: Valid API key, test files

## Critical Flows

### 1. Login Flow
- [ ] Login page loads
- [ ] Valid API key logs in
- [ ] Invalid API key shows error
- [ ] Empty API key shows validation
- [ ] Session persists after reload
- [ ] Password toggle works

### 2. Trigger Scan Flow
- [ ] Scan form loads
- [ ] Model scan tab works
- [ ] MCP scan tab works
- [ ] Form validation works
- [ ] Model scan creates successfully
- [ ] MCP scan creates successfully
- [ ] Redirect to scan detail works

### 3. View Results Flow
- [ ] Scan detail page loads
- [ ] Scan information displays
- [ ] Findings table displays
- [ ] Findings expand/collapse
- [ ] Findings filter/sort
- [ ] Real-time status updates
- [ ] Export findings works
- [ ] Create baseline works

### 4. Baseline Management Flow
- [ ] Baselines list loads
- [ ] View baseline works
- [ ] Compare baselines works
- [ ] Delete baseline works
- [ ] Confirmation dialog works

### 5. Dashboard Navigation Flow
- [ ] Dashboard loads
- [ ] Statistics display
- [ ] Charts display (if implemented)
- [ ] Filters work
- [ ] Search works
- [ ] Export works
- [ ] Navigation works

## Cross-Flow Testing

- [ ] Complete workflow (login → scan → view → baseline)
- [ ] Error recovery works
- [ ] Data persists correctly
- [ ] Navigation is smooth

## Browser Testing

- [ ] Chrome: All flows work
- [ ] Firefox: All flows work
- [ ] Safari: All flows work
- [ ] Mobile: Core flows work

## Performance

- [ ] Pages load quickly (< 2s)
- [ ] Interactions are responsive
- [ ] No timeouts
- [ ] No memory leaks

## Accessibility

- [ ] Keyboard navigation works
- [ ] Screen reader works
- [ ] Focus indicators visible
- [ ] Error messages announced

## Test Results

**Date**: _________________
**Tester**: _________________
**Browser**: _________________

**Login Flow**: ✅ Pass / ❌ Fail
**Trigger Scan Flow**: ✅ Pass / ❌ Fail
**View Results Flow**: ✅ Pass / ❌ Fail
**Baseline Flow**: ✅ Pass / ❌ Fail
**Dashboard Flow**: ✅ Pass / ❌ Fail

**Critical Issues**:
1. 
2. 
3. 

