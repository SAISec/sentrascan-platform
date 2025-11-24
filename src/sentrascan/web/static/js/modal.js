/**
 * SentraScan Platform - Modal/Dialog Component
 * Reusable modal system with focus trap, ESC key support, and accessibility features
 */

(function() {
  'use strict';

  // Modal state
  let activeModal = null;
  let previousFocus = null;
  let focusableElements = [];

  /**
   * Open a modal
   * @param {string} modalId - ID of the modal element
   * @param {Object} options - Configuration options
   */
  window.openModal = function(modalId, options = {}) {
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.error(`Modal with ID "${modalId}" not found`);
      return;
    }

    // Close any existing modal
    if (activeModal) {
      closeModal(activeModal);
    }

    activeModal = modal;
    previousFocus = document.activeElement;

    // Show modal
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    // Get focusable elements
    focusableElements = getFocusableElements(modal);
    
    // Focus first element
    if (focusableElements.length > 0 && !options.skipFocus) {
      setTimeout(() => {
        focusableElements[0].focus();
      }, 100);
    }

    // Set up focus trap
    setupFocusTrap(modal);

    // Set up ESC key handler
    const escHandler = function(e) {
      if (e.key === 'Escape' && activeModal === modal) {
        if (options.onEscape) {
          options.onEscape();
        } else {
          closeModal(modalId);
        }
      }
    };
    modal._escHandler = escHandler;
    document.addEventListener('keydown', escHandler);

    // Set up click outside handler
    const clickHandler = function(e) {
      if (e.target === modal && options.closeOnBackdrop !== false) {
        closeModal(modalId);
      }
    };
    modal._clickHandler = clickHandler;
    modal.addEventListener('click', clickHandler);

    // Call onOpen callback
    if (options.onOpen) {
      options.onOpen();
    }
  };

  /**
   * Close a modal
   * @param {string} modalId - ID of the modal element
   */
  window.closeModal = function(modalId) {
    const modal = typeof modalId === 'string' ? document.getElementById(modalId) : modalId;
    if (!modal) return;

    // Hide modal
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';

    // Remove event handlers
    if (modal._escHandler) {
      document.removeEventListener('keydown', modal._escHandler);
      delete modal._escHandler;
    }
    if (modal._clickHandler) {
      modal.removeEventListener('click', modal._clickHandler);
      delete modal._clickHandler;
    }

    // Restore focus
    if (previousFocus && previousFocus.focus) {
      previousFocus.focus();
    }

    // Clear state
    if (activeModal === modal) {
      activeModal = null;
    }
    previousFocus = null;
    focusableElements = [];
  };

  /**
   * Get all focusable elements within a container
   */
  function getFocusableElements(container) {
    const selector = 'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';
    return Array.from(container.querySelectorAll(selector)).filter(el => {
      return el.offsetWidth > 0 && el.offsetHeight > 0;
    });
  }

  /**
   * Set up focus trap within modal
   */
  function setupFocusTrap(modal) {
    const trapHandler = function(e) {
      if (e.key !== 'Tab' || activeModal !== modal) return;

      const focusable = getFocusableElements(modal);
      if (focusable.length === 0) return;

      const firstElement = focusable[0];
      const lastElement = focusable[focusable.length - 1];

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
    };

    modal._trapHandler = trapHandler;
    modal.addEventListener('keydown', trapHandler);
  }

  /**
   * Create a confirmation dialog
   * @param {Object} options - Configuration options
   * @returns {Promise<boolean>} - Resolves to true if confirmed, false if cancelled
   */
  window.showConfirmDialog = function(options = {}) {
    return new Promise((resolve) => {
      const {
        title = 'Confirm Action',
        message = 'Are you sure you want to proceed?',
        confirmText = 'Confirm',
        cancelText = 'Cancel',
        confirmClass = 'btn-primary',
        cancelClass = 'btn-secondary',
        destructive = false
      } = options;

      // Create modal HTML
      const modalId = 'confirm-dialog-' + Date.now();
      const modal = document.createElement('div');
      modal.id = modalId;
      modal.className = 'modal';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-labelledby', modalId + '-title');
      modal.setAttribute('aria-describedby', modalId + '-message');
      modal.style.display = 'none';

      modal.innerHTML = `
        <div class="modal-content card" style="max-width: 500px; width: 90%;">
          <h2 id="${modalId}-title" style="margin: 0 0 var(--spacing-md) 0;">${escapeHtml(title)}</h2>
          <p id="${modalId}-message" style="margin: 0 0 var(--spacing-lg) 0; color: var(--color-text-secondary);">
            ${escapeHtml(message)}
          </p>
          <div class="form-actions" style="display: flex; gap: var(--spacing-md); justify-content: flex-end;">
            <button class="btn ${cancelClass}" data-action="cancel">${escapeHtml(cancelText)}</button>
            <button class="btn ${destructive ? 'btn-danger' : confirmClass}" data-action="confirm" autofocus>${escapeHtml(confirmText)}</button>
          </div>
        </div>
      `;

      // Add to DOM
      document.body.appendChild(modal);

      // Set up handlers
      const handleAction = (action) => {
        closeModal(modalId);
        setTimeout(() => {
          document.body.removeChild(modal);
        }, 300);
        resolve(action === 'confirm');
      };

      modal.querySelector('[data-action="confirm"]').addEventListener('click', () => handleAction('confirm'));
      modal.querySelector('[data-action="cancel"]').addEventListener('click', () => handleAction('cancel'));

      // Open modal
      openModal(modalId, {
        onEscape: () => handleAction('cancel'),
        closeOnBackdrop: false
      });
    });
  };

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Initialize modals on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initModals);
  } else {
    initModals();
  }

  function initModals() {
    // Set up close buttons
    document.querySelectorAll('.modal-close, [data-modal-close]').forEach(btn => {
      btn.addEventListener('click', function() {
        const modal = this.closest('.modal');
        if (modal) {
          closeModal(modal.id);
        }
      });
    });

    // Set up modal triggers
    document.querySelectorAll('[data-modal-open]').forEach(trigger => {
      trigger.addEventListener('click', function() {
        const modalId = this.getAttribute('data-modal-open');
        openModal(modalId);
      });
    });
  }

})();

