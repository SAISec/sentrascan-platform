/**
 * SentraScan Platform - Accessibility Enhancements
 * Keyboard navigation, ARIA live regions, focus management
 */

(function() {
  'use strict';

  // ============================================
  // Skip Link Enhancement
  // ============================================

  /**
   * Initialize skip link
   */
  function initSkipLink() {
    const skipLink = document.querySelector('.skip-link');
    if (skipLink) {
      skipLink.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          e.preventDefault();
          target.focus();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    }
  }

  // ============================================
  // ARIA Live Regions
  // ============================================

  /**
   * Create or get ARIA live region
   */
  window.getAriaLiveRegion = function(politeness = 'polite') {
    let region = document.getElementById(`aria-live-${politeness}`);
    if (!region) {
      region = document.createElement('div');
      region.id = `aria-live-${politeness}`;
      region.setAttribute('role', 'status');
      region.setAttribute('aria-live', politeness);
      region.setAttribute('aria-atomic', 'true');
      region.className = 'sr-only';
      region.style.cssText = `
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
      `;
      document.body.appendChild(region);
    }
    return region;
  };

  /**
   * Announce message to screen readers
   */
  window.announceToScreenReader = function(message, politeness = 'polite') {
    const region = getAriaLiveRegion(politeness);
    region.textContent = '';
    // Use setTimeout to ensure the message is announced
    setTimeout(() => {
      region.textContent = message;
    }, 100);
  };

  // ============================================
  // Keyboard Navigation Helpers
  // ============================================

  /**
   * Trap focus within an element
   */
  window.trapFocus = function(container) {
    const focusableElements = container.querySelectorAll(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    container.addEventListener('keydown', function(e) {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    });
  };

  /**
   * Make element keyboard accessible
   */
  window.makeKeyboardAccessible = function(element, callback) {
    if (!element) return;

    // If it's not already focusable, make it focusable
    if (!element.hasAttribute('tabindex')) {
      element.setAttribute('tabindex', '0');
    }

    // Add keyboard event listeners
    element.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        callback(e);
      }
    });
  };

  // ============================================
  // Focus Management
  // ============================================

  /**
   * Save current focus
   */
  let savedFocus = null;

  window.saveFocus = function() {
    savedFocus = document.activeElement;
  };

  /**
   * Restore saved focus
   */
  window.restoreFocus = function() {
    if (savedFocus && document.contains(savedFocus)) {
      savedFocus.focus();
      savedFocus = null;
    }
  };

  /**
   * Focus first focusable element in container
   */
  window.focusFirstElement = function(container) {
    const focusable = container.querySelector(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    if (focusable) {
      focusable.focus();
    }
  };

  // ============================================
  // Enhanced Keyboard Shortcuts
  // ============================================

  /**
   * Initialize keyboard shortcuts
   */
  function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
      // Skip if user is typing in an input
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
        return;
      }

      // Escape key - close modals, dropdowns, etc.
      if (e.key === 'Escape') {
        // Close any open modals
        const openModal = document.querySelector('.modal[style*="display: block"], .modal:not([style*="display: none"])');
        if (openModal && typeof closeModal !== 'undefined') {
          closeModal();
        }

        // Close any open dropdowns
        document.querySelectorAll('[aria-expanded="true"]').forEach(element => {
          if (element.getAttribute('aria-haspopup') === 'true' || element.classList.contains('dropdown-toggle')) {
            element.setAttribute('aria-expanded', 'false');
            const menu = element.nextElementSibling;
            if (menu && menu.classList.contains('dropdown-menu')) {
              menu.style.display = 'none';
            }
          }
        });
      }

      // '/' key - focus search
      if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
        const searchInput = document.getElementById('global-search-input') || document.getElementById('global-search-input-mobile');
        if (searchInput) {
          e.preventDefault();
          searchInput.focus();
        }
      }
    });
  }

  // ============================================
  // Form Accessibility
  // ============================================

  /**
   * Associate error messages with form fields
   */
  function initFormAccessibility() {
    document.querySelectorAll('.form-group').forEach(group => {
      const input = group.querySelector('input, textarea, select');
      const error = group.querySelector('.form-error, .error-message');
      
      if (input && error) {
        const errorId = error.id || `error-${Math.random().toString(36).substr(2, 9)}`;
        error.id = errorId;
        input.setAttribute('aria-describedby', errorId);
        input.setAttribute('aria-invalid', 'true');
      }
    });
  }

  // ============================================
  // Table Accessibility
  // ============================================

  /**
   * Enhance table accessibility
   */
  function initTableAccessibility() {
    document.querySelectorAll('table').forEach(table => {
      // Ensure table has headers
      const headers = table.querySelectorAll('th');
      if (headers.length === 0) {
        // Add headers if missing
        const firstRow = table.querySelector('tr');
        if (firstRow) {
          firstRow.querySelectorAll('td').forEach((cell, index) => {
            const th = document.createElement('th');
            th.textContent = cell.textContent || `Column ${index + 1}`;
            th.setAttribute('scope', 'col');
            cell.replaceWith(th);
          });
        }
      } else {
        // Add scope attributes to headers
        headers.forEach(header => {
          if (!header.hasAttribute('scope')) {
            const row = header.closest('tr');
            if (row && row.parentElement.tagName === 'THEAD') {
              header.setAttribute('scope', 'col');
            } else if (row && row.parentElement.tagName === 'TBODY') {
              header.setAttribute('scope', 'row');
            }
          }
        });
      }

      // Add caption if missing
      if (!table.querySelector('caption')) {
        const caption = document.createElement('caption');
        caption.className = 'sr-only';
        caption.textContent = 'Data table';
        table.insertBefore(caption, table.firstChild);
      }
    });
  }

  // ============================================
  // Initialize on page load
  // ============================================

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      initSkipLink();
      initKeyboardShortcuts();
      initFormAccessibility();
      initTableAccessibility();
    });
  } else {
    initSkipLink();
    initKeyboardShortcuts();
    initFormAccessibility();
    initTableAccessibility();
  }

})();

