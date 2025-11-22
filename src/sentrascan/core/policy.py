import os
import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Policy:
    severity_threshold: str
    block_issues: List[str] = field(default_factory=list)
    sbom_requirements: Dict[str, Any] | None = None

class PolicyEngine:
    def __init__(self, module: str, policy: Policy):
        self.module = module
        self.policy = policy

    @staticmethod
    def from_file(path: str):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        # try both unified and module-specific keys
        if "model" in data:
            pol = data["model"]
            return PolicyEngine("model", Policy(pol.get("severity_threshold", "HIGH"), pol.get("block_issues", []), pol.get("sbom_requirements")))
        if "mcp" in data:
            pol = data["mcp"]
            return PolicyEngine("mcp", Policy(pol.get("severity_threshold", "HIGH"), pol.get("block_issues", [])))
        raise ValueError("Invalid policy file")

    @staticmethod
    def default_model():
        return PolicyEngine("model", Policy("HIGH", ["arbitrary_code_execution", "os_command_execution", "file_system_access"], {"require_sbom": True}))

    @staticmethod
    def default_mcp():
        return PolicyEngine("mcp", Policy("HIGH", ["tool_poisoning", "command_injection", "baseline_drift", "hardcoded_secrets"]))

    def gate(self, severity_counts: Dict[str, int], issue_types: List[str]) -> bool:
        sev_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        threshold_idx = sev_order.index(self.policy.severity_threshold)
        for idx in range(threshold_idx, len(sev_order)):
            sev = sev_order[idx]
            if severity_counts.get(sev.lower() + "_count", 0) > 0:
                return False
        if any(it in self.policy.block_issues for it in issue_types):
            return False
        return True