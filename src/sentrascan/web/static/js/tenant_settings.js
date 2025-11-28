/**
 * Tenant Settings Management JavaScript
 * Handles loading, displaying, and saving tenant settings
 */

const API_BASE = window.location.origin;

let currentSettings = {};

// Load settings on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
});

// Tab switching
function showTab(tabName) {
    // Hide all panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.add('hidden');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active', 'border-blue-500', 'text-blue-600', 'dark:text-blue-400');
        button.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300', 'dark:text-gray-400', 'dark:hover:text-gray-300');
    });
    
    // Show selected panel
    const panel = document.getElementById(`panel-${tabName}`);
    if (panel) {
        panel.classList.remove('hidden');
    }
    
    // Activate selected tab
    const tab = document.getElementById(`tab-${tabName}`);
    if (tab) {
        tab.classList.add('active', 'border-blue-500', 'text-blue-600', 'dark:text-blue-400');
        tab.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300', 'dark:text-gray-400', 'dark:hover:text-gray-300');
    }
}

// Load settings from API
async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE}/api/v1/tenant-settings`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`Failed to load settings: ${response.statusText}`);
        }
        
        currentSettings = await response.json();
        populateForm(currentSettings);
    } catch (error) {
        console.error('Error loading settings:', error);
        showToast('Failed to load settings', 'error');
    }
}

// Populate form with settings
function populateForm(settings) {
    // Policy settings
    if (settings.policy) {
        if (settings.policy.gate_thresholds) {
            document.getElementById('policy-gate-critical').value = settings.policy.gate_thresholds.critical_max || 0;
            document.getElementById('policy-gate-high').value = settings.policy.gate_thresholds.high_max || 10;
            document.getElementById('policy-gate-medium').value = settings.policy.gate_thresholds.medium_max || 50;
            document.getElementById('policy-gate-low').value = settings.policy.gate_thresholds.low_max || 100;
        }
        if (settings.policy.pass_criteria) {
            document.getElementById('policy-require-all-scanners').checked = settings.policy.pass_criteria.require_all_scanners_pass || false;
            document.getElementById('policy-allow-warnings').checked = settings.policy.pass_criteria.allow_warnings || false;
        }
    }
    
    // Scanner settings
    if (settings.scanner) {
        if (settings.scanner.enabled_scanners) {
            document.getElementById('scanner-enabled-mcp').checked = settings.scanner.enabled_scanners.includes('mcp');
            document.getElementById('scanner-enabled-model').checked = settings.scanner.enabled_scanners.includes('model');
        }
        if (settings.scanner.scanner_timeouts) {
            document.getElementById('scanner-timeout-mcp').value = settings.scanner.scanner_timeouts.mcp_timeout || 300;
            document.getElementById('scanner-timeout-model').value = settings.scanner.scanner_timeouts.model_timeout || 600;
        }
    }
    
    // Severity settings
    if (settings.severity) {
        if (settings.severity.severity_thresholds) {
            document.getElementById('severity-threshold-critical').value = settings.severity.severity_thresholds.critical_threshold || 0;
            document.getElementById('severity-threshold-high').value = settings.severity.severity_thresholds.high_threshold || 10;
            document.getElementById('severity-threshold-medium').value = settings.severity.severity_thresholds.medium_threshold || 50;
            document.getElementById('severity-threshold-low').value = settings.severity.severity_thresholds.low_threshold || 100;
        }
        if (settings.severity.severity_actions) {
            document.getElementById('severity-action-critical').value = settings.severity.severity_actions.critical_action || 'block';
            document.getElementById('severity-action-high').value = settings.severity.severity_actions.high_action || 'warn';
            document.getElementById('severity-action-medium').value = settings.severity.severity_actions.medium_action || 'notify';
            document.getElementById('severity-action-low').value = settings.severity.severity_actions.low_action || 'notify';
        }
    }
    
    // Notification settings
    if (settings.notification) {
        if (settings.notification.alert_thresholds) {
            document.getElementById('notification-alert-critical').value = settings.notification.alert_thresholds.critical_count || 1;
            document.getElementById('notification-alert-high').value = settings.notification.alert_thresholds.high_count || 5;
            document.getElementById('notification-alert-medium').value = settings.notification.alert_thresholds.medium_count || 20;
            document.getElementById('notification-alert-low').value = settings.notification.alert_thresholds.low_count || 50;
        }
        if (settings.notification.notification_preferences) {
            document.getElementById('notification-email').checked = settings.notification.notification_preferences.email_enabled || false;
            document.getElementById('notification-webhook').checked = settings.notification.notification_preferences.webhook_enabled || false;
            document.getElementById('notification-slack').checked = settings.notification.notification_preferences.slack_enabled || false;
            document.getElementById('notification-teams').checked = settings.notification.notification_preferences.teams_enabled || false;
        }
    }
    
    // Scan settings
    if (settings.scan) {
        if (settings.scan.default_scan_params) {
            document.getElementById('scan-default-timeout').value = settings.scan.default_scan_params.timeout || 300;
            document.getElementById('scan-default-auto-discover').checked = settings.scan.default_scan_params.auto_discover || false;
            document.getElementById('scan-default-include-sbom').checked = settings.scan.default_scan_params.include_sbom || false;
        }
        if (settings.scan.retention_policies) {
            document.getElementById('scan-retention-scans').value = settings.scan.retention_policies.scan_retention_days || 90;
            document.getElementById('scan-retention-findings').value = settings.scan.retention_policies.finding_retention_days || 180;
            document.getElementById('scan-retention-sbom').value = settings.scan.retention_policies.sbom_retention_days || 365;
        }
    }
    
    // Integration settings
    if (settings.integration && settings.integration.webhook_urls) {
        const container = document.getElementById('webhook-urls-container');
        container.innerHTML = '';
        settings.integration.webhook_urls.forEach((url, index) => {
            addWebhookUrlInput(url, index);
        });
    }
}

// Collect form data
function collectFormData() {
    const settings = {
        policy: {
            gate_thresholds: {
                critical_max: parseInt(document.getElementById('policy-gate-critical').value) || 0,
                high_max: parseInt(document.getElementById('policy-gate-high').value) || 10,
                medium_max: parseInt(document.getElementById('policy-gate-medium').value) || 50,
                low_max: parseInt(document.getElementById('policy-gate-low').value) || 100
            },
            pass_criteria: {
                require_all_scanners_pass: document.getElementById('policy-require-all-scanners').checked,
                allow_warnings: document.getElementById('policy-allow-warnings').checked
            }
        },
        scanner: {
            enabled_scanners: [
                ...(document.getElementById('scanner-enabled-mcp').checked ? ['mcp'] : []),
                ...(document.getElementById('scanner-enabled-model').checked ? ['model'] : [])
            ],
            scanner_timeouts: {
                mcp_timeout: parseInt(document.getElementById('scanner-timeout-mcp').value) || 300,
                model_timeout: parseInt(document.getElementById('scanner-timeout-model').value) || 600
            }
        },
        severity: {
            severity_thresholds: {
                critical_threshold: parseInt(document.getElementById('severity-threshold-critical').value) || 0,
                high_threshold: parseInt(document.getElementById('severity-threshold-high').value) || 10,
                medium_threshold: parseInt(document.getElementById('severity-threshold-medium').value) || 50,
                low_threshold: parseInt(document.getElementById('severity-threshold-low').value) || 100
            },
            severity_actions: {
                critical_action: document.getElementById('severity-action-critical').value,
                high_action: document.getElementById('severity-action-high').value,
                medium_action: document.getElementById('severity-action-medium').value,
                low_action: document.getElementById('severity-action-low').value
            }
        },
        notification: {
            alert_thresholds: {
                critical_count: parseInt(document.getElementById('notification-alert-critical').value) || 1,
                high_count: parseInt(document.getElementById('notification-alert-high').value) || 5,
                medium_count: parseInt(document.getElementById('notification-alert-medium').value) || 20,
                low_count: parseInt(document.getElementById('notification-alert-low').value) || 50
            },
            notification_channels: [
                ...(document.getElementById('notification-email').checked ? ['email'] : []),
                ...(document.getElementById('notification-webhook').checked ? ['webhook'] : []),
                ...(document.getElementById('notification-slack').checked ? ['slack'] : []),
                ...(document.getElementById('notification-teams').checked ? ['teams'] : [])
            ],
            notification_preferences: {
                email_enabled: document.getElementById('notification-email').checked,
                webhook_enabled: document.getElementById('notification-webhook').checked,
                slack_enabled: document.getElementById('notification-slack').checked,
                teams_enabled: document.getElementById('notification-teams').checked
            }
        },
        scan: {
            default_scan_params: {
                timeout: parseInt(document.getElementById('scan-default-timeout').value) || 300,
                auto_discover: document.getElementById('scan-default-auto-discover').checked,
                include_sbom: document.getElementById('scan-default-include-sbom').checked
            },
            retention_policies: {
                scan_retention_days: parseInt(document.getElementById('scan-retention-scans').value) || 90,
                finding_retention_days: parseInt(document.getElementById('scan-retention-findings').value) || 180,
                sbom_retention_days: parseInt(document.getElementById('scan-retention-sbom').value) || 365
            }
        },
        integration: {
            webhook_urls: Array.from(document.querySelectorAll('.webhook-url-input')).map(input => input.value).filter(url => url.trim())
        }
    };
    
    return settings;
}

// Save settings
async function saveSettings() {
    try {
        const settings = collectFormData();
        
        const response = await fetch(`${API_BASE}/api/v1/tenant-settings`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(settings)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `Failed to save settings: ${response.statusText}`);
        }
        
        showToast('Settings saved successfully', 'success');
        currentSettings = settings;
    } catch (error) {
        console.error('Error saving settings:', error);
        showToast(`Failed to save settings: ${error.message}`, 'error');
    }
}

// Reset to defaults
async function resetToDefaults() {
    if (!confirm('Are you sure you want to reset all settings to defaults? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/v1/tenant-settings/reset`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`Failed to reset settings: ${response.statusText}`);
        }
        
        showToast('Settings reset to defaults', 'success');
        loadSettings();
    } catch (error) {
        console.error('Error resetting settings:', error);
        showToast(`Failed to reset settings: ${error.message}`, 'error');
    }
}

// Add webhook URL input
function addWebhookUrl(url = '') {
    const container = document.getElementById('webhook-urls-container');
    const index = container.children.length;
    addWebhookUrlInput(url, index);
}

function addWebhookUrlInput(url, index) {
    const container = document.getElementById('webhook-urls-container');
    const div = document.createElement('div');
    div.className = 'flex gap-2';
    div.innerHTML = `
        <input type="url" class="webhook-url-input flex-1 px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
               placeholder="https://example.com/webhook" value="${url || ''}">
        <button onclick="removeWebhookUrl(this)" class="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm">
            Remove
        </button>
    `;
    container.appendChild(div);
}

// Remove webhook URL
function removeWebhookUrl(button) {
    button.parentElement.remove();
}

// Show toast notification
function showToast(message, type = 'info') {
    // Simple toast implementation (can be enhanced)
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-md shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

