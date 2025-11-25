# Real-Time Update Testing Quick Checklist

Quick reference for real-time update functionality testing.

## Quick Test Setup

1. **Start Server**: Ensure FastAPI server is running
2. **Open DevTools**: Network tab and Console
3. **Navigate**: Go to scan detail page
4. **Monitor**: Watch for SSE connection or polling requests

## Essential Checks

### SSE Connection
- [ ] Connection establishes to `/api/v1/scans/{id}/status/stream`
- [ ] Response type is `text/event-stream`
- [ ] Connection remains open
- [ ] Status updates are received

### Status Updates
- [ ] Status badge updates
- [ ] Status text updates
- [ ] Badge color changes
- [ ] Icons update

### Polling Fallback
- [ ] Polling activates if SSE unavailable
- [ ] Requests sent every 3 seconds
- [ ] Polling stops on completion
- [ ] Status updates received

### UI Updates
- [ ] Progress indicator shows/hides
- [ ] Findings count updates
- [ ] Toast appears on completion
- [ ] Page reloads after completion

## Status Transition Testing

- [ ] queued → running
- [ ] running → completed
- [ ] running → failed
- [ ] Each transition updates UI

## Browser Testing

- [ ] Chrome: SSE works
- [ ] Firefox: SSE works
- [ ] Safari: SSE works
- [ ] Mobile: SSE or polling works

## Error Handling

- [ ] Connection errors handled
- [ ] Polling fallback activates
- [ ] User notified of errors
- [ ] No unhandled exceptions

## Test Results

**Scan ID**: _________________
**Date**: _________________
**Tester**: _________________
**Browser**: _________________

**Connection**: ✅ SSE / ✅ Polling / ❌ Failed
**Updates**: ✅ Pass / ❌ Fail
**UI Updates**: ✅ Pass / ❌ Fail

**Issues**:
1. 
2. 
3. 

