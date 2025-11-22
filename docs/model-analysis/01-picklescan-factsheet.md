# Picklescan - Fact Sheet

## Overview

| Attribute | Value |
|-----------|-------|
| **Project Name** | picklescan |
| **Author** | Matthieu Maitre (Microsoft) |
| **Version** | 0.0.32 |
| **License** | MIT License |
| **Repository** | https://github.com/mmaitre314/picklescan |
| **Language** | Python |
| **Python Requirement** | ≥3.9 |
| **Last Update** | Active (2024) |
| **Stars** | ~600+ |
| **Maturity** | Stable |

---

## Purpose

Security scanner specifically designed to detect Python Pickle files that perform suspicious or malicious actions during deserialization. Focused on identifying arbitrary code execution vulnerabilities in serialized ML models.

---

## Key Features

### 1. **Pickle Bytecode Analysis**
- Static analysis of pickle bytecode without executing the file
- Scans for dangerous global imports (e.g., `eval`, `exec`, `os.system`)
- Detects suspicious opcode patterns

### 2. **Multiple Input Sources**
- **Local files**: Single file or directory scanning
- **Remote URLs**: Direct HTTP/HTTPS URL scanning
- **Hugging Face**: Direct integration with Hugging Face model hub
- **Zip archives**: Scans PyTorch `.bin` files (zip format internally)
- **NumPy files**: Supports `.npy` file scanning (with numpy installed)

### 3. **Format Support**
| Format | Support | Notes |
|--------|---------|-------|
| `.pkl` | ✅ | Standard pickle format |
| `.bin` | ✅ | PyTorch models (zip with pickle inside) |
| `.pth` | ✅ | PyTorch checkpoint format |
| `.npy` | ✅ | NumPy array format (requires numpy) |
| `.pt` | ✅ | PyTorch tensors |
| `.h5` | ❌ | Not supported |
| `.pb` | ❌ | Not supported |

### 4. **Detection Capabilities**
- **Dangerous Globals**: `eval`, `exec`, `compile`, `os.system`, `subprocess`, `__builtin__`, etc.
- **Code Injection**: Embedded Python code in pickle streams
- **Import Abuse**: Suspicious module imports
- **Filesystem Access**: File read/write operations

### 5. **Output & Reporting**
- Clear terminal output with file path and findings
- Scan summary: total files, infected files, dangerous globals
- Exit codes: 0 (clean), 1 (malware found), 2 (error)

---

## Architecture

```
picklescan/
├── scanner.py          # Core scanning logic
├── torch.py            # PyTorch-specific handling
├── relaxed_zipfile.py  # Zip file handling for .bin files
└── cli.py              # Command-line interface
```

**Scanning Process:**
1. Load file as byte stream
2. Parse pickle opcodes without execution
3. Identify global imports and function calls
4. Match against dangerous pattern database
5. Report findings with severity

---

## Strengths

✅ **Lightweight**: Minimal dependencies, pure Python  
✅ **Fast**: Scans models in seconds (no execution overhead)  
✅ **Safe**: Never executes suspicious code  
✅ **Focused**: Specialized for pickle security  
✅ **Hugging Face Integration**: Direct model hub scanning  
✅ **Clear Output**: Easy to understand scan results  
✅ **MIT License**: Permissive, enterprise-friendly  

---

## Limitations

❌ **Pickle-Only**: Does not support H5, Protocol Buffer, ONNX, etc.  
❌ **No Baseline Management**: Cannot track approved models over time  
❌ **Limited Context**: No metadata analysis (author, provenance)  
❌ **No Backdoor Detection**: Only checks deserialization attacks  
❌ **No Notebook Scanning**: Doesn't scan Jupyter notebooks  
❌ **No Secrets Detection**: Doesn't find hardcoded API keys/passwords  

---

## Use Cases

1. **Pre-download Verification**: Scan Hugging Face models before downloading
2. **CI/CD Integration**: Validate models in pipelines
3. **Manual Audits**: Quick checks of downloaded models
4. **Research**: Analyze pickle structure for security research

---

## Command-Line Interface

```bash
# Scan Hugging Face model
picklescan --huggingface ykilcher/totally-harmless-model

# Scan local file
picklescan --path downloads/pytorch_model.bin

# Scan directory
picklescan --path models/

# Scan URL
picklescan --url https://huggingface.co/.../pytorch_model.bin

# Debug mode
picklescan -l DEBUG -p model.pkl
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Clean scan, no malware detected |
| 1 | Malware found |
| 2 | Scan failed (error occurred) |

---

## Installation

```bash
pip install picklescan

# Optional: NumPy support
pip install picklescan numpy

# Optional: 7z support
pip install picklescan[7z]
```

---

## Dependencies

**Core**: None (pure Python)  
**Optional**:
- `numpy`: For `.npy` file scanning
- `py7zr`: For `.7z` archive support

---

## Example Output

```
https://huggingface.co/ykilcher/totally-harmless-model/resolve/main/pytorch_model.bin:archive/data.pkl: 
  global import '__builtin__ eval' FOUND

----------- SCAN SUMMARY -----------
Scanned files: 1
Infected files: 1
Dangerous globals: 1
```

---

## Integration Examples

### Python API
```python
from picklescan.scanner import scan_file_path

result = scan_file_path("model.pkl")
if result.infected_files > 0:
    print("Malicious model detected!")
```

### CI/CD (GitHub Actions)
```yaml
- name: Scan ML Model
  run: |
    pip install picklescan
    picklescan --path models/pytorch_model.bin || exit 1
```

---

## Performance

- **Speed**: Scans 100MB model in ~2 seconds
- **Memory**: Minimal (stream-based parsing)
- **Scalability**: Can scan thousands of files

---

## Security Model

**Threat Detection:**
- ✅ Arbitrary code execution (ACE)
- ✅ Credential theft
- ✅ Data exfiltration
- ❌ Backdoor triggers (model behavior)
- ❌ Data poisoning (model weights)

**Analysis Type:**
- Static bytecode analysis
- Pattern-based detection
- No ML/heuristics

---

## Community & Support

- **Documentation**: README.md with examples
- **Issues**: GitHub issue tracker
- **Updates**: Regular maintenance
- **References**: Extensive security research references

---

## Comparison to Alternatives

| Feature | Picklescan | ModelScan | Watchtower |
|---------|-----------|-----------|------------|
| Pickle Support | ✅ Excellent | ✅ Excellent | ✅ Good |
| Multi-Format | ❌ No | ✅ Yes | ✅ Yes |
| Notebook Scanning | ❌ No | ❌ No | ✅ Yes |
| Hugging Face Direct | ✅ Yes | ❌ No | ✅ Yes |
| License | MIT | Apache 2.0 | Apache 2.0 |

---

## Recommendation for SentraScan-Model

**Include**: ✅ **Yes**

**Reasoning:**
- Excellent pickle scanning engine
- Lightweight and fast
- MIT license (compatible)
- Can be integrated as pickle scanner module
- Complements ModelScan's broader approach

**Integration Strategy:**
- Use as specialized pickle analysis engine
- Combine with ModelScan for multi-format support
- Leverage Hugging Face integration
