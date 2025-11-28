"""
Tenant Settings Service

Manages tenant-specific configurations including:
- Policy settings (custom policy rules, gate thresholds, pass/fail criteria)
- Scanner settings (enable/disable scanners, timeouts, configurations)
- Severity settings (custom severity mappings, thresholds, actions)
- Notification settings (alert thresholds, channels, preferences)
- Scan settings (default scan parameters, schedules, retention policies)
- Integration settings (webhook URLs, external tool configs)
"""

import json
import jsonschema
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sentrascan.core.models import Tenant, TenantSettings, User
from sentrascan.core.audit import log_configuration_change
import structlog

logger = structlog.get_logger(__name__)

# Default settings schema
DEFAULT_SETTINGS_SCHEMA = {
    "type": "object",
    "properties": {
        "policy": {
            "type": "object",
            "properties": {
                "policy_rules": {"type": "array", "items": {"type": "object"}},
                "gate_thresholds": {
                    "type": "object",
                    "properties": {
                        "critical_max": {"type": "integer", "minimum": 0},
                        "high_max": {"type": "integer", "minimum": 0},
                        "medium_max": {"type": "integer", "minimum": 0},
                        "low_max": {"type": "integer", "minimum": 0}
                    }
                },
                "pass_criteria": {
                    "type": "object",
                    "properties": {
                        "require_all_scanners_pass": {"type": "boolean"},
                        "allow_warnings": {"type": "boolean"}
                    }
                }
            }
        },
        "scanner": {
            "type": "object",
            "properties": {
                "enabled_scanners": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["mcp", "model"]}
                },
                "scanner_timeouts": {
                    "type": "object",
                    "properties": {
                        "mcp_timeout": {"type": "integer", "minimum": 1},
                        "model_timeout": {"type": "integer", "minimum": 1}
                    }
                },
                "scanner_configs": {
                    "type": "object",
                    "additionalProperties": True
                }
            }
        },
        "severity": {
            "type": "object",
            "properties": {
                "severity_mappings": {
                    "type": "object",
                    "additionalProperties": {"type": "string", "enum": ["critical", "high", "medium", "low", "info"]}
                },
                "severity_thresholds": {
                    "type": "object",
                    "properties": {
                        "critical_threshold": {"type": "integer", "minimum": 0},
                        "high_threshold": {"type": "integer", "minimum": 0},
                        "medium_threshold": {"type": "integer", "minimum": 0},
                        "low_threshold": {"type": "integer", "minimum": 0}
                    }
                },
                "severity_actions": {
                    "type": "object",
                    "properties": {
                        "critical_action": {"type": "string", "enum": ["block", "warn", "notify"]},
                        "high_action": {"type": "string", "enum": ["block", "warn", "notify"]},
                        "medium_action": {"type": "string", "enum": ["block", "warn", "notify"]},
                        "low_action": {"type": "string", "enum": ["block", "warn", "notify"]}
                    }
                }
            }
        },
        "notification": {
            "type": "object",
            "properties": {
                "alert_thresholds": {
                    "type": "object",
                    "properties": {
                        "critical_count": {"type": "integer", "minimum": 0},
                        "high_count": {"type": "integer", "minimum": 0},
                        "medium_count": {"type": "integer", "minimum": 0},
                        "low_count": {"type": "integer", "minimum": 0}
                    }
                },
                "notification_channels": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["email", "webhook", "slack", "teams"]}
                },
                "notification_preferences": {
                    "type": "object",
                    "properties": {
                        "email_enabled": {"type": "boolean"},
                        "webhook_enabled": {"type": "boolean"},
                        "slack_enabled": {"type": "boolean"},
                        "teams_enabled": {"type": "boolean"}
                    }
                }
            }
        },
        "scan": {
            "type": "object",
            "properties": {
                "default_scan_params": {
                    "type": "object",
                    "properties": {
                        "timeout": {"type": "integer", "minimum": 1},
                        "auto_discover": {"type": "boolean"},
                        "include_sbom": {"type": "boolean"}
                    }
                },
                "scan_schedules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "cron": {"type": "string"},
                            "scan_type": {"type": "string", "enum": ["mcp", "model"]},
                            "enabled": {"type": "boolean"}
                        }
                    }
                },
                "retention_policies": {
                    "type": "object",
                    "properties": {
                        "scan_retention_days": {"type": "integer", "minimum": 1},
                        "finding_retention_days": {"type": "integer", "minimum": 1},
                        "sbom_retention_days": {"type": "integer", "minimum": 1}
                    }
                }
            }
        },
        "integration": {
            "type": "object",
            "properties": {
                "webhook_urls": {
                    "type": "array",
                    "items": {"type": "string", "format": "uri"}
                },
                "external_tool_configs": {
                    "type": "object",
                    "additionalProperties": True
                }
            }
        }
    }
}

# Default settings for new tenants
DEFAULT_SETTINGS = {
    "policy": {
        "policy_rules": [],
        "gate_thresholds": {
            "critical_max": 0,
            "high_max": 10,
            "medium_max": 50,
            "low_max": 100
        },
        "pass_criteria": {
            "require_all_scanners_pass": True,
            "allow_warnings": False
        }
    },
    "scanner": {
        "enabled_scanners": ["mcp", "model"],
        "scanner_timeouts": {
            "mcp_timeout": 300,
            "model_timeout": 600
        },
        "scanner_configs": {}
    },
    "severity": {
        "severity_mappings": {},
        "severity_thresholds": {
            "critical_threshold": 0,
            "high_threshold": 10,
            "medium_threshold": 50,
            "low_threshold": 100
        },
        "severity_actions": {
            "critical_action": "block",
            "high_action": "warn",
            "medium_action": "notify",
            "low_action": "notify"
        }
    },
    "notification": {
        "alert_thresholds": {
            "critical_count": 1,
            "high_count": 5,
            "medium_count": 20,
            "low_count": 50
        },
        "notification_channels": ["email"],
        "notification_preferences": {
            "email_enabled": True,
            "webhook_enabled": False,
            "slack_enabled": False,
            "teams_enabled": False
        }
    },
    "scan": {
        "default_scan_params": {
            "timeout": 300,
            "auto_discover": True,
            "include_sbom": True
        },
        "scan_schedules": [],
        "retention_policies": {
            "scan_retention_days": 90,
            "finding_retention_days": 180,
            "sbom_retention_days": 365
        }
    },
    "integration": {
        "webhook_urls": [],
        "external_tool_configs": {}
    }
}


class TenantSettingsService:
    """Service for managing tenant-specific settings"""
    
    @staticmethod
    def get_default_settings() -> Dict[str, Any]:
        """Get default settings for new tenants"""
        return DEFAULT_SETTINGS.copy()
    
    @staticmethod
    def validate_settings(settings: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate settings against JSON schema.
        
        Args:
            settings: Settings dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            jsonschema.validate(instance=settings, schema=DEFAULT_SETTINGS_SCHEMA)
            return True, None
        except jsonschema.ValidationError as e:
            return False, f"Validation error: {e.message}"
        except Exception as e:
            return False, f"Validation failed: {str(e)}"
    
    @staticmethod
    def get_settings(db: Session, tenant_id: str) -> Dict[str, Any]:
        """
        Get all settings for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            Dictionary of all settings (merged from TenantSettings table and Tenant.settings JSON)
        """
        # Get tenant
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        # Start with default settings
        settings = DEFAULT_SETTINGS.copy()
        
        # Merge with tenant.settings JSON field (if exists)
        if tenant.settings:
            settings = TenantSettingsService._deep_merge(settings, tenant.settings)
        
        # Merge with TenantSettings table entries (key-value pairs)
        tenant_settings_records = db.query(TenantSettings).filter(
            TenantSettings.tenant_id == tenant_id
        ).all()
        
        for record in tenant_settings_records:
            if record.setting_key in settings:
                settings[record.setting_key] = TenantSettingsService._deep_merge(
                    settings[record.setting_key],
                    record.setting_value
                )
            else:
                settings[record.setting_key] = record.setting_value
        
        return settings
    
    @staticmethod
    def get_setting(db: Session, tenant_id: str, setting_key: str, default: Any = None) -> Any:
        """
        Get a specific setting value for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            setting_key: Setting key (e.g., "policy.gate_thresholds.critical_max")
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        all_settings = TenantSettingsService.get_settings(db, tenant_id)
        
        # Navigate nested keys (e.g., "policy.gate_thresholds.critical_max")
        keys = setting_key.split(".")
        value = all_settings
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    @staticmethod
    def set_setting(
        db: Session,
        tenant_id: str,
        setting_key: str,
        setting_value: Any,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Set a specific setting value for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            setting_key: Setting key (e.g., "policy")
            setting_value: Setting value (must be JSON-serializable)
            user_id: User ID who made the change (for audit logging)
            
        Returns:
            True if successful, False otherwise
        """
        # Validate tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        # Get current settings and merge new value
        current_settings = TenantSettingsService.get_settings(db, tenant_id)
        current_settings[setting_key] = setting_value
        
        # Validate merged settings
        is_valid, error_msg = TenantSettingsService.validate_settings(current_settings)
        if not is_valid:
            raise ValueError(f"Invalid settings: {error_msg}")
        
        # Store in TenantSettings table (upsert)
        existing = db.query(TenantSettings).filter(
            TenantSettings.tenant_id == tenant_id,
            TenantSettings.setting_key == setting_key
        ).first()
        
        if existing:
            existing.setting_value = setting_value
            existing.updated_at = datetime.utcnow()
            existing.updated_by = user_id
        else:
            new_setting = TenantSettings(
                tenant_id=tenant_id,
                setting_key=setting_key,
                setting_value=setting_value,
                updated_by=user_id
            )
            db.add(new_setting)
        
        db.commit()
        
        # Log configuration change
        log_configuration_change(
            db=db,
            action="update",
            resource_type="tenant_settings",
            resource_id=tenant_id,
            user_id=user_id,
            details={"setting_key": setting_key, "setting_value": setting_value}
        )
        
        logger.info(
            "tenant_setting_updated",
            tenant_id=tenant_id,
            setting_key=setting_key,
            updated_by=user_id
        )
        
        return True
    
    @staticmethod
    def set_settings(
        db: Session,
        tenant_id: str,
        settings: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> bool:
        """
        Set multiple settings for a tenant at once.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            settings: Dictionary of settings to update
            user_id: User ID who made the change (for audit logging)
            
        Returns:
            True if successful, False otherwise
        """
        # Get current settings and merge
        current_settings = TenantSettingsService.get_settings(db, tenant_id)
        merged_settings = TenantSettingsService._deep_merge(current_settings, settings)
        
        # Validate merged settings
        is_valid, error_msg = TenantSettingsService.validate_settings(merged_settings)
        if not is_valid:
            raise ValueError(f"Invalid settings: {error_msg}")
        
        # Update each setting
        for setting_key, setting_value in settings.items():
            TenantSettingsService.set_setting(
                db=db,
                tenant_id=tenant_id,
                setting_key=setting_key,
                setting_value=setting_value,
                user_id=user_id
            )
        
        return True
    
    @staticmethod
    def reset_to_defaults(
        db: Session,
        tenant_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Reset all settings to default values for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            user_id: User ID who made the change (for audit logging)
            
        Returns:
            True if successful, False otherwise
        """
        # Delete all TenantSettings records for this tenant
        db.query(TenantSettings).filter(
            TenantSettings.tenant_id == tenant_id
        ).delete()
        
        # Clear tenant.settings JSON field
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant:
            tenant.settings = {}
            db.commit()
        
        # Log configuration change
        log_configuration_change(
            db=db,
            action="reset",
            resource_type="tenant_settings",
            resource_id=tenant_id,
            user_id=user_id,
            details={"reset_to": "defaults"}
        )
        
        logger.info(
            "tenant_settings_reset",
            tenant_id=tenant_id,
            updated_by=user_id
        )
        
        return True
    
    @staticmethod
    def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            update: Dictionary to merge into base
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = TenantSettingsService._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result


# Convenience functions
def get_tenant_settings(db: Session, tenant_id: str) -> Dict[str, Any]:
    """Get all settings for a tenant"""
    return TenantSettingsService.get_settings(db, tenant_id)


def get_tenant_setting(db: Session, tenant_id: str, setting_key: str, default: Any = None) -> Any:
    """Get a specific setting value for a tenant"""
    return TenantSettingsService.get_setting(db, tenant_id, setting_key, default)


def set_tenant_setting(
    db: Session,
    tenant_id: str,
    setting_key: str,
    setting_value: Any,
    user_id: Optional[str] = None
) -> bool:
    """Set a specific setting value for a tenant"""
    return TenantSettingsService.set_setting(db, tenant_id, setting_key, setting_value, user_id)


def set_tenant_settings(
    db: Session,
    tenant_id: str,
    settings: Dict[str, Any],
    user_id: Optional[str] = None
) -> bool:
    """Set multiple settings for a tenant at once"""
    return TenantSettingsService.set_settings(db, tenant_id, settings, user_id)


def reset_tenant_settings_to_defaults(
    db: Session,
    tenant_id: str,
    user_id: Optional[str] = None
) -> bool:
    """Reset all settings to default values for a tenant"""
    return TenantSettingsService.reset_to_defaults(db, tenant_id, user_id)

