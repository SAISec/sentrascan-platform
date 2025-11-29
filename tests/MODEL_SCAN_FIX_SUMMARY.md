# Model Scan Findings Storage Fix - Summary

## Problem

When scanning the YOLO World Mirror model from Hugging Face, modelaudit correctly detected 320 security issues (including critical pickle and PyTorch vulnerabilities), but these findings were not being stored in the database. The scan showed 0 findings and was incorrectly marked as "PASSED".

## Root Cause

**Issue:** modelaudit was failing with a read-only filesystem error:
```
[Errno 30] Read-only file system: '/home/nonroot/.modelaudit'
```

Even though `MODELAUDIT_CACHE_DIR` was set to `/cache/modelaudit`, modelaudit was still trying to use `/home/nonroot/.modelaudit` as a fallback cache location, which is read-only in the distroless container.

**Impact:**
- modelaudit returned exit code 2 (error)
- Report file was only 315-318 bytes (error response, not full report)
- No findings were extracted or stored
- Scans incorrectly showed 0 findings and "PASSED" status

## Solution

### 1. Fixed Environment Variables

**File:** `src/sentrascan/modules/model/scanner.py`

**Changes:**
- Set `HOME=/cache` (writable directory) instead of `/home/nonroot`
- Added `XDG_CACHE_HOME` environment variable
- Ensured `MODELAUDIT_CACHE_DIR` points to writable volume

```python
# Set HOME to writable location - modelaudit uses ~/.modelaudit as fallback
writable_home = "/cache"
os.makedirs(writable_home, exist_ok=True)
env["HOME"] = writable_home
env["XDG_CACHE_HOME"] = modelaudit_cache
```

### 2. Changed Report Capture Method

**Change:** Switched from file-based (`-o` flag) to stdout-based capture

**Reason:** modelaudit's `-o` flag was unreliable in subprocess context. Capturing from stdout is more reliable.

```python
# Removed -o flag, capture from stdout instead
args = [sys.executable, "-m", "modelaudit", "scan"] + list(paths)
args += ["-f", "json"]  # No -o flag
# ...
report_data = proc.stdout if proc.stdout else None
```

### 3. Fixed Severity Mapping

**Requirement:** 
- modelaudit "critical" → "CRITICAL" (no change)
- modelaudit "warning" → "MEDIUM"
- modelaudit "info" → "INFO" (not "LOW")

**Implementation:**
```python
severity = (iss.get("severity") or iss.get("level") or "info").upper()
# Severity mapping: critical→critical, warning→medium, info→info (no change)
if severity == "WARNING":
    severity = "MEDIUM"
# Keep "CRITICAL" and "INFO" as-is
```

### 4. Added Info Count Tracking

**Change:** Added `info_count` to severity counts (though Scan model doesn't have this field for backward compatibility)

```python
sev_counts = {"critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0, "info_count": 0}
```

### 5. Improved Error Handling and Logging

**Added:**
- Detailed logging for report loading
- Error handling for JSON parsing
- Fallback to stdout if file read fails
- Better error messages for debugging

## Test Results

### Before Fix
- **Findings:** 0
- **Critical:** 0
- **Medium:** 0
- **Info:** 0
- **Status:** PASSED (incorrect)
- **Error:** Read-only filesystem error

### After Fix
- **Findings:** 320
- **Critical:** 16
- **Medium:** 290
- **Info:** 14
- **Status:** FAILED (correct - has critical findings)
- **Severity Mapping:** ✓ Correct (Critical→Critical, Warning→Medium, Info→Info)

## Verification

### YOLO World Mirror Model Scan
```
Scan ID: 36b4fbe7-5f9a-42fc-b4d1-9ad1f543709c
Critical: 16
Medium: 290
Total Findings: 320
Passed: False

Severity Distribution:
  CRITICAL: 16
  MEDIUM: 290
  INFO: 14

Sample Findings:
  1. [CRITICAL] CRITICAL: Malicious code detected: OBJ(25), NEWOBJ(25), BUILD(4), GLOBAL(1) opcodes detected
  2. [INFO] Found 5 network communication patterns...
  3. [MEDIUM] Found NEWOBJ opcode with non-allowlisted class: ultralytics.nn.tasks.WorldModel
```

### Severity Mapping Verification
- ✓ Critical found: True
- ✓ Medium found: True
- ✓ Info found: True
- ✓ Low found: False (correct - info is not mapped to low)

## Files Modified

1. `src/sentrascan/modules/model/scanner.py`
   - Fixed environment variable setup (HOME, XDG_CACHE_HOME)
   - Changed from file-based to stdout-based report capture
   - Fixed severity mapping (info→info, not info→low)
   - Added info_count tracking
   - Improved error handling and logging

## Key Takeaways

1. **Environment Variables Matter:** Setting `HOME` to a writable directory is critical for tools that use `~/.toolname` as fallback
2. **Stdout is More Reliable:** Capturing from stdout is more reliable than file-based output in subprocess contexts
3. **Error Codes:** Exit code 1 = issues found (normal), Exit code 2 = actual error
4. **Severity Mapping:** Must preserve "info" as "info", not map to "low"

## Status

✅ **FIXED** - All findings are now correctly detected, stored, and displayed with proper severity mapping.

