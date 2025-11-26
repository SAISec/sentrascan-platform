# Container Protection Quick Start

Quick reference for protecting your SentraScan container from inspection.

## Quick Build & Test

### 1. Build Protected Image

```bash
docker build -f Dockerfile.protected -t sentrascan:protected .
```

### 2. Test Protection

```bash
# Try to access shell (should FAIL)
docker run --rm sentrascan:protected /bin/sh
# Error: stat /bin/sh: no such file or directory

# Try to list source files (should show NO .py files)
docker run --rm sentrascan:protected find /app/src -name "*.py"
# Should return nothing

# Verify bytecode exists
docker run --rm sentrascan:protected find /app/src -name "*.pyc"
# Should show compiled bytecode files
```

### 3. Run Protected Container

```bash
# Using docker-compose
docker compose -f docker-compose.protected.yml up

# Or manually
docker run -d \
  --name sentrascan-protected \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /var/tmp \
  -p 8200:8200 \
  sentrascan:protected
```

## Verification Checklist

- [ ] No shell access (`/bin/sh`, `/bin/bash` not available)
- [ ] Source code removed (no `.py` files in `/app/src`)
- [ ] Only bytecode present (`.pyc` files exist)
- [ ] Read-only filesystem (except data volumes)
- [ ] Application runs correctly
- [ ] All features work (scans, API, UI)

## What Gets Protected

✅ **Protected:**
- Source code (removed, only bytecode)
- Shell access (distroless = no shell)
- Build tools (removed from runtime)
- File system (read-only)

⚠️ **Still Possible (but harder):**
- Bytecode decompilation (requires tools)
- Memory analysis (requires expertise)
- Network traffic analysis

## Troubleshooting

### Issue: Application won't start

**Solution:** Check if all dependencies are copied correctly:
```bash
docker run --rm sentrascan:protected python3 -c "import sentrascan; print('OK')"
```

### Issue: Dynamic imports fail

**Solution:** Some Python code uses dynamic imports. You may need to:
1. Pre-import modules in your code
2. Use PyInstaller instead of bytecode-only
3. Keep some `.py` files for dynamic imports

### Issue: Need to debug

**Solution:** Use the regular Dockerfile for development:
```bash
docker build -f Dockerfile -t sentrascan:dev .
```

## Next Steps

For advanced protection, see [CONTAINER-PROTECTION.md](./CONTAINER-PROTECTION.md):
- PyArmor obfuscation
- PyInstaller standalone
- Nuitka compilation
- License validation

