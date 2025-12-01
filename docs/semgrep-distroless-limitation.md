# Semgrep Limitation in Distroless Containers

## Issue

Semgrep does not function correctly in distroless containers due to missing Python shared libraries.

## Root Cause

Semgrep is a Python-based static analysis tool that requires Python shared libraries (specifically `libpython3.11.so.1.0`) to execute. Distroless containers are minimal images that do not include these runtime libraries, only the Python interpreter binary.

When Semgrep is executed in a distroless container, it fails with:
```
error while loading shared libraries: libpython3.11.so.1.0: cannot open shared object file: No such file or directory
```

## Impact

- **MCP Scans**: Semgrep-based SAST scanning is unavailable in the protected/distroless container image
- **Model Scans**: Semgrep is not used for model scans, so no impact
- **Alternative Scanners**: Code Rules, Gitleaks, TruffleHog, and MCP-specific scanners continue to function

## Workarounds

### Option 1: Use Non-Distroless Base Image (Recommended for Development)

If Semgrep is required, use a non-distroless base image that includes Python shared libraries:

```dockerfile
FROM python:3.11-slim
# ... rest of Dockerfile
```

**Trade-offs:**
- ✅ Semgrep works
- ❌ Larger image size
- ❌ More attack surface (includes shell and additional tools)

### Option 2: Use Semgrep via Separate Container/Service

Run Semgrep in a separate container or service that has the required dependencies:

```yaml
services:
  semgrep:
    image: returntocorp/semgrep:latest
    # ... configuration
```

**Trade-offs:**
- ✅ Maintains distroless security benefits
- ✅ Semgrep works
- ❌ Additional infrastructure complexity

### Option 3: Use Alternative SAST Tools

Use statically compiled SAST tools that don't require Python shared libraries:

- **CodeQL** (if available)
- **Bandit** (also Python-based, same issue)
- **Custom regex-based rules** (already implemented as "Code Rules")

**Trade-offs:**
- ✅ Works in distroless containers
- ❌ Different feature set than Semgrep
- ❌ May require custom rule development

## Current Implementation

The `SASTRunner` class in `src/sentrascan/modules/mcp/sast.py` includes:

1. **Availability Check**: Detects if Semgrep is available and functional
2. **Graceful Degradation**: If Semgrep is unavailable, scanning continues with other tools
3. **Documentation**: Code comments explain the limitation

## Detection

The system automatically detects Semgrep unavailability:

```python
def available(self) -> bool:
    """
    Check if Semgrep is available.
    
    NOTE: Semgrep requires Python shared libraries which are not available
    in distroless containers. Semgrep will not work in the protected/distroless
    container image. This is a known limitation.
    """
    # ... implementation checks for library errors
```

## Future Improvements

1. **Statically Compiled Semgrep**: If Semgrep releases a statically compiled binary, update the Dockerfile to use it
2. **Semgrep API**: Use Semgrep's API/CLI in a separate service
3. **Alternative SAST**: Evaluate and integrate alternative SAST tools that work in distroless containers

## References

- [Semgrep Documentation](https://semgrep.dev/docs/)
- [Distroless Images](https://github.com/GoogleContainerTools/distroless)
- [Python Shared Libraries](https://docs.python.org/3/c-api/intro.html#compilation-and-linkage)

