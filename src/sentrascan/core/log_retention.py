"""
Log retention and archiving module.

Manages log file retention (7 days) and archiving.
"""

import os
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional


def archive_old_logs(log_dir: Optional[str] = None, retention_days: int = 7):
    """
    Archive log files older than retention_days.
    
    Args:
        log_dir: Directory containing log files. Defaults to /app/logs or ./logs.
        retention_days: Number of days to retain logs. Defaults to 7.
    """
    if log_dir is None:
        if os.path.exists("/app"):
            log_dir = "/app/logs"
        else:
            log_dir = "./logs"
    
    log_path = Path(log_dir)
    if not log_path.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    archive_dir = log_path / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    # Find log files to archive
    log_files = list(log_path.glob("*.log"))
    archived_count = 0
    
    for log_file in log_files:
        # Check file modification time
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        
        if mtime < cutoff_date:
            # Archive this file
            archive_name = f"{log_file.stem}_{mtime.strftime('%Y%m%d_%H%M%S')}.log.gz"
            archive_path = archive_dir / archive_name
            
            try:
                # Compress and move to archive
                with open(log_file, "rb") as f_in:
                    with gzip.open(archive_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove original file
                log_file.unlink()
                archived_count += 1
            except Exception:
                # Continue on error
                pass
    
    return archived_count


def cleanup_old_archives(archive_dir: Optional[str] = None, max_age_days: int = 90):
    """
    Clean up archived log files older than max_age_days.
    
    Args:
        archive_dir: Directory containing archived logs. Defaults to /app/logs/archive or ./logs/archive.
        max_age_days: Maximum age of archives to keep. Defaults to 90 days.
    """
    if archive_dir is None:
        if os.path.exists("/app"):
            archive_dir = "/app/logs/archive"
        else:
            archive_dir = "./logs/archive"
    
    archive_path = Path(archive_dir)
    if not archive_path.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    
    # Find archived files to delete
    archive_files = list(archive_path.glob("*.log.gz"))
    deleted_count = 0
    
    for archive_file in archive_files:
        # Check file modification time
        mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
        
        if mtime < cutoff_date:
            try:
                archive_file.unlink()
                deleted_count += 1
            except Exception:
                pass
    
    return deleted_count


def archive_telemetry(telemetry_dir: Optional[str] = None, retention_days: int = 7):
    """
    Archive telemetry files older than retention_days.
    
    Args:
        telemetry_dir: Directory containing telemetry files. Defaults to /app/telemetry or ./telemetry.
        retention_days: Number of days to retain telemetry. Defaults to 7.
    """
    if telemetry_dir is None:
        if os.path.exists("/app"):
            telemetry_dir = "/app/telemetry"
        else:
            telemetry_dir = "./telemetry"
    
    telemetry_path = Path(telemetry_dir)
    if not telemetry_path.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    archive_dir = telemetry_path / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    # Find telemetry files to archive
    telemetry_files = list(telemetry_path.glob("*.jsonl"))
    archived_count = 0
    
    for telemetry_file in telemetry_files:
        # Check file modification time
        mtime = datetime.fromtimestamp(telemetry_file.stat().st_mtime)
        
        if mtime < cutoff_date:
            # Archive this file
            archive_name = f"{telemetry_file.stem}_{mtime.strftime('%Y%m%d_%H%M%S')}.jsonl.gz"
            archive_path = archive_dir / archive_name
            
            try:
                # Compress and move to archive
                with open(telemetry_file, "rb") as f_in:
                    with gzip.open(archive_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove original file
                telemetry_file.unlink()
                archived_count += 1
            except Exception:
                # Continue on error
                pass
    
    return archived_count

