/**
 * User Management JavaScript
 * Handles user listing, creation, editing, and deactivation
 */

document.addEventListener('DOMContentLoaded', function() {
    const createBtn = document.getElementById('create-user-btn');
    const userModal = document.getElementById('user-modal');
    const userForm = document.getElementById('user-form');
    const usersTableBody = document.getElementById('users-table-body');
    
    // Load users on page load
    loadUsers();
    
    // Open create modal
    if (createBtn) {
        createBtn.addEventListener('click', () => openUserModal());
    }
    
    // Modal close handlers
    const closeButtons = userModal.querySelectorAll('.modal-close, .modal-cancel');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', () => closeUserModal());
    });
    
    // Form submission
    if (userForm) {
        userForm.addEventListener('submit', handleUserSubmit);
    }
    
    // Close modal on outside click
    userModal.addEventListener('click', (e) => {
        if (e.target === userModal) {
            closeUserModal();
        }
    });
    
    function loadUsers() {
        fetch('/api/v1/users')
            .then(response => {
                if (!response.ok) {
                    if (response.status === 401 || response.status === 403) {
                        window.location.href = '/login';
                        return;
                    }
                    throw new Error('Failed to load users');
                }
                return response.json();
            })
            .then(users => {
                renderUsers(users);
            })
            .catch(error => {
                console.error('Error loading users:', error);
                usersTableBody.innerHTML = `
                    <tr>
                        <td colspan="6" style="padding: var(--spacing-xl); text-align: center; color: var(--color-danger);">
                            Error loading users. Please refresh the page.
                        </td>
                    </tr>
                `;
            });
    }
    
    function renderUsers(users) {
        if (!users || users.length === 0) {
            usersTableBody.innerHTML = `
                <tr>
                    <td colspan="6" style="padding: var(--spacing-xl); text-align: center; color: var(--color-text-secondary);">
                        No users found. Create your first user.
                    </td>
                </tr>
            `;
            return;
        }
        
        usersTableBody.innerHTML = users.map(user => `
            <tr>
                <td style="padding: var(--spacing-md);">${escapeHtml(user.name || 'N/A')}</td>
                <td style="padding: var(--spacing-md);">${escapeHtml(user.email)}</td>
                <td style="padding: var(--spacing-md);">
                    <span class="badge badge-${getRoleBadgeClass(user.role)}">${escapeHtml(user.role)}</span>
                </td>
                <td style="padding: var(--spacing-md);">
                    <span class="badge badge-${user.is_active ? 'success' : 'secondary'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td style="padding: var(--spacing-md); color: var(--color-text-secondary);">
                    ${user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                </td>
                <td style="padding: var(--spacing-md); text-align: right;">
                    <div style="display: flex; gap: var(--spacing-xs); justify-content: flex-end;">
                        <button class="btn btn-sm btn-secondary" onclick="editUser('${user.id}')" title="Edit">
                            Edit
                        </button>
                        ${user.is_active ? 
                            `<button class="btn btn-sm btn-danger" onclick="deactivateUser('${user.id}')" title="Deactivate">
                                Deactivate
                            </button>` :
                            `<button class="btn btn-sm btn-success" onclick="activateUser('${user.id}')" title="Activate">
                                Activate
                            </button>`
                        }
                    </div>
                </td>
            </tr>
        `).join('');
    }
    
    function openUserModal(user = null) {
        const modal = document.getElementById('user-modal');
        const title = document.getElementById('user-modal-title');
        const form = document.getElementById('user-form');
        
        if (user) {
            title.textContent = 'Edit User';
            document.getElementById('user-id').value = user.id;
            document.getElementById('user-name').value = user.name || '';
            document.getElementById('user-email').value = user.email || '';
            document.getElementById('user-role').value = user.role || 'viewer';
            document.getElementById('user-password').required = false;
            document.getElementById('user-password').parentElement.querySelector('small').textContent = 'Leave blank to keep current password';
        } else {
            title.textContent = 'Create User';
            form.reset();
            document.getElementById('user-id').value = '';
            document.getElementById('user-password').required = true;
            document.getElementById('user-password').parentElement.querySelector('small').textContent = 'Minimum 12 characters with uppercase, lowercase, digits, and special characters';
        }
        
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
    }
    
    function closeUserModal() {
        const modal = document.getElementById('user-modal');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        document.getElementById('user-form').reset();
    }
    
    function handleUserSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const userId = formData.get('user_id');
        const isEdit = !!userId;
        
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            role: formData.get('role')
        };
        
        if (formData.get('password')) {
            data.password = formData.get('password');
        }
        
        const url = isEdit ? `/api/v1/users/${userId}` : '/api/v1/users';
        const method = isEdit ? 'PUT' : 'POST';
        
        // Convert to FormData for multipart/form-data
        const submitData = new FormData();
        Object.keys(data).forEach(key => {
            if (data[key] !== null && data[key] !== undefined) {
                submitData.append(key, data[key]);
            }
        });
        
        fetch(url, {
            method: method,
            body: submitData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.detail || 'Failed to save user');
                });
            }
            return response.json();
        })
        .then(() => {
            closeUserModal();
            loadUsers();
            showToast('User saved successfully', 'success');
        })
        .catch(error => {
            showToast(error.message || 'Failed to save user', 'error');
        });
    }
    
    function getRoleBadgeClass(role) {
        const roleClasses = {
            'super_admin': 'danger',
            'tenant_admin': 'warning',
            'scanner': 'info',
            'viewer': 'secondary'
        };
        return roleClasses[role] || 'secondary';
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Global functions for inline handlers
    window.editUser = function(userId) {
        fetch(`/api/v1/users/${userId}`)
            .then(response => response.json())
            .then(user => {
                openUserModal(user);
            })
            .catch(error => {
                showToast('Failed to load user', 'error');
            });
    };
    
    window.deactivateUser = function(userId) {
        if (!confirm('Are you sure you want to deactivate this user?')) {
            return;
        }
        
        fetch(`/api/v1/users/${userId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to deactivate user');
            }
            return response.json();
        })
        .then(() => {
            loadUsers();
            showToast('User deactivated', 'success');
        })
        .catch(error => {
            showToast(error.message || 'Failed to deactivate user', 'error');
        });
    };
    
    window.activateUser = function(userId) {
        fetch(`/api/v1/users/${userId}/activate`, {
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to activate user');
            }
            return response.json();
        })
        .then(() => {
            loadUsers();
            showToast('User activated', 'success');
        })
        .catch(error => {
            showToast(error.message || 'Failed to activate user', 'error');
        });
    };
});

