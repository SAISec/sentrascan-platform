/**
 * SentraScan Platform - Advanced Filtering
 * Multi-select, date pickers, filter chips, global search
 */

(function() {
  'use strict';

  // ============================================
  // Filter Chips Management
  // ============================================

  /**
   * Add a filter chip
   */
  window.addFilterChip = function(key, label, value) {
    const container = document.getElementById('filter-chips-container');
    if (!container) return;

    // Check if chip already exists
    if (container.querySelector(`[data-filter-key="${key}"]`)) {
      return;
    }

    const chip = document.createElement('span');
    chip.className = 'filter-chip badge badge-neutral';
    chip.setAttribute('data-filter-key', key);
    chip.setAttribute('data-filter-value', value);
    chip.style.cssText = `
      display: inline-flex;
      align-items: center;
      gap: var(--spacing-xs);
      padding: var(--spacing-xs) var(--spacing-sm);
      cursor: default;
    `;
    
    chip.innerHTML = `
      <span>${escapeHtml(label)}</span>
      <button 
        class="filter-chip-remove" 
        onclick="removeFilterChip('${key}')"
        aria-label="Remove ${escapeHtml(label)} filter"
        style="background: none; border: none; color: inherit; cursor: pointer; padding: 0; margin-left: var(--spacing-xs); font-size: var(--font-size-lg); line-height: 1;">
        ×
      </button>
    `;

    container.appendChild(chip);
    updateClearFiltersButton();
  };

  /**
   * Remove a filter chip
   */
  window.removeFilterChip = function(key) {
    const chip = document.querySelector(`[data-filter-key="${key}"]`);
    if (chip) {
      const label = chip.textContent.trim();
      chip.remove();
      updateClearFiltersButton();
      
      // Announce to screen readers
      if (typeof announceToScreenReader !== 'undefined') {
        announceToScreenReader(`Filter removed: ${label}`, 'polite');
      }
      
      // Remove from URL and reload
      const url = new URL(window.location);
      url.searchParams.delete(key);
      window.location.href = url.toString();
    }
  };

  /**
   * Clear all filter chips
   */
  window.clearAllFilters = function() {
    const container = document.getElementById('filter-chips-container');
    if (container) {
      container.innerHTML = '';
      
      // Announce to screen readers
      if (typeof announceToScreenReader !== 'undefined') {
        announceToScreenReader('All filters cleared', 'polite');
      }
    }
    
    // Clear URL parameters and reload
    const url = new URL(window.location);
    const paramsToKeep = ['page', 'page_size']; // Keep pagination params
    url.searchParams.forEach((value, key) => {
      if (!paramsToKeep.includes(key)) {
        url.searchParams.delete(key);
      }
    });
    window.location.href = url.toString();
  };

  /**
   * Update clear filters button visibility
   */
  function updateClearFiltersButton() {
    const container = document.getElementById('filter-chips-container');
    const clearBtn = document.getElementById('clear-all-filters-btn');
    
    if (container && clearBtn) {
      const hasFilters = container.children.length > 0;
      clearBtn.style.display = hasFilters ? 'inline-block' : 'none';
    }
  }

  // ============================================
  // Multi-Select Component
  // ============================================

  /**
   * Initialize multi-select components
   */
  function initMultiSelects() {
    document.querySelectorAll('[data-multi-select]').forEach(select => {
      setupMultiSelect(select);
    });
  }

  function setupMultiSelect(select) {
    // Convert select to multi-select UI
    const wrapper = document.createElement('div');
    wrapper.className = 'multi-select-wrapper';
    wrapper.style.cssText = 'position: relative;';
    
    const display = document.createElement('button');
    display.className = 'multi-select-display form-select';
    display.type = 'button';
    display.setAttribute('aria-haspopup', 'listbox');
    display.setAttribute('aria-expanded', 'false');
    
    const options = Array.from(select.options);
    const selected = options.filter(opt => opt.selected && opt.value);
    display.textContent = selected.length > 0 
      ? `${selected.length} selected` 
      : select.querySelector('option[value=""]')?.textContent || 'Select...';
    
    const dropdown = document.createElement('div');
    dropdown.className = 'multi-select-dropdown';
    dropdown.setAttribute('role', 'listbox');
    dropdown.style.cssText = `
      display: none;
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      margin-top: var(--spacing-xs);
      background: var(--color-bg-primary);
      border: 1px solid var(--color-border-light);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      max-height: 200px;
      overflow-y: auto;
      z-index: var(--z-index-dropdown);
    `;
    
    options.forEach(option => {
      if (option.value === '') return; // Skip empty option
      
      const item = document.createElement('div');
      item.className = 'multi-select-option';
      item.setAttribute('role', 'option');
      item.setAttribute('aria-selected', option.selected ? 'true' : 'false');
      item.style.cssText = `
        padding: var(--spacing-sm) var(--spacing-md);
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        transition: background-color var(--transition-fast);
      `;
      
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = option.selected;
      checkbox.value = option.value;
      
      const label = document.createElement('label');
      label.textContent = option.textContent;
      label.style.cssText = 'cursor: pointer; flex: 1; margin: 0;';
      
      item.appendChild(checkbox);
      item.appendChild(label);
      
      checkbox.addEventListener('change', function() {
        option.selected = this.checked;
        item.setAttribute('aria-selected', this.checked ? 'true' : 'false');
        updateDisplay();
        triggerChange();
      });
      
      item.addEventListener('click', function(e) {
        if (e.target !== checkbox) {
          checkbox.checked = !checkbox.checked;
          checkbox.dispatchEvent(new Event('change'));
        }
      });
      
      dropdown.appendChild(item);
    });
    
    function updateDisplay() {
      const selected = options.filter(opt => opt.selected && opt.value);
      display.textContent = selected.length > 0 
        ? `${selected.length} selected` 
        : 'Select...';
    }
    
    function triggerChange() {
      const event = new Event('change', { bubbles: true });
      select.dispatchEvent(event);
    }
    
    display.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      const isOpen = dropdown.style.display === 'block';
      dropdown.style.display = isOpen ? 'none' : 'block';
      display.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
    });
    
    // Close on outside click
    document.addEventListener('click', function(e) {
      if (!wrapper.contains(e.target)) {
        dropdown.style.display = 'none';
        display.setAttribute('aria-expanded', 'false');
      }
    });
    
    wrapper.appendChild(display);
    wrapper.appendChild(dropdown);
    select.style.display = 'none';
    select.parentNode.insertBefore(wrapper, select);
  }

  // ============================================
  // Date Picker Component
  // ============================================

  /**
   * Initialize date pickers
   */
  function initDatePickers() {
    document.querySelectorAll('input[type="date"]').forEach(input => {
      // Add min/max if not set
      if (!input.min) {
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
        input.min = oneYearAgo.toISOString().split('T')[0];
      }
      if (!input.max) {
        input.max = new Date().toISOString().split('T')[0];
      }
    });
  }

  // ============================================
  // Global Search
  // ============================================

  /**
   * Initialize global search
   */
  function initGlobalSearch() {
    const searchInput = document.getElementById('global-search-input');
    const searchForm = document.getElementById('global-search-form');
    const searchInputMobile = document.getElementById('global-search-input-mobile');
    const searchFormMobile = document.getElementById('global-search-form-mobile');
    
    // Desktop search
    if (searchInput && searchForm) {
      setupSearch(searchInput, searchForm);
    }
    
    // Mobile search
    if (searchInputMobile && searchFormMobile) {
      setupSearch(searchInputMobile, searchFormMobile);
    }
  }
  
  function setupSearch(searchInput, searchForm) {
    if (!searchInput || !searchForm) return;
    
    let searchTimeout = null;
    
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      const query = this.value.trim();
      
      if (query.length < 2) {
        return;
      }
      
      searchTimeout = setTimeout(() => {
        performGlobalSearch(query);
      }, 300);
    });
    
    searchForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const query = searchInput.value.trim();
      if (query) {
        performGlobalSearch(query);
      }
    });
  }

  /**
   * Perform global search
   */
  function performGlobalSearch(query) {
    // Navigate to search results page or filter current page
    window.location.href = `/?search=${encodeURIComponent(query)}`;
  }

  // ============================================
  // Initialize on page load
  // ============================================

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      initMultiSelects();
      initDatePickers();
      initGlobalSearch();
    });
  } else {
    initMultiSelects();
    initDatePickers();
    initGlobalSearch();
  }

})();

