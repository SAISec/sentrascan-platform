# Model Security Scanning Tools - Analysis Documentation

This directory contains comprehensive analysis of open-source ML model security scanning tools for developing the **SentraScan-Model** product.

---

## 📋 Document Index

### 1. **[UPDATED-MODEL-ONLY-ANALYSIS.md](./UPDATED-MODEL-ONLY-ANALYSIS.md)** ⭐⭐ **START HERE (LATEST)**
   **Updated analysis focusing on model scanning only + SBOM**
   
   - Executive summary with modelaudit discovery
   - Tool comparison matrix (5 tools: modelaudit, modelscan, picklescan, model-unpickler, watchtower)
   - 30 scanners via modelaudit (vs 5 in modelscan)
   - Built-in SBOM generation (CycloneDX 1.6)
   - Excludes: notebooks, secrets, PII scanning
   - Includes: Dependency analysis
   - Simplified architecture (modelaudit primary)
   - 18-week implementation roadmap
   - Risk assessment & success metrics

### 2. **[MODEL-SCANNING-ANALYSIS-SUMMARY.md](./MODEL-SCANNING-ANALYSIS-SUMMARY.md)** ⭐ (SUPERSEDED)
   **Original comprehensive analysis (includes notebooks/secrets)**
   
   - Executive summary
   - Tool comparison matrix (4 tools analyzed)
   - Detailed strengths/weaknesses analysis
   - Feature coverage comparison
   - Licensing analysis
   - Architecture recommendations
   - Technology stack recommendations
   - Implementation roadmap (3 phases, 18 weeks)
   - Risk assessment
   - Success metrics
   - **Note**: This version includes notebooks/secrets scanning (now excluded)

### 3. **[01-picklescan-factsheet.md](./01-picklescan-factsheet.md)**
   **Detailed fact sheet for picklescan**
   
   - Lightweight Python pickle scanner
   - MIT License
   - Excellent Hugging Face integration
   - Pure Python, zero dependencies
   - Best for: Pickle-specific scanning

---

## 🎯 Quick Summary

### Tools Analyzed

1. **modelaudit** (Promptfoo) ⭐⭐⭐ **NEW - RECOMMENDED PRIMARY**
   - License: MIT
   - Focus: 30 scanners + SBOM generation (CycloneDX)
   - Rating: ⭐⭐⭐⭐⭐ (Most comprehensive + SBOM built-in)
   - Version: 0.2.17 (PyPI)

2. **modelscan** (Protect AI)
   - License: Apache 2.0
   - Focus: Multi-format (Pickle, H5, SavedModel)
   - Rating: ⭐⭐⭐⭐ (Good H5/SavedModel depth)

3. **picklescan** (Matthieu Maitre/Microsoft)
   - License: MIT
   - Focus: Python Pickle files
   - Rating: ⭐⭐⭐⭐ (Excellent for pickle)

4. **model-unpickler** (Goeckslab)
   - License: MIT
   - Focus: Safe loading library (not scanner)
   - Rating: ⭐⭐ (Research-level)

5. **watchtower** (Bosch AIShield) - EXCLUDED
   - License: Apache 2.0
   - Focus: Comprehensive (models + notebooks + secrets)
   - Rating: ⭐⭐⭐⭐ (Most features)
   - **Note**: Excluded per requirements (no notebooks/secrets/PII)

### Final Recommendation ⚡ UPDATED

**Build SentraScan-Model using:**
- **Primary**: **modelaudit** (30 scanners + SBOM built-in)
- **Secondary**: modelscan (optional, H5/SavedModel depth)
- **Optional**: picklescan (Hugging Face direct integration)
- **Excluded**: Watchtower (notebooks/secrets/PII not needed)

---

## 🏗️ Recommended Architecture ⚡ UPDATED

```
SentraScan-Model Platform
│
├── Primary Engine: modelaudit
│   ├── 30 scanners (Pickle, H5, ONNX, GGUF, etc.)
│   ├── SBOM generation (CycloneDX 1.6)
│   ├── Smart detection & auto-config
│   └── Fickling integration (pickle)
│
├── Enhancement Engines (Optional)
│   ├── modelscan (H5/SavedModel depth)
│   └── picklescan (Hugging Face direct)
│
├── Orchestrator & Policy Engine
│
└── Report Generator
    ├── JSON
    ├── SARIF
    ├── CycloneDX SBOM
    └── Markdown
```

---

## 📦 Cloned Repositories

All repositories have been cloned to:
```
/Users/mp/Documents/02_DevSpace/02_experiments/14_sentrascan_modules/
├── picklescan/
├── modelscan/
├── model-unpickler/
└── watchtower/

Note: modelaudit installed via PyPI (no public GitHub repository)
```

---

## 🚀 Next Steps ⚡ UPDATED

1. **Read**: [UPDATED-MODEL-ONLY-ANALYSIS.md](./UPDATED-MODEL-ONLY-ANALYSIS.md) for latest analysis ⭐
2. **Review**: modelaudit (30 scanners + SBOM) as primary engine
3. **Test**: Install modelaudit and run `modelaudit doctor`
4. **Approve**: Technology stack (modelaudit + optional modelscan/picklescan)
5. **Proceed**: Create Product Requirements Document (PRD) for SentraScan-Model
6. **Implement**: Follow 18-week roadmap (3 phases x 6 weeks)

---

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| **Tools Analyzed** | 5 (modelaudit, modelscan, picklescan, model-unpickler, watchtower) |
| **Repositories Cloned** | 4 (+ modelaudit via PyPI) |
| **Documentation Pages** | 3 (2 summaries + 1 fact sheet) |
| **Total Analysis Lines** | 1,500+ |
| **Licenses Reviewed** | MIT, Apache 2.0 |
| **Scanners Available** | 30 (via modelaudit) |
| **SBOM Format** | CycloneDX 1.6 built-in |
| **Recommended Stack** | **modelaudit** (primary) + modelscan (optional) + picklescan (optional) |

---

## 🔗 External Resources

- **modelaudit**: https://pypi.org/project/modelaudit (no public GitHub)
- **picklescan**: https://github.com/mmaitre314/picklescan
- **modelscan**: https://github.com/protectai/modelscan
- **model-unpickler**: https://github.com/goeckslab/model-unpickler
- **watchtower**: https://github.com/bosch-aisecurity-aishield/watchtower

---

## 📝 Notes

- **modelaudit** (PyPI) discovered in updated analysis - 30 scanners + SBOM ⭐
- **watchtower** excluded per requirements (no notebooks/secrets/PII scanning)
- All licenses (MIT + Apache 2.0) are compatible for commercial use
- Recommend Apache 2.0 for final SentraScan-Model product (stronger patent protection)
- **SBOM generation** is built into modelaudit (CycloneDX 1.6)

---

**Status**: ✅ Analysis Complete - Ready for PRD Development  
**Date**: January 2025  
**Primary Engine**: **modelaudit** (30 scanners + SBOM built-in)  
**Next Document**: Product Requirements Document for SentraScan-Model
