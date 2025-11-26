# Container Protection & Obfuscation Guide

This guide covers techniques to protect your Docker container from reverse engineering, preventing customers from:
- Logging into the container
- Inspecting source code
- Understanding internal components
- Modifying the application

## Protection Levels

### Level 1: Basic Protection (Recommended Minimum)
- Remove shells and build tools
- Use distroless/minimal base images
- Remove source code, keep only bytecode
- Read-only filesystem

### Level 2: Intermediate Protection
- Compile Python to standalone executables (PyInstaller/Nuitka)
- Code obfuscation (PyArmor)
- Remove debugging symbols

### Level 3: Advanced Protection
- Encrypted source code with runtime decryption
- License key validation
- Anti-tampering checks
- Encrypted bytecode

---

## Implementation Approaches

### Approach 1: Distroless Image + Bytecode Only (Recommended)

**Pros:** Simple, effective, small image size  
**Cons:** Still possible to decompile bytecode (but harder)

#### Step 1: Create Protected Dockerfile

```dockerfile
# Build stage - compile Python to bytecode
FROM python:3.11-slim AS builder
WORKDIR /build

# Install dependencies
COPY pyproject.toml README.md /build/
RUN pip install --no-cache-dir setuptools wheel

# Copy and compile source code to bytecode
COPY src/ /build/src/
RUN python -m compileall -b /build/src && \
    find /build/src -name "*.py" -delete && \
    find /build/src -name "__pycache__" -type d -exec find {} -name "*.pyc" -exec mv {} {}.pyc \; \; && \
    find /build/src -type d -empty -delete

# Runtime stage - distroless (no shell, no tools)
FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app

# Copy only bytecode and required files
COPY --from=builder /build/src /app/src
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy only necessary binaries (ZAP, gitleaks, etc.)
# Note: You'll need to copy these from builder stage

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Read-only filesystem (except data dirs)
VOLUME ["/data", "/reports", "/sboms", "/cache"]

EXPOSE 8200
ENTRYPOINT ["/usr/bin/python3", "-m", "sentrascan.cli", "server", "--host", "0.0.0.0", "--port", "8200"]
```

**Key protections:**
- ✅ No shell (`/bin/sh`, `/bin/bash` removed)
- ✅ No build tools
- ✅ Source code removed (only `.pyc` files)
- ✅ Minimal attack surface

**Limitations:**
- Bytecode can still be decompiled (but requires effort)
- May need adjustments for dynamic imports

---

### Approach 2: PyInstaller Standalone Executable

**Pros:** Single executable, harder to inspect  
**Cons:** Larger image, slower startup

#### Step 1: Create build script

```python
# scripts/build_standalone.py
import PyInstaller.__main__
import sys
import os

PyInstaller.__main__.run([
    'src/sentrascan/cli.py',
    '--name=sentrascan',
    '--onefile',
    '--hidden-import=fastapi',
    '--hidden-import=uvicorn',
    '--hidden-import=sqlalchemy',
    '--collect-all=sentrascan',
    '--strip',
    '--clean',
])
```

#### Step 2: Dockerfile for PyInstaller

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /build

# Install PyInstaller
RUN pip install --no-cache-dir pyinstaller

# Copy source
COPY . /build/

# Build standalone executable
RUN pyinstaller --onefile --name sentrascan \
    --hidden-import=fastapi \
    --hidden-import=uvicorn \
    --collect-all=sentrascan \
    src/sentrascan/cli.py

# Runtime - distroless
FROM gcr.io/distroless/base-debian12:nonroot
WORKDIR /app

COPY --from=builder /build/dist/sentrascan /app/sentrascan
# Copy other required binaries/files

EXPOSE 8200
ENTRYPOINT ["/app/sentrascan", "server", "--host", "0.0.0.0", "--port", "8200"]
```

---

### Approach 3: PyArmor Obfuscation

**Pros:** Strong obfuscation, runtime protection  
**Cons:** Requires license for commercial use, slight performance overhead

#### Step 1: Obfuscate code before building

```dockerfile
FROM python:3.11-slim AS obfuscator
WORKDIR /build

# Install PyArmor
RUN pip install --no-cache-dir pyarmor

# Copy source
COPY src/ /build/src/

# Obfuscate Python code
RUN pyarmor gen --recursive \
    --restrict-mode 4 \
    --enable-rft \
    --mix-str \
    /build/src

FROM python:3.11-slim AS builder
WORKDIR /build

# Copy obfuscated code
COPY --from=obfuscator /build/src /build/src
COPY pyproject.toml /build/

# Install and compile
RUN pip install --no-cache-dir -e .

# Runtime stage
FROM gcr.io/distroless/python3-debian12:nonroot
# ... rest of setup
```

---

### Approach 4: Nuitka Compilation (C Extension)

**Pros:** Native binary, very hard to reverse engineer  
**Cons:** Complex build, larger binaries

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /build

RUN apt-get update && apt-get install -y gcc g++ && \
    pip install --no-cache-dir nuitka

COPY . /build/

# Compile to standalone
RUN python -m nuitka \
    --standalone \
    --onefile \
    --include-module=sentrascan \
    src/sentrascan/cli.py

FROM gcr.io/distroless/base-debian12:nonroot
COPY --from=builder /build/cli.bin /app/sentrascan
# ...
```

---

## Complete Protected Dockerfile Example

Here's a production-ready protected Dockerfile combining multiple techniques:

```dockerfile
# ============================================
# Stage 1: Build wheels and dependencies
# ============================================
FROM python:3.11-slim AS wheels
WORKDIR /wheels
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ make && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir wheel
RUN pip wheel --no-cache-dir mcp-checkpoint cisco-ai-mcp-scanner -w /wheels

# ============================================
# Stage 2: Compile source to bytecode
# ============================================
FROM python:3.11-slim AS compiler
WORKDIR /build

# Install dependencies
COPY pyproject.toml README.md /build/
COPY --from=wheels /wheels /wheels
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir semgrep && \
    pip install --no-cache-dir /wheels/* && \
    pip install --no-cache-dir 'mcp>=1.0.0' || true

# Copy source and compile to bytecode
COPY src/ /build/src/
RUN python -m compileall -b /build/src && \
    find /build/src -name "*.py" -type f -delete && \
    find /build/src -name "__pycache__" -type d -exec sh -c 'find "$1" -name "*.pyc" -exec mv {} "$(dirname {}).pyc" \;' _ {} \; && \
    find /build/src -type d -empty -delete

# Install package (will use bytecode)
RUN pip install --no-cache-dir -e .

# Install system tools (ZAP, gitleaks, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tar gzip default-jre-headless \
    libharfbuzz0b libfontconfig1 libfreetype6 && \
    rm -rf /var/lib/apt/lists/*

# Install ZAP
ARG ZAP_VERSION=2.15.0
RUN curl -fsSL -o /tmp/zap.sh \
    "https://github.com/zaproxy/zaproxy/releases/download/v${ZAP_VERSION}/ZAP_2_15_0_unix.sh" && \
    chmod +x /tmp/zap.sh && \
    /tmp/zap.sh -q -dir /opt/zap && \
    rm -f /tmp/zap.sh

# Install gitleaks and trufflehog
ARG GITLEAKS_VERSION=8.18.1
ARG TRUFFLEHOG_VERSION=3.78.0
RUN arch="$(uname -m)" && \
    if [ "$arch" = "x86_64" ] || [ "$arch" = "amd64" ]; then \
        gl_arch="linux_x64"; th_arch="linux_amd64"; \
    elif [ "$arch" = "aarch64" ] || [ "$arch" = "arm64" ]; then \
        gl_arch="linux_arm64"; th_arch="linux_arm64"; \
    else gl_arch="linux_x64"; th_arch="linux_amd64"; fi && \
    curl -fsSL -o /tmp/gitleaks.tgz \
        "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_${gl_arch}.tar.gz" && \
    tar -C /usr/local/bin -xzf /tmp/gitleaks.tgz gitleaks && \
    chmod +x /usr/local/bin/gitleaks && \
    rm -f /tmp/gitleaks.tgz && \
    curl -fsSL -o /tmp/trufflehog.tgz \
        "https://github.com/trufflesecurity/trufflehog/releases/download/v${TRUFFLEHOG_VERSION}/trufflehog_${TRUFFLEHOG_VERSION}_${th_arch}.tar.gz" && \
    tar -C /usr/local/bin -xzf /tmp/trufflehog.tgz trufflehog && \
    chmod +x /usr/local/bin/trufflehog && \
    rm -f /tmp/trufflehog.tgz

# ============================================
# Stage 3: Runtime (Distroless - No Shell)
# ============================================
FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app

# Copy only bytecode and runtime files
COPY --from=compiler --chown=nonroot:nonroot \
    /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=compiler --chown=nonroot:nonroot \
    /usr/local/bin /usr/local/bin
COPY --from=compiler --chown=nonroot:nonroot \
    /build/src /app/src

# Copy system tools
COPY --from=compiler --chown=nonroot:nonroot \
    /opt/zap /opt/zap

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/usr/local/bin:/opt/zap:${PATH}"

# Create writable directories (read-only filesystem except these)
VOLUME ["/data", "/reports", "/sboms", "/cache"]

EXPOSE 8200
USER nonroot

# Entrypoint (no shell available)
ENTRYPOINT ["/usr/bin/python3", "-m", "sentrascan.cli", "server", "--host", "0.0.0.0", "--port", "8200"]
```

---

## Additional Security Hardening

### 1. Remove Shell Access in docker-compose.yml

```yaml
services:
  api:
    # ... other config ...
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /var/tmp
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only if needed for binding ports < 1024
```

### 2. Runtime Protection Script

Add anti-tampering checks:

```python
# src/sentrascan/core/protection.py
import os
import sys
import hashlib

def verify_integrity():
    """Check if critical files have been modified"""
    critical_files = [
        '/app/src/sentrascan/server.py',
        '/app/src/sentrascan/core/models.py',
    ]
    
    # Compare file hashes (pre-computed during build)
    expected_hashes = {
        # Add hashes here
    }
    
    for filepath in critical_files:
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
                if filepath in expected_hashes:
                    if actual_hash != expected_hashes[filepath]:
                        sys.exit(1)  # Tampering detected
```

### 3. License Key Validation

```python
# src/sentrascan/core/license.py
import os
from datetime import datetime

def validate_license():
    license_key = os.getenv('SENTRASCAN_LICENSE_KEY')
    if not license_key:
        raise RuntimeError("License key required")
    
    # Validate against your license server or local validation
    # ...
```

---

## Testing Protection

### Verify No Shell Access

```bash
# This should FAIL in protected container
docker compose exec api /bin/sh
# Error: OCI runtime exec failed: exec failed: unable to start container process: exec "/bin/sh": stat /bin/sh: no such file or directory

# This should also FAIL
docker compose exec api /bin/bash
docker compose exec api python -c "import os; os.system('ls')"
```

### Verify Source Code Removal

```bash
# Check that .py files are gone
docker compose exec api find /app/src -name "*.py"
# Should return nothing

# Check that only .pyc exists
docker compose exec api find /app/src -name "*.pyc"
# Should show compiled bytecode files
```

### Verify Read-Only Filesystem

```bash
# Try to modify a file (should fail)
docker compose exec api touch /app/test.txt
# Error: Read-only file system
```

---

## Trade-offs & Considerations

| Approach | Protection Level | Complexity | Image Size | Performance Impact |
|----------|-----------------|------------|------------|-------------------|
| Bytecode Only | Medium | Low | Small | None |
| PyInstaller | High | Medium | Large | Startup delay |
| PyArmor | High | Medium | Small | ~5-10% overhead |
| Nuitka | Very High | High | Medium | None |
| Distroless | Medium | Low | Small | None |

**Recommendation:** Start with **Approach 1 (Distroless + Bytecode)** for good protection with minimal complexity.

---

## Limitations & Reality Check

⚠️ **Important:** Complete protection is impossible. Determined attackers can:
- Extract and analyze bytecode
- Reverse engineer binaries
- Use debuggers and memory dumps
- Analyze network traffic

**Best practices:**
1. Use multiple layers of protection
2. Focus on making reverse engineering expensive/time-consuming
3. Implement license validation
4. Monitor for tampering
5. Use legal protection (licenses, contracts)

---

## Migration Steps

1. **Test locally first:**
   ```bash
   docker build -f Dockerfile.protected -t sentrascan:protected .
   docker run --rm sentrascan:protected sentrascan --version
   ```

2. **Verify functionality:**
   - All CLI commands work
   - Server starts correctly
   - API endpoints respond
   - Scans execute properly

3. **Performance testing:**
   - Compare startup time
   - Compare scan execution time
   - Monitor memory usage

4. **Deploy to staging:**
   - Test with real workloads
   - Verify all features work

5. **Production deployment:**
   - Tag as production image
   - Update docker-compose.yml
   - Monitor for issues

---

## References

- [Distroless Images](https://github.com/GoogleContainerTools/distroless)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [PyArmor Documentation](https://pyarmor.readthedocs.io/)
- [Nuitka Documentation](https://nuitka.net/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

