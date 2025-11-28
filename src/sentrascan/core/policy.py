import os
import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

@dataclass
class Policy:
    severity_threshold: str
    block_issues: List[str] = field(default_factory=list)
    sbom_requirements: Dict[str, Any] | None = None
    # Tenant-specific policy settings
    gate_thresholds: Optional[Dict[str, int]] = None
    policy_rules: Optional[List[Dict[str, Any]]] = None
    pass_criteria: Optional[Dict[str, Any]] = None

class PolicyEngine:
    def __init__(self, module: str, policy: Policy, tenant_id: Optional[str] = None, db: Optional[Session] = None):
        self.module = module
        self.policy = policy
        self.tenant_id = tenant_id
        self.db = db
        # Load tenant-specific policy settings if tenant_id and db are provided
        if tenant_id and db:
            self._load_tenant_policy_settings()

    def _load_tenant_policy_settings(self):
        """Load tenant-specific policy settings from tenant settings service"""
        try:
            from sentrascan.core.tenant_settings import get_tenant_setting
            
            # Get policy settings
            policy_settings = get_tenant_setting(
                self.db,
                self.tenant_id,
                "policy",
                {}
            )
            
            if policy_settings:
                # Update gate thresholds
                if "gate_thresholds" in policy_settings:
                    self.policy.gate_thresholds = policy_settings["gate_thresholds"]
                
                # Update policy rules
                if "policy_rules" in policy_settings:
                    self.policy.policy_rules = policy_settings["policy_rules"]
                
                # Update pass criteria
                if "pass_criteria" in policy_settings:
                    self.policy.pass_criteria = policy_settings["pass_criteria"]
        except Exception:
            # If tenant settings can't be loaded, use defaults
            pass

    @staticmethod
    def from_file(path: str, tenant_id: Optional[str] = None, db: Optional[Session] = None):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        # try both unified and module-specific keys
        if "model" in data:
            pol = data["model"]
            return PolicyEngine(
                "model",
                Policy(
                    pol.get("severity_threshold", "HIGH"),
                    pol.get("block_issues", []),
                    pol.get("sbom_requirements")
                ),
                tenant_id=tenant_id,
                db=db
            )
        if "mcp" in data:
            pol = data["mcp"]
            return PolicyEngine(
                "mcp",
                Policy(
                    pol.get("severity_threshold", "HIGH"),
                    pol.get("block_issues", [])
                ),
                tenant_id=tenant_id,
                db=db
            )
        raise ValueError("Invalid policy file")

    @staticmethod
    def default_model(tenant_id: Optional[str] = None, db: Optional[Session] = None):
        return PolicyEngine(
            "model",
            Policy(
                "HIGH",
                ["arbitrary_code_execution", "os_command_execution", "file_system_access"],
                {"require_sbom": True}
            ),
            tenant_id=tenant_id,
            db=db
        )

    @staticmethod
    def default_mcp(tenant_id: Optional[str] = None, db: Optional[Session] = None):
        return PolicyEngine(
            "mcp",
            Policy(
                "HIGH",
                ["tool_poisoning", "command_injection", "baseline_drift", "hardcoded_secrets"]
            ),
            tenant_id=tenant_id,
            db=db
        )

    def _evaluate_custom_rules(self, severity_counts: Dict[str, int], issue_types: List[str]) -> bool:
        """
        Evaluate custom policy rules.
        
        Returns:
            True if all rules pass, False otherwise
        """
        if not self.policy.policy_rules:
            return True
        
        for rule in self.policy.policy_rules:
            rule_type = rule.get("type")
            rule_condition = rule.get("condition")
            rule_action = rule.get("action", "block")
            
            if rule_type == "severity_count":
                severity = rule_condition.get("severity", "").lower()
                max_count = rule_condition.get("max", 0)
                count = severity_counts.get(f"{severity}_count", 0)
                
                if count > max_count:
                    if rule_action == "block":
                        return False
                    elif rule_action == "warn":
                        # Warning doesn't block, but could be logged
                        pass
            
            elif rule_type == "issue_type":
                blocked_types = rule_condition.get("blocked_types", [])
                if any(it in blocked_types for it in issue_types):
                    if rule_action == "block":
                        return False
            
            elif rule_type == "custom":
                # Custom rule evaluation (can be extended)
                # For now, just return True to allow custom rules
                pass
        
        return True

    def gate(self, severity_counts: Dict[str, int], issue_types: List[str]) -> bool:
        """
        Evaluate gate criteria using tenant-specific policy settings if available.
        
        Args:
            severity_counts: Dictionary with severity counts (critical_count, high_count, etc.)
            issue_types: List of issue type strings
            
        Returns:
            True if scan passes, False otherwise
        """
        # Use tenant-specific gate thresholds if available
        if self.policy.gate_thresholds:
            if severity_counts.get("critical_count", 0) > self.policy.gate_thresholds.get("critical_max", 0):
                return False
            if severity_counts.get("high_count", 0) > self.policy.gate_thresholds.get("high_max", 0):
                return False
            if severity_counts.get("medium_count", 0) > self.policy.gate_thresholds.get("medium_max", 0):
                return False
            if severity_counts.get("low_count", 0) > self.policy.gate_thresholds.get("low_max", 0):
                return False
        else:
            # Fall back to legacy severity threshold logic
            sev_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            threshold_idx = sev_order.index(self.policy.severity_threshold)
            for idx in range(threshold_idx, len(sev_order)):
                sev = sev_order[idx]
                if severity_counts.get(sev.lower() + "_count", 0) > 0:
                    return False
        
        # Check blocked issue types
        if self.policy.block_issues and any(it in self.policy.block_issues for it in issue_types):
            return False
        
        # Evaluate custom policy rules
        if not self._evaluate_custom_rules(severity_counts, issue_types):
            return False
        
        return True