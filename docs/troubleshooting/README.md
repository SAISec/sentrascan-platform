# Troubleshooting Guide

Solutions to common issues and problems.

## Table of Contents

1. [Authentication Issues](#authentication-issues)
2. [Scan Failures](#scan-failures)
3. [API Errors](#api-errors)
4. [Performance Issues](#performance-issues)
5. [Database Issues](#database-issues)
6. [UI Issues](#ui-issues)
7. [Export Issues](#export-issues)
8. [ML Insights Issues](#ml-insights-issues)

## Authentication Issues

### Cannot Log In

**Symptoms**: Login fails with "Invalid credentials" error.

**Solutions**:
1. Verify email and password are correct
2. Check for typos (case-sensitive)
3. Try password reset if forgotten
4. Verify account is not locked (too many failed attempts)
5. Check if account is deactivated (contact admin)

### API Key Not Working

**Symptoms**: API requests return 401 Unauthorized.

**Solutions**:
1. Verify API key format: `ss-proj-h_<147-chars>`
2. Check if key is revoked (create new key)
3. Ensure `X-API-Key` header is used (not `x-api-key`)
4. Verify key hasn't expired
5. Check key belongs to active tenant

### MFA Code Not Working

**Symptoms**: MFA verification fails.

**Solutions**:
1. Ensure time is synchronized on device
2. Check authenticator app is working
3. Try generating new code (codes expire every 30 seconds)
4. Verify correct account in authenticator app
5. Re-scan QR code if needed

### Session Expired

**Symptoms**: Logged out unexpectedly.

**Solutions**:
1. Default session timeout is 48 hours
2. Log in again to create new session
3. Check browser cookies are enabled
4. Clear cookies and try again if persistent

## Scan Failures

### Scan Times Out

**Symptoms**: Scan doesn't complete, timeout error.

**Solutions**:
1. Increase timeout in scan settings
2. Check if target files are very large
3. Verify network connectivity
4. Check server resources (CPU, memory)
5. Try scanning smaller subsets

### No Findings Detected

**Symptoms**: Scan completes but shows zero findings.

**Possible Causes**:
1. Target files are actually secure (good!)
2. Scanners not enabled for tenant
3. Policy too permissive
4. Scan didn't access target files

**Solutions**:
1. Verify scanners are enabled in tenant settings
2. Check scan logs for errors
3. Verify file paths are correct
4. Try different scan type
5. Review policy configuration

### Scan Returns Errors

**Symptoms**: Scan fails with error message.

**Common Errors**:

**"File not found"**:
- Verify file paths are correct
- Check file permissions
- Ensure files exist

**"Permission denied"**:
- Check file/directory permissions
- Run with appropriate user permissions
- Verify API key has scan.create permission

**"Invalid format"**:
- Verify file format is supported
- Check file isn't corrupted
- Try different file format

### Auto-Discovery Not Finding Configs

**Symptoms**: Auto-discovery returns no results.

**Solutions**:
1. Check common locations exist:
   - `~/.cursor/mcp.json`
   - `~/Library/Application Support/Claude/`
   - `~/.vscode/mcp.json`
2. Verify file permissions allow reading
3. Use manual paths instead
4. Check logs for discovery errors

## API Errors

### 403 Forbidden

**Symptoms**: API returns 403 even with valid API key.

**Solutions**:
1. Check API key role/permissions
2. Verify required permission for endpoint
3. Check if tenant is active
4. Verify user account is active
5. Review RBAC configuration

### 404 Not Found

**Symptoms**: Endpoint returns 404.

**Solutions**:
1. Verify endpoint URL is correct
2. Check API version (`/api/v1/`)
3. Verify resource ID exists
4. Check tenant context (resource may belong to different tenant)

### 422 Validation Error

**Symptoms**: Request returns 422 with validation details.

**Solutions**:
1. Review error message for specific validation failures
2. Check required fields are provided
3. Verify data types match expected format
4. Check value constraints (min/max, enums)
5. Review API documentation for correct format

### 429 Rate Limit Exceeded

**Symptoms**: Too many requests error.

**Solutions**:
1. Wait for rate limit window to reset
2. Reduce request frequency
3. Implement exponential backoff
4. Use batch endpoints when available
5. Contact admin to increase limits if needed

## Performance Issues

### Slow Scan Execution

**Symptoms**: Scans take very long to complete.

**Solutions**:
1. Check server CPU and memory usage
2. Reduce scan scope (fewer files)
3. Increase scanner timeout if needed
4. Run scans during off-peak hours
5. Consider horizontal scaling

### Dashboard Loading Slowly

**Symptoms**: Dashboard takes long to load.

**Solutions**:
1. Reduce time range for analytics
2. Check database query performance
3. Verify database indexes exist
4. Clear browser cache
5. Check network latency

### Analytics Export Slow

**Symptoms**: Export takes long to generate.

**Solutions**:
1. Reduce time range
2. Select fewer data categories
3. Use CSV instead of PDF (faster)
4. Export during off-peak hours
5. Check server resources

## Database Issues

### Connection Errors

**Symptoms**: Database connection failures.

**Solutions**:
1. Verify `DATABASE_URL` environment variable
2. Check database server is running
3. Verify network connectivity
4. Check database credentials
5. Review database logs

### Migration Errors

**Symptoms**: Database schema errors.

**Solutions**:
1. Run database migrations: `python -m sentrascan.cli db migrate`
2. Check migration logs
3. Verify database version compatibility
4. Backup database before migrations
5. Contact support if persistent

### Data Not Appearing

**Symptoms**: Data created but not visible.

**Solutions**:
1. Check tenant context (data may be in different tenant)
2. Verify user has access to tenant
3. Check data filters
4. Verify database transaction committed
5. Check for soft-deleted records

## UI Issues

### Charts Not Displaying

**Symptoms**: Analytics charts don't render.

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify Chart.js library loaded
3. Clear browser cache
4. Try different browser
5. Check network tab for failed requests

### Forms Not Submitting

**Symptoms**: Form submission doesn't work.

**Solutions**:
1. Check browser console for errors
2. Verify required fields are filled
3. Check CSRF token (if applicable)
4. Try disabling browser extensions
5. Clear browser cache and cookies

### Styling Issues

**Symptoms**: UI looks broken or unstyled.

**Solutions**:
1. Clear browser cache
2. Hard refresh (Ctrl+F5 or Cmd+Shift+R)
3. Check CSS files are loading
4. Verify browser compatibility
5. Try different browser

## Export Issues

### CSV Export Empty

**Symptoms**: CSV file has no data.

**Solutions**:
1. Verify data exists for selected time range
2. Check filters aren't too restrictive
3. Verify export permissions
4. Try JSON export to compare
5. Check server logs for errors

### PDF Export Fails

**Symptoms**: PDF export returns error.

**Solutions**:
1. Verify ReportLab is installed: `pip install reportlab`
2. Check server has write permissions
3. Try CSV or JSON export instead
4. Check server logs for specific error
5. Verify sufficient disk space

### Export File Corrupted

**Symptoms**: Exported file can't be opened.

**Solutions**:
1. Verify file download completed
2. Check file size matches expected
3. Try exporting again
4. Use different format (CSV vs JSON)
5. Check browser download settings

## ML Insights Issues

### ML Insights Not Available

**Symptoms**: ML insights panel doesn't appear or shows "not enabled".

**Solutions**:
1. Set `ML_INSIGHTS_ENABLED=true` environment variable
2. Install scikit-learn: `pip install scikit-learn`
3. Restart server after installation
4. Check `/api/v1/ml-insights/status` endpoint
5. Verify scipy is installed (dependency)

### Anomaly Detection Not Working

**Symptoms**: Anomaly detection returns no results or errors.

**Solutions**:
1. Ensure at least 2 scans exist for analysis
2. Check ML insights are enabled
3. Verify scikit-learn is installed
4. Review server logs for errors
5. Try different time range

### Correlation Analysis Fails

**Symptoms**: Correlation analysis returns errors.

**Solutions**:
1. Ensure sufficient findings exist (at least 10)
2. Check scipy is installed
3. Verify data has variation (not all same values)
4. Review server logs
5. Try different time range

## Getting Additional Help

If you continue to experience issues:

1. **Check Logs**: Review server logs for detailed error messages
2. **Review Documentation**: See [User Guide](../user-guide/README.md) and [FAQ](../faq/README.md)
3. **Contact Support**: Reach out with:
   - Error messages
   - Steps to reproduce
   - Log excerpts
   - System information

## Common Error Messages

### "Tenant not found"
- Verify tenant ID is correct
- Check tenant is active
- Ensure user has access to tenant

### "Permission denied"
- Check user role and permissions
- Verify API key permissions
- Review RBAC configuration

### "Invalid API key format"
- Verify key starts with `ss-proj-h_`
- Check key is 158 characters total
- Ensure key hasn't been modified

### "Session expired"
- Log in again
- Check session timeout settings
- Verify cookies are enabled

### "Database connection failed"
- Check `DATABASE_URL` environment variable
- Verify database server is running
- Check network connectivity

