/**
 * Tenant Management JavaScript
 * Handles tenant listing, creation, editing, and activation/deactivation
 */

document.addEventListener('DOMContentLoaded', function() {
    const createBtn = document.getElementById('create-tenant-btn');
    const tenantModal = document.getElementById('tenant-modal');
    const tenantForm = document.getElementById('tenant-form');
    const tenantsTableBody = document.getElementById('tenants-table-body');
    
    // Load tenants on page load
    loadTenants();
    
    // Open create modal
    if (createBtn) {
        createBtn.addEventListener('click', () => openTenantModal());
    }
    
    // Modal close handlers
    const closeButtons = tenantModal.querySelectorAll('.modal-close, .modal-cancel');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', () => closeTenantModal());
    });
    
    // Form submission
    if (tenantForm) {
        tenantForm.addEventListener('submit', handleTenantSubmit);
    }
    
    // Close modal on outside click
    tenantModal.addEventListener('click', (e) => {
        if (e.target === tenantModal) {
            closeTenantModal();
        }
    });
    
    function loadTenants() {
        fetch('/api/v1/tenants')
            .then(response => {
                if (!response.ok) {
                    if (response.status === 401 || response.status === 403) {
                        window.location.href = '/login';
                        return;
                    }
                    throw new Error('Failed to load tenants');
                }
                return response.json();
            })
            .then(tenants => {
                renderTenants(tenants);
            })
            .catch(error => {
                console.error('Error loading tenants:', error);
                tenantsTableBody.innerHTML = `
                    <tr>
                        <td colspan="6" style="padding: var(--spacing-xl); text-align: center; color: var(--color-danger);">
                            Error loading tenants. Please refresh the page.
                        </td>
                    </tr>
                `;
            });
    }
    
    function renderTenants(tenants) {
        if (!tenants || tenants.length === 0) {
            tenantsTableBody.innerHTML = `
                <tr>
                    <td colspan="6" style="padding: var(--spacing-xl); text-align: center; color: var(--color-text-secondary);">
                        No tenants found. Create your first tenant.
                    </td>
                </tr>
            `;
            return;
        }
        
        tenantsTableBody.innerHTML = tenants.map(tenant => `
            <tr>
                <td style="padding: var(--spacing-md); font-weight: var(--font-weight-medium);">${escapeHtml(tenant.name)}</td>
                <td style="padding: var(--spacing-md);">
                    <span class="badge badge-${tenant.is_active ? 'success' : 'secondary'}">
                        ${tenant.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td style="padding: var(--spacing-md); color: var(--color-text-secondary);">
                    ${tenant.stats ? tenant.stats.user_count : 'N/A'}
                </td>
                <td style="padding: var(--spacing-md); color: var(--color-text-secondary);">
                    ${tenant.stats ? tenant.stats.scan_count : 'N/A'}
                </td>
                <td style="padding: var(--spacing-md); color: var(--color-text-secondary);">
                    ${tenant.created_at ? new Date(tenant.created_at).toLocaleDateString() : 'N/A'}
                </td>
                <td style="padding: var(--spacing-md); text-align: right;">
                    <div style="display: flex; gap: var(--spacing-xs); justify-content: flex-end;">
                        <button class="btn btn-sm btn-secondary" onclick="editTenant('${tenant.id}')" title="Edit">
                            Edit
                        </button>
                        ${tenant.is_active ? 
                            `<button class="btn btn-sm btn-danger" onclick="deactivateTenant('${tenant.id}')" title="Deactivate">
                                Deactivate
                            </button>` :
                            `<button class="btn btn-sm btn-success" onclick="activateTenant('${tenant.id}')" title="Activate">
                                Activate
                            </button>`
                        }
                    </div>
                </td>
            </tr>
        `).join('');
    }
    
    function openTenantModal(tenant = null) {
        const modal = document.getElementById('tenant-modal');
        const title = document.getElementById('tenant-modal-title');
        const form = document.getElementById('tenant-form');
        
        if (tenant) {
            title.textContent = 'Edit Tenant';
            document.getElementById('tenant-id').value = tenant.id;
            document.getElementById('tenant-name').value = tenant.name || '';
            document.getElementById('tenant-active').checked = tenant.is_active !== false;
        } else {
            title.textContent = 'Create Tenant';
            form.reset();
            document.getElementById('tenant-id').value = '';
            document.getElementById('tenant-active').checked = true;
        }
        
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
    }
    
    function closeTenantModal() {
        const modal = document.getElementById('tenant-modal');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        document.getElementById('tenant-form').reset();
    }
    
    function handleTenantSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const tenantId = formData.get('tenant_id');
        const isEdit = !!tenantId;
        
        const data = {
            name: formData.get('name'),
            is_active: formData.get('is_active') === 'on'
        };
        
        const url = isEdit ? `/api/v1/tenants/${tenantId}` : '/api/v1/tenants';
        const method = isEdit ? 'PUT' : 'POST';
        
        // Convert to FormData for multipart/form-data
        const submitData = new FormData();
        submitData.append('name', data.name);
        submitData.append('is_active', data.is_active);
        
        fetch(url, {
            method: method,
            body: submitData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.detail || 'Failed to save tenant');
                });
            }
            return response.json();
        })
        .then(() => {
            closeTenantModal();
            loadTenants();
            showToast('Tenant saved successfully', 'success');
        })
        .catch(error => {
            showToast(error.message || 'Failed to save tenant', 'error');
        });
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Global functions for inline handlers
    window.editTenant = function(tenantId) {
        fetch(`/api/v1/tenants/${tenantId}`)
            .then(response => response.json())
            .then(tenant => {
                openTenantModal(tenant);
            })
            .catch(error => {
                showToast('Failed to load tenant', 'error');
            });
    };
    
    window.deactivateTenant = function(tenantId) {
        if (!confirm('Are you sure you want to deactivate this tenant? All users in this tenant will also be deactivated.')) {
            return;
        }
        
        fetch(`/api/v1/tenants/${tenantId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to deactivate tenant');
            }
            return response.json();
        })
        .then(() => {
            loadTenants();
            showToast('Tenant deactivated', 'success');
        })
        .catch(error => {
            showToast(error.message || 'Failed to deactivate tenant', 'error');
        });
    };
    
    window.activateTenant = function(tenantId) {
        fetch(`/api/v1/tenants/${tenantId}/activate`, {
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to activate tenant');
            }
            return response.json();
        })
        .then(() => {
            loadTenants();
            showToast('Tenant activated', 'success');
        })
        .catch(error => {
            showToast(error.message || 'Failed to activate tenant', 'error');
        });
    };
});

