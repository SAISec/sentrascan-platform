# Model Scan Findings Not Being Stored - Debug Issue

## Problem

When scanning the YOLO World Mirror model from Hugging Face, modelaudit correctly detects 320 security issues (including critical pickle and PyTorch vulnerabilities), but these findings are not being stored in the database.

## Root Cause Analysis

### What Works
1. ✅ modelaudit scan executes successfully
2. ✅ Report file is generated with 320 issues
3. ✅ Issues are correctly extracted from the report
4. ✅ Finding objects are created and added to the database session
5. ✅ Transaction is committed

### What Doesn't Work
1. ❌ Findings are not persisted in the database
2. ❌ Scan shows 0 findings even though modelaudit found 320
3. ❌ Scan is marked as "passed" despite critical vulnerabilities

## Investigation Steps

### Step 1: Verify modelaudit Output
```bash
docker compose -f docker-compose.protected.yml exec api \
  /usr/bin/python3 -m modelaudit scan \
  https://huggingface.co/Bingsu/yolo-world-mirror \
  -f json -o /tmp/report.json --strict
```

**Result:** Report contains 320 issues with correct structure:
- `issues` array with 320 items
- Each issue has: `message`, `severity`, `location`, `details`, `timestamp`, `type`
- Severities include: `critical`, `warning`, `info`

### Step 2: Verify Extraction Logic
The code correctly extracts issues:
```python
findings = report.get("issues") or report.get("findings") or []
# Returns 320 items
```

### Step 3: Verify Database Schema
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'findings';
```

**Result:** All columns exist and are correctly typed:
- `evidence` is JSON type (supports dict)
- `tenant_id` is required (correctly passed)
- All required fields are present

### Step 4: Check Database Directly
```sql
SELECT COUNT(*) FROM findings 
WHERE scan_id = '<scan_id>';
```

**Result:** 0 findings in database

## Potential Issues

### Issue 1: Transaction Rollback
The scanner commits the transaction, but FastAPI's dependency injection might be rolling it back after the endpoint returns.

### Issue 2: Exception During Commit
An exception might be raised during `db.commit()` that's being silently caught.

### Issue 3: Session Management
The database session from FastAPI's dependency injection might not be compatible with explicit commits in the scanner.

### Issue 4: Evidence Field Serialization
The `evidence` field is JSON type, and we're passing a dict. SQLAlchemy should handle this, but there might be an issue with complex nested structures.

## Next Steps

1. Add detailed logging around the commit operation
2. Check for exceptions during Finding creation
3. Verify session management between FastAPI and scanner
4. Test with a simpler evidence structure
5. Check if findings are created but not visible due to tenant isolation

## Expected Behavior

When scanning a model with known vulnerabilities:
- modelaudit should detect issues ✅ (working)
- Issues should be extracted from report ✅ (working)
- Finding objects should be created ✅ (working)
- Findings should be stored in database ❌ (NOT working)
- Scan should show correct finding counts ❌ (NOT working)
- Scan should fail if critical findings exist ❌ (NOT working)

## Current Status

**Status:** 🔴 **CRITICAL BUG** - Findings are not being stored despite being detected.

**Impact:** 
- Security scans are not reporting vulnerabilities
- Users see false "PASSED" status for unsafe models
- Critical security issues are not being tracked

**Priority:** **P0 - CRITICAL** - This defeats the purpose of the security scanner.

