# Docker Build Optimization Guide

This document explains how Docker builds are optimized for fast incremental builds during development.

## Build Optimization Strategy

### Layer Caching Order

The Dockerfile is structured to maximize layer caching:

1. **System Dependencies** (lines 14-18)
   - Installed first, rarely change
   - Cached unless base image changes

2. **External Tools** (lines 20-46)
   - ZAP, uv, gitleaks, trufflehog
   - Cached unless tool versions change

3. **Python Dependencies** (lines 48-57)
   - `pyproject.toml` copied first
   - Dependencies installed before source code
   - **This layer is cached unless dependencies change**

4. **Test Dependencies** (lines 59-64)
   - Playwright and browsers
   - Cached separately

5. **Source Code** (lines 66-68)
   - Copied LAST
   - **Only this layer rebuilds when code changes**

### Key Optimizations

1. **Dependency Files Copied First**
   ```dockerfile
   COPY pyproject.toml README.md /app/
   RUN pip install -e .
   ```
   Dependencies are installed before source code, so dependency installation is cached.

2. **Source Code Copied Last**
   ```dockerfile
   COPY src/ /app/src/
   COPY tests/ /app/tests/
   ```
   Code changes only invalidate the final layer.

3. **.dockerignore File**
   - Excludes unnecessary files from build context
   - Reduces build context size
   - Speeds up COPY operations

## Development Workflows

### Option 1: Incremental Builds (Recommended for Testing)

For quick iteration when testing changes:

```bash
# Build with BuildKit for better caching
make docker-build-fast

# Or use standard build (also uses cache)
make docker-build
```

**When to rebuild:**
- ✅ Code changes in `src/` or `tests/` → Only final layer rebuilds (~seconds)
- ✅ Dependency changes in `pyproject.toml` → Dependency layer rebuilds (~minutes)
- ✅ System/tool changes → Full rebuild (~10+ minutes)

**Build time examples:**
- First build: ~15-20 minutes
- Code-only change: ~30-60 seconds
- Dependency change: ~5-10 minutes

### Option 2: Development Mode with Volume Mounts (Fastest Iteration)

For live code reloading without rebuilds:

```bash
# Start in development mode
make docker-up-dev

# Make code changes - they're immediately available!
# No rebuild needed
```

**How it works:**
- Source code is mounted as volumes
- Changes in `src/` and `tests/` are immediately reflected
- No Docker rebuild required
- Perfect for rapid development

**Limitations:**
- Some Python packages may need container restart
- Not suitable for production builds

### Option 3: Hybrid Approach

1. Build base image once:
   ```bash
   make docker-build-fast
   ```

2. Use dev mode for iteration:
   ```bash
   make docker-up-dev
   ```

3. Rebuild only when dependencies change:
   ```bash
   # After changing pyproject.toml
   make docker-build-fast
   make docker-up
   ```

## Build Performance Tips

### 1. Use BuildKit

BuildKit provides better caching and parallel builds:

```bash
export DOCKER_BUILDKIT=1
make docker-build-fast
```

Or set it permanently:
```bash
echo 'export DOCKER_BUILDKIT=1' >> ~/.zshrc
```

### 2. Check Build Cache

See what layers are cached:
```bash
docker build --progress=plain -t sentrascan/platform:dev .
```

### 3. Prune Unused Cache

If cache gets too large:
```bash
docker builder prune
```

### 4. Use .dockerignore

Ensure `.dockerignore` excludes:
- Git files
- IDE files
- Test artifacts
- Build artifacts
- Data directories

## Troubleshooting

### Build Still Slow?

1. **Check if cache is being used:**
   ```bash
   docker build --progress=plain -t sentrascan/platform:dev . 2>&1 | grep "CACHED"
   ```

2. **Verify .dockerignore:**
   ```bash
   docker build --no-cache -t sentrascan/platform:dev .
   # Compare build context size
   ```

3. **Check for unnecessary COPY operations:**
   - Ensure code is copied last
   - Verify dependency files are copied before code

### Code Changes Not Reflected?

1. **In standard mode:**
   - Rebuild: `make docker-build-fast`
   - Restart: `make docker-down && make docker-up`

2. **In dev mode:**
   - Check volume mounts: `docker compose -f docker-compose.yml -f docker-compose.dev.yml config`
   - Restart container: `docker compose restart api`

## Best Practices

1. **For Development:**
   - Use `docker-up-dev` for rapid iteration
   - Rebuild only when dependencies change

2. **For Testing:**
   - Use `docker-build-fast` for incremental builds
   - Cache is preserved between builds

3. **For CI/CD:**
   - Use `docker-build` (standard build)
   - Consider multi-stage builds for smaller images

4. **For Production:**
   - Always do full rebuilds
   - Tag images with version numbers
   - Use multi-arch builds if needed

## Summary

- **Code changes**: ~30-60 seconds (only final layer)
- **Dependency changes**: ~5-10 minutes (dependency layer)
- **Full rebuild**: ~15-20 minutes (all layers)

Use `docker-up-dev` for fastest iteration during development!

