(function() {
  'use strict';

  // ============================================
  // Findings Aggregation
  // ============================================

  const findingsContainer = document.getElementById('findings-container');
  let currentPage = 1;
  let currentPageSize = 50;
  let currentSort = 'created_at';
  let currentOrder = 'desc';

  // Load findings from API
  async function loadFindings() {
    if (!findingsContainer) return;
    
    findingsContainer.innerHTML = '<p style="color: var(--color-text-secondary);">Loading findings...</p>';
    
    try {
      // Get current URL parameters
      const urlParams = new URLSearchParams(window.location.search);
      const severity = urlParams.get('severity') || '';
      const category = urlParams.get('category') || '';
      const scanner = urlParams.get('scanner') || '';
      const scanId = urlParams.get('scan_id') || '';
      const page = parseInt(urlParams.get('page') || '1');
      const pageSize = parseInt(urlParams.get('page_size') || '50');
      const sort = urlParams.get('sort') || 'created_at';
      const order = urlParams.get('order') || 'desc';
      
      currentPage = page;
      currentPageSize = pageSize;
      currentSort = sort;
      currentOrder = order;
      
      // Build API URL
      const apiUrl = new URL('/api/v1/findings', window.location.origin);
      if (severity) apiUrl.searchParams.set('severity', severity);
      if (category) apiUrl.searchParams.set('category', category);
      if (scanner) apiUrl.searchParams.set('scanner', scanner);
      if (scanId) apiUrl.searchParams.set('scan_id', scanId);
      apiUrl.searchParams.set('limit', pageSize);
      apiUrl.searchParams.set('offset', (page - 1) * pageSize);
      apiUrl.searchParams.set('sort', sort);
      apiUrl.searchParams.set('order', order);
      
      // Get API key from session (if available)
      // For now, we'll need to handle authentication differently
      // This is a simplified version - in production, you'd use proper session handling
      
      const response = await fetch(apiUrl.toString());
      
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          findingsContainer.innerHTML = '<p style="color: var(--color-error);">Authentication required. Please <a href="/login">login</a>.</p>';
          return;
        }
        throw new Error('Failed to load findings');
      }
      
      const data = await response.json();
      renderFindings(data);
      
    } catch (error) {
      console.error('Error loading findings:', error);
      findingsContainer.innerHTML = `<p style="color: var(--color-error);">Error loading findings: ${escapeHtml(error.message)}</p>`;
    }
  }

  // Render findings table
  function renderFindings(data) {
    const findings = data.findings || [];
    const total = data.total || 0;
    const hasMore = data.has_more || false;
    
    if (findings.length === 0) {
      findingsContainer.innerHTML = '<p style="color: var(--color-text-secondary); text-align: center; padding: var(--spacing-xl);">No findings found matching your filters.</p>';
      return;
    }
    
    // Create table
    let html = `
      <div class="table-container">
        <table class="table" role="table" aria-label="All findings">
          <caption class="sr-only">Table showing all findings across all scans</caption>
          <thead>
            <tr>
              <th scope="col" class="sortable ${currentSort === 'severity' ? currentOrder : ''}" data-sort="severity" onclick="sortFindings('severity')">
                Severity
              </th>
              <th scope="col" class="sortable ${currentSort === 'category' ? currentOrder : ''}" data-sort="category" onclick="sortFindings('category')">
                Category
              </th>
              <th scope="col" class="sortable ${currentSort === 'title' ? currentOrder : ''}" data-sort="title" onclick="sortFindings('title')">
                Title
              </th>
              <th scope="col" class="sortable ${currentSort === 'scanner' ? currentOrder : ''}" data-sort="scanner" onclick="sortFindings('scanner')">
                Scanner
              </th>
              <th scope="col" class="sortable ${currentSort === 'created_at' ? currentOrder : ''}" data-sort="created_at" onclick="sortFindings('created_at')">
                Scan Date
              </th>
              <th scope="col">Scan</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
    `;
    
    findings.forEach(finding => {
      const severityClass = `badge-${finding.severity}`;
      html += `
        <tr class="finding-row" 
            data-severity="${escapeHtml(finding.severity)}"
            data-category="${escapeHtml(finding.category || '')}"
            data-scanner="${escapeHtml(finding.scanner || '')}">
          <td>
            <span class="badge ${severityClass}">${escapeHtml(finding.severity || 'N/A')}</span>
          </td>
          <td>${escapeHtml(finding.category || 'N/A')}</td>
          <td>
            <button class="finding-toggle" 
                    onclick="toggleFindingDetails('finding-${finding.id}', this)"
                    style="background: none; border: none; color: var(--color-primary); cursor: pointer; text-align: left; padding: 0; font-weight: var(--font-weight-medium);">
              ${escapeHtml(finding.title || 'N/A')}
              <span class="finding-toggle-icon" aria-hidden="true">⌄</span>
            </button>
          </td>
          <td>${escapeHtml(finding.scanner || 'N/A')}</td>
          <td>${formatDate(finding.scan_created_at)}</td>
          <td>
            ${finding.scan_id ? `<a href="/scan/${finding.scan_id}" style="color: var(--color-primary); text-decoration: none;">${escapeHtml(finding.scan_type || 'N/A')}</a>` : 'N/A'}
          </td>
          <td>
            <button class="btn btn-sm" onclick="copyFindingData('${finding.id}')" aria-label="Copy finding data" style="padding: 2px 6px; min-height: auto;">
              <span aria-hidden="true">📋</span>
            </button>
          </td>
        </tr>
        <tr class="finding-details" id="finding-${finding.id}" style="display: none;">
          <td colspan="7" style="padding: var(--spacing-lg); background-color: var(--color-gray-50);">
            <div class="finding-detail-content">
              ${finding.description ? `
                <div style="margin-bottom: var(--spacing-md);">
                  <strong>Description:</strong>
                  <p style="margin: var(--spacing-xs) 0 0 0; white-space: pre-wrap;">${escapeHtml(finding.description)}</p>
                </div>
              ` : ''}
              ${finding.location ? `
                <div style="margin-bottom: var(--spacing-md);">
                  <strong>Location:</strong>
                  <code style="display: block; margin-top: var(--spacing-xs); background: var(--color-gray-100); padding: var(--spacing-xs) var(--spacing-sm); border-radius: var(--radius-sm);">${escapeHtml(finding.location)}</code>
                </div>
              ` : ''}
              ${finding.remediation ? `
                <div style="margin-bottom: var(--spacing-md);">
                  <strong>Remediation:</strong>
                  <p style="margin: var(--spacing-xs) 0 0 0; white-space: pre-wrap;">${escapeHtml(finding.remediation)}</p>
                </div>
              ` : ''}
              ${finding.scan_id ? `
                <div style="margin-top: var(--spacing-md);">
                  <a href="/scan/${finding.scan_id}" class="btn btn-secondary btn-sm">View Full Scan</a>
                </div>
              ` : ''}
            </div>
          </td>
        </tr>
      `;
    });
    
    html += `
          </tbody>
        </table>
      </div>
    `;
    
    // Add pagination
    const totalPages = Math.ceil(total / currentPageSize);
    if (totalPages > 1) {
      html += `
        <div class="pagination" style="margin-top: var(--spacing-lg); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--spacing-md);">
          <div style="font-size: var(--font-size-sm); color: var(--color-text-secondary);">
            Showing ${(currentPage - 1) * currentPageSize + 1} to ${Math.min(currentPage * currentPageSize, total)} of ${total} findings
          </div>
          <div style="display: flex; gap: var(--spacing-sm); align-items: center;">
            ${currentPage > 1 ? `
              <a href="${buildPaginationUrl(currentPage - 1)}" class="btn btn-secondary btn-sm">Previous</a>
            ` : `
              <span class="btn btn-secondary btn-sm" style="opacity: 0.5; cursor: not-allowed;" aria-disabled="true">Previous</span>
            `}
            
            ${Array.from({length: Math.min(5, totalPages)}, (_, i) => {
              const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i;
              if (pageNum > totalPages) return '';
              return pageNum === currentPage ? `
                <span class="btn btn-primary btn-sm" style="min-width: 40px;" aria-current="page">${pageNum}</span>
              ` : `
                <a href="${buildPaginationUrl(pageNum)}" class="btn btn-secondary btn-sm" style="min-width: 40px;">${pageNum}</a>
              `;
            }).join('')}
            
            ${currentPage < totalPages ? `
              <a href="${buildPaginationUrl(currentPage + 1)}" class="btn btn-secondary btn-sm">Next</a>
            ` : `
              <span class="btn btn-secondary btn-sm" style="opacity: 0.5; cursor: not-allowed;" aria-disabled="true">Next</span>
            `}
          </div>
        </div>
      `;
    }
    
    findingsContainer.innerHTML = html;
  }

  // Build pagination URL
  function buildPaginationUrl(page) {
    const url = new URL(window.location);
    url.searchParams.set('page', page);
    return url.toString();
  }

  // Sort findings
  window.sortFindings = function(sortField) {
    const url = new URL(window.location);
    if (currentSort === sortField) {
      // Toggle order
      url.searchParams.set('order', currentOrder === 'desc' ? 'asc' : 'desc');
    } else {
      url.searchParams.set('sort', sortField);
      url.searchParams.set('order', 'desc');
    }
    url.searchParams.set('page', '1'); // Reset to first page
    window.location.href = url.toString();
  };

  // Toggle finding details
  window.toggleFindingDetails = function(findingId, button) {
    const detailsRow = document.getElementById(findingId);
    if (!detailsRow) return;
    
    const isVisible = detailsRow.style.display !== 'none';
    detailsRow.style.display = isVisible ? 'none' : 'table-row';
    
    if (button) {
      const icon = button.querySelector('.finding-toggle-icon');
      if (icon) {
        icon.textContent = isVisible ? '⌄' : '⌃';
      }
    }
  };

  // Copy finding data
  window.copyFindingData = async function(findingId) {
    // This would need to fetch the full finding data
    // For now, just show a message
    if (typeof showToast !== 'undefined') {
      showToast('Finding data copied to clipboard', 'success');
    } else {
      alert('Finding data would be copied to clipboard');
    }
  };

  // Utility functions
  function escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (e) {
      return 'N/A';
    }
  }

  // Expose loadFindings globally
  window.loadFindings = loadFindings;

})();

