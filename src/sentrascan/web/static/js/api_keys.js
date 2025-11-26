(function() {
  'use strict';

  // ============================================
  // API Key Management
  // ============================================

  const createForm = document.getElementById('create-api-key-form');
  const newKeyDisplay = document.getElementById('new-api-key-display');
  const newKeyValue = document.getElementById('new-api-key-value');
  const copyBtn = document.getElementById('copy-api-key-btn');
  const copySuccessMessage = document.getElementById('copy-success-message');
  const apiKeysList = document.getElementById('api-keys-list');

  // Load API keys on page load
  document.addEventListener('DOMContentLoaded', function() {
    loadApiKeys();
  });

  // Create API key form submission
  if (createForm) {
    createForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const formData = new FormData(createForm);
      const name = formData.get('name') || null;
      const createBtn = document.getElementById('create-key-btn');
      
      // Disable button during request
      createBtn.disabled = true;
      createBtn.textContent = 'Creating...';
      
      try {
        const response = await fetch('/api/v1/api-keys', {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to create API key');
        }
        
        const data = await response.json();
        
        // Display new API key
        newKeyValue.value = data.key;
        newKeyDisplay.style.display = 'block';
        copySuccessMessage.style.display = 'none';
        
        // Reset form
        createForm.reset();
        
        // Scroll to new key display
        newKeyDisplay.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Reload API keys list
        loadApiKeys();
        
      } catch (error) {
        alert('Error creating API key: ' + error.message);
      } finally {
        createBtn.disabled = false;
        createBtn.textContent = 'Create API Key';
      }
    });
  }

  // Copy API key to clipboard
  if (copyBtn) {
    copyBtn.addEventListener('click', async function() {
      const keyValue = newKeyValue.value;
      
      try {
        await navigator.clipboard.writeText(keyValue);
        
        // Show success message
        copySuccessMessage.style.display = 'block';
        copyBtn.textContent = '✓ Copied';
        
        // Reset button text after 2 seconds
        setTimeout(() => {
          copyBtn.textContent = 'Copy';
        }, 2000);
        
      } catch (error) {
        // Fallback for older browsers
        newKeyValue.select();
        document.execCommand('copy');
        copySuccessMessage.style.display = 'block';
      }
    });
  }

  // Load API keys list
  async function loadApiKeys() {
    try {
      const response = await fetch('/api/v1/api-keys');
      
      if (!response.ok) {
        if (response.status === 403) {
          apiKeysList.innerHTML = '<p style="color: var(--color-error);">You do not have permission to view API keys.</p>';
          return;
        }
        throw new Error('Failed to load API keys');
      }
      
      const keys = await response.json();
      
      if (keys.length === 0) {
        apiKeysList.innerHTML = '<p style="color: var(--color-text-secondary);">No API keys found. Create one above to get started.</p>';
        return;
      }
      
      // Render API keys list
      const html = `
        <div class="table-container">
          <table class="table" role="table" aria-label="API keys list">
            <thead>
              <tr>
                <th scope="col">Name</th>
                <th scope="col">Role</th>
                <th scope="col">Created</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              ${keys.map(key => `
                <tr>
                  <td>${escapeHtml(key.name || '(Unnamed)')}</td>
                  <td><span class="badge badge-neutral">${escapeHtml(key.role)}</span></td>
                  <td>${formatDate(key.created_at)}</td>
                  <td>
                    <button 
                      class="btn btn-danger btn-sm revoke-key-btn" 
                      data-key-id="${escapeHtml(key.id)}"
                      aria-label="Revoke API key"
                    >
                      Revoke
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
      
      apiKeysList.innerHTML = html;
      
      // Attach revoke handlers
      document.querySelectorAll('.revoke-key-btn').forEach(btn => {
        btn.addEventListener('click', function() {
          const keyId = this.getAttribute('data-key-id');
          if (confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
            revokeApiKey(keyId);
          }
        });
      });
      
    } catch (error) {
      apiKeysList.innerHTML = `<p style="color: var(--color-error);">Error loading API keys: ${escapeHtml(error.message)}</p>`;
    }
  }

  // Revoke API key
  async function revokeApiKey(keyId) {
    try {
      const response = await fetch(`/api/v1/api-keys/${keyId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to revoke API key');
      }
      
      // Reload list
      loadApiKeys();
      
      // Show success message (you could use a toast notification here)
      if (typeof showToast !== 'undefined') {
        showToast('API key revoked successfully', 'success');
      }
      
    } catch (error) {
      alert('Error revoking API key: ' + error.message);
    }
  }

  // Utility functions
  function escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  }

})();

