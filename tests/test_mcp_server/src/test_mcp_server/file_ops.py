"""
File operations with LFI and Zip Slip vulnerabilities
WARNING: This code contains intentional security vulnerabilities for testing purposes only.
"""

import os
import zipfile
import tarfile
import shutil

# ============================================================================
# LOCAL FILE INCLUSION (LFI) VULNERABILITIES
# ============================================================================

def read_config_file(filename):
    """LFI - No path validation"""
    # VULNERABLE: Path traversal possible
    filepath = f"config/{filename}"
    with open(filepath, 'r') as f:
        return f.read()

def load_template(template_name):
    """LFI - Template inclusion"""
    # VULNERABLE: No validation
    template_path = os.path.join("templates", template_name)
    with open(template_path, 'r') as f:
        return f.read()

def include_file(filepath):
    """LFI - Direct file inclusion"""
    # VULNERABLE: No path sanitization
    with open(filepath, 'r') as f:
        content = f.read()
    exec(f"result = {content}")  # Also RCE vulnerability
    return result

def read_log_file(log_name):
    """LFI - Log file reading"""
    # VULNERABLE: Path traversal
    log_path = f"/var/log/{log_name}"
    with open(log_path, 'r') as f:
        return f.readlines()

# ============================================================================
# ZIP SLIP VULNERABILITIES
# ============================================================================

def extract_zip(zip_path, dest_dir):
    """Zip Slip - extractall without validation"""
    # VULNERABLE: No path validation
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)

def extract_tar(tar_path, dest_dir):
    """Zip Slip - tar extraction"""
    # VULNERABLE: No path validation
    with tarfile.open(tar_path, 'r:*') as tar_ref:
        tar_ref.extractall(dest_dir)

def extract_archive_safe_looking(archive_path, dest_dir):
    """Zip Slip - Looks safe but isn't"""
    # VULNERABLE: Only checks prefix, not absolute paths
    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if member.startswith('safe/'):
                zip_ref.extract(member, dest_dir)  # Still vulnerable!

# ============================================================================
# ARBITRARY FILE WRITE
# ============================================================================

def save_uploaded_file(filename, content):
    """Arbitrary file write - No validation"""
    # VULNERABLE: Can write anywhere
    filepath = f"uploads/{filename}"
    with open(filepath, 'wb') as f:
        f.write(content)

def write_config(config_name, config_data):
    """Arbitrary file write"""
    # VULNERABLE: Path traversal
    config_path = f"config/{config_name}.json"
    with open(config_path, 'w') as f:
        json.dump(config_data, f)

