# Real-Time Update Functionality Testing Guide

This document provides comprehensive instructions for testing Server-Sent Events (SSE) and polling functionality for real-time scan status updates.

## Overview

The SentraScan Platform uses Server-Sent Events (SSE) for real-time scan status updates, with polling as a fallback for browsers that don't support SSE.

## Testing Components

### 1. Server-Sent Events (SSE)
- **Endpoint**: `/api/v1/scans/{scan_id}/status/stream`
- **Method**: GET
- **Response**: `text/event-stream`
- **Format**: JSON data in SSE format

### 2. Polling Fallback
- **Endpoint**: `/api/v1/scans/{scan_id}/status`
- **Method**: GET
- **Response**: JSON
- **Interval**: 3 seconds

### 3. Auto-Update Function
- **Function**: `autoUpdateScanStatus(scanId, options)`
- **Features**: UI updates, progress indicators, toast notifications

## Testing Setup

### Prerequisites
1. **Running Application**: Ensure the FastAPI server is running
2. **Active Scan**: Have a scan that can be monitored (queued or running)
3. **Browser DevTools**: Open Network tab to monitor connections
4. **Console**: Open browser console to see logs

### Test Scenarios

#### Scenario 1: SSE Connection Test
1. Navigate to scan detail page (`/scan/{scan_id}`)
2. Open browser DevTools → Network tab
3. Filter by "EventStream" or "stream"
4. Verify SSE connection is established
5. Check connection status in console

#### Scenario 2: Status Update Test
1. Start a scan (or use existing running scan)
2. Navigate to scan detail page
3. Observe status badge updates
4. Check console for update messages
5. Verify UI reflects status changes

#### Scenario 3: Polling Fallback Test
1. Disable SSE (or use browser without SSE support)
2. Navigate to scan detail page
3. Open Network tab
4. Verify polling requests every 3 seconds
5. Check status updates occur

## Testing Procedures

### 1. SSE Connection Testing

#### Test: Connection Establishment
**Steps**:
1. Navigate to scan detail page for a running scan
2. Open DevTools → Network tab
3. Look for request to `/api/v1/scans/{scan_id}/status/stream`
4. Check response type is `text/event-stream`
5. Verify connection status is "200 OK"

**Expected Results**:
- ✅ Connection established successfully
- ✅ Response type is `text/event-stream`
- ✅ Connection remains open
- ✅ No connection errors

#### Test: Connection Error Handling
**Steps**:
1. Stop the server (or block the endpoint)
2. Navigate to scan detail page
3. Observe error handling
4. Check if polling fallback activates

**Expected Results**:
- ✅ Error is caught and handled
- ✅ Polling fallback activates (if implemented)
- ✅ User is notified of connection issue
- ✅ No unhandled errors in console

#### Test: Connection Reconnection
**Steps**:
1. Establish SSE connection
2. Temporarily disconnect network
3. Reconnect network
4. Observe reconnection behavior

**Expected Results**:
- ✅ Connection attempts to reconnect
- ✅ Status updates resume after reconnection
- ✅ No duplicate connections

### 2. Status Update Testing

#### Test: Status Transitions
**Steps**:
1. Start a new scan
2. Navigate to scan detail page
3. Observe status changes:
   - `queued` → `running` → `completed`
4. Verify each transition is reflected in UI

**Expected Results**:
- ✅ Status badge updates correctly
- ✅ Status text updates
- ✅ Badge color changes appropriately
- ✅ Icons update correctly

#### Test: Progress Indicator
**Steps**:
1. Navigate to running scan detail page
2. Verify progress indicator appears
3. Check progress indicator styling
4. Verify it disappears when scan completes

**Expected Results**:
- ✅ Progress indicator shows when status is "running"
- ✅ Progress indicator is visible and styled
- ✅ Progress indicator hides when scan completes
- ✅ Progress indicator hides on error

#### Test: Findings Count Updates
**Steps**:
1. Navigate to running scan detail page
2. Observe findings count element (if present)
3. Verify count updates as scan progresses
4. Check final count matches actual findings

**Expected Results**:
- ✅ Findings count updates in real-time
- ✅ Count is accurate
- ✅ UI reflects current count

### 3. Polling Fallback Testing

#### Test: Polling Activation
**Steps**:
1. Use browser without SSE support (or disable SSE)
2. Navigate to scan detail page
3. Open Network tab
4. Verify polling requests every 3 seconds
5. Check request to `/api/v1/scans/{scan_id}/status`

**Expected Results**:
- ✅ Polling activates automatically
- ✅ Requests sent every 3 seconds
- ✅ Status updates received
- ✅ UI updates correctly

#### Test: Polling Stops on Completion
**Steps**:
1. Start polling for a scan
2. Wait for scan to complete
3. Verify polling stops
4. Check no further requests are made

**Expected Results**:
- ✅ Polling stops when status is "completed"
- ✅ Polling stops when status is "failed"
- ✅ No unnecessary requests after completion
- ✅ Interval is cleared

#### Test: Polling Error Handling
**Steps**:
1. Start polling
2. Cause network error (block endpoint)
3. Observe error handling
4. Check if polling continues or stops

**Expected Results**:
- ✅ Errors are caught and logged
- ✅ User is notified (if applicable)
- ✅ Polling may retry or stop gracefully

### 4. UI Update Testing

#### Test: Badge Updates
**Steps**:
1. Navigate to scan detail page
2. Observe status badge
3. Trigger status change
4. Verify badge updates:
   - Class changes
   - Text changes
   - Icon changes
   - Color changes

**Expected Results**:
- ✅ Badge class updates (e.g., `badge-success`, `badge-error`)
- ✅ Badge text updates (e.g., "PASS", "FAIL")
- ✅ Badge icon updates
- ✅ Badge color updates

#### Test: Status Text Updates
**Steps**:
1. Navigate to scan detail page
2. Find status text element
3. Trigger status change
4. Verify text updates

**Expected Results**:
- ✅ Status text reflects current status
- ✅ Text is readable
- ✅ Updates occur smoothly

#### Test: Screen Reader Announcements
**Steps**:
1. Enable screen reader (NVDA, JAWS, VoiceOver)
2. Navigate to scan detail page
3. Trigger status change
4. Verify status is announced

**Expected Results**:
- ✅ Status changes are announced
- ✅ Announcements are clear and descriptive
- ✅ Appropriate aria-live region is used

#### Test: Toast Notifications
**Steps**:
1. Navigate to scan detail page
2. Wait for scan to complete
3. Verify toast notification appears
4. Check toast type (success/error)

**Expected Results**:
- ✅ Toast appears on completion
- ✅ Toast type matches scan result (success/error)
- ✅ Toast message is clear
- ✅ Toast auto-dismisses or is dismissible

### 5. Page Reload Testing

#### Test: Auto-Reload on Completion
**Steps**:
1. Navigate to scan detail page
2. Wait for scan to complete
3. Observe page behavior
4. Verify page reloads after delay

**Expected Results**:
- ✅ Page reloads after scan completion
- ✅ Reload occurs after short delay (2 seconds)
- ✅ Final results are displayed after reload
- ✅ No data loss during reload

### 6. Multiple Scans Testing

#### Test: Multiple Active Connections
**Steps**:
1. Open multiple scan detail pages (different scans)
2. Verify each has its own connection
3. Check connections don't interfere
4. Verify all updates correctly

**Expected Results**:
- ✅ Each scan has independent connection
- ✅ Connections don't conflict
- ✅ All scans update correctly
- ✅ Connections are cleaned up on page close

#### Test: Connection Cleanup
**Steps**:
1. Establish SSE connection
2. Navigate away from page
3. Verify connection is closed
4. Check no memory leaks

**Expected Results**:
- ✅ Connection closes on page unload
- ✅ No memory leaks
- ✅ Resources are cleaned up

## Browser Compatibility Testing

### Chrome/Edge
- [ ] SSE connection works
- [ ] Status updates received
- [ ] Polling fallback works if SSE fails
- [ ] UI updates correctly

### Firefox
- [ ] SSE connection works
- [ ] Status updates received
- [ ] Polling fallback works if SSE fails
- [ ] UI updates correctly

### Safari
- [ ] SSE connection works
- [ ] Status updates received
- [ ] Polling fallback works if SSE fails
- [ ] UI updates correctly

### Mobile Browsers
- [ ] SSE works on mobile Chrome
- [ ] SSE works on mobile Safari
- [ ] Polling fallback works
- [ ] UI updates correctly

## Network Condition Testing

### Slow Network
- [ ] Connection establishes (may take longer)
- [ ] Updates are received (may be delayed)
- [ ] UI remains responsive
- [ ] No timeouts cause issues

### Intermittent Connection
- [ ] Connection reconnects automatically
- [ ] Updates resume after reconnection
- [ ] No duplicate updates
- [ ] User is informed of connection issues

### Offline/No Connection
- [ ] Error is handled gracefully
- [ ] Polling fallback attempts (if applicable)
- [ ] User is informed
- [ ] No unhandled errors

## Performance Testing

### Connection Overhead
- [ ] SSE connection doesn't impact page performance
- [ ] Polling doesn't cause performance issues
- [ ] UI updates are smooth
- [ ] No memory leaks

### Update Frequency
- [ ] Updates don't flood the UI
- [ ] Updates are throttled if needed
- [ ] UI remains responsive
- [ ] No visual flickering

## Test Results Template

### Test: [Test Name]
**Date**: [Date]
**Tester**: [Name]
**Browser**: [Browser/Version]
**Scan ID**: [Scan ID]

#### Connection
- **Type**: SSE / Polling
- **Status**: ✅ Connected / ❌ Failed
- **Endpoint**: [Endpoint URL]
- **Issues**: [List issues]

#### Status Updates
- **Updates Received**: [Yes/No]
- **Status Transitions**: [List transitions]
- **UI Updates**: ✅ Pass / ❌ Fail
- **Issues**: [List issues]

#### UI Elements
- **Badge Updates**: ✅ Pass / ❌ Fail
- **Progress Indicator**: ✅ Pass / ❌ Fail
- **Toast Notifications**: ✅ Pass / ❌ Fail
- **Screen Reader**: ✅ Pass / ❌ Fail

#### Overall Assessment
- **Status**: ✅ Pass / ❌ Fail / ⚠️ Needs Improvement
- **Critical Issues**: [List issues]
- **Recommendations**: [Suggestions]

## Common Issues to Check

### ❌ Problems to Identify

1. **Connection Issues**
   - Connection fails to establish
   - Connection drops unexpectedly
   - No reconnection attempt
   - Multiple connections for same scan

2. **Update Issues**
   - Status updates not received
   - UI doesn't update
   - Updates are delayed
   - Duplicate updates

3. **UI Issues**
   - Badge doesn't update
   - Progress indicator doesn't show/hide
   - Toast doesn't appear
   - Page doesn't reload on completion

4. **Performance Issues**
   - Connection causes slowdown
   - Too many updates
   - Memory leaks
   - UI becomes unresponsive

5. **Error Handling**
   - Errors not caught
   - No fallback mechanism
   - User not informed of errors
   - Unhandled exceptions

## Debugging Tips

### Chrome DevTools
1. **Network Tab**: Monitor SSE connection
2. **Console**: Check for errors and logs
3. **Application Tab**: Check EventSource connections
4. **Performance Tab**: Monitor performance impact

### Firefox DevTools
1. **Network Tab**: Monitor connections
2. **Console**: Check for errors
3. **Performance Tab**: Monitor performance

### Console Commands
```javascript
// Check active connections
console.log(activeConnections);

// Manually connect
connectScanStatusStream('scan-id', {
  onUpdate: (data) => console.log('Update:', data),
  onComplete: (data) => console.log('Complete:', data),
  onError: (error) => console.error('Error:', error)
});

// Manually poll
pollScanStatus('scan-id', {
  onUpdate: (data) => console.log('Update:', data)
});
```

## Resources

- [MDN Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [FastAPI SSE Documentation](https://fastapi.tiangolo.com/advanced/server-sent-events/)

