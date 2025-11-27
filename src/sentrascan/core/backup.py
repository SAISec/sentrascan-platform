"""
Database backup module with encryption support.

Provides encrypted database backup functionality.
"""

import os
import subprocess
import gzip
from datetime import datetime
from pathlib import Path
from typing import Optional

from sentrascan.core.encryption import encrypt_data
from sentrascan.core.logging import get_logger

logger = get_logger(__name__)

# Use local directory for development, /app/backups for production
_default_backup_dir = os.path.join(os.path.expanduser("~"), ".sentrascan", "backups") if os.path.exists(os.path.expanduser("~")) else "/app/backups"
BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", _default_backup_dir))
try:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    # Fallback to current directory if can't create default
    BACKUP_DIR = Path(os.path.join(os.getcwd(), ".backups"))
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def create_encrypted_backup(db_url: str, tenant_id: Optional[str] = None) -> Optional[str]:
    """
    Create an encrypted database backup.
    
    Args:
        db_url: Database connection URL.
        tenant_id: Optional tenant ID for tenant-specific backup.
    
    Returns:
        Path to encrypted backup file, or None if failed.
    """
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{tenant_id}_{timestamp}" if tenant_id else f"backup_{timestamp}"
        backup_path = BACKUP_DIR / f"{backup_name}.sql.gz"
        
        # Create PostgreSQL dump
        dump_cmd = ["pg_dump", db_url]
        result = subprocess.run(
            dump_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Compress
        with gzip.open(backup_path, 'wb') as f:
            f.write(result.stdout.encode())
        
        # Encrypt the backup
        with open(backup_path, 'rb') as f:
            backup_data = f.read().decode('utf-8', errors='ignore')
        
        encrypted_data = encrypt_data(backup_data)
        encrypted_path = BACKUP_DIR / f"{backup_name}.encrypted"
        
        with open(encrypted_path, 'w') as f:
            f.write(encrypted_data)
        
        # Remove unencrypted backup
        backup_path.unlink()
        
        logger.info("encrypted_backup_created", path=str(encrypted_path), tenant_id=tenant_id)
        return str(encrypted_path)
        
    except Exception as e:
        logger.error("backup_creation_failed", error=str(e))
        return None

