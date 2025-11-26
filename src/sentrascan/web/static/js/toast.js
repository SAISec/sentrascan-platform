/**
 * SentraScan Platform - Toast Notification System
 * Toast notifications with stacking, auto-dismiss, and accessibility
 */

(function() {
  'use strict';

  // Use existing container if present, otherwise create one
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.setAttribute('aria-live', 'polite');
    toastContainer.setAttribute('aria-atomic', 'false');
    toastContainer.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: var(--z-index-tooltip);
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
      max-width: 400px;
      pointer-events: none;
    `;
    document.body.appendChild(toastContainer);
  } else {
    // Ensure existing container has proper styles
    toastContainer.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: var(--z-index-tooltip);
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
      max-width: 400px;
      pointer-events: none;
    `;
  }

  let toastCount = 0;

  /**
   * Show a toast notification
   * @param {string} message - Toast message
   * @param {string} type - Toast type: 'success', 'error', 'warning', 'info'
   * @param {Object} options - Configuration options
   * @returns {string} - Toast ID
   */
  window.showToast = function(message, type = 'info', options = {}) {
    const {
      duration = 5000,
      dismissible = true,
      action = null,
      actionLabel = null,
      onAction = null
    } = options;

    toastCount++;
    const toastId = 'toast-' + toastCount;
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');
    toast.style.cssText = `
      background: var(--color-bg-primary);
      border: 1px solid var(--color-border-light);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      padding: var(--spacing-md);
      display: flex;
      align-items: flex-start;
      gap: var(--spacing-sm);
      pointer-events: auto;
      animation: slideInRight 0.3s ease-out;
      max-width: 100%;
    `;

    // Icon
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };
    const icon = document.createElement('span');
    icon.className = 'toast-icon';
    icon.textContent = icons[type] || icons.info;
    icon.style.cssText = `
      flex-shrink: 0;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: var(--radius-full);
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-bold);
      color: var(--color-text-inverse);
      background: var(--color-${type === 'warning' ? 'warning' : type === 'error' ? 'error' : type === 'success' ? 'success' : 'info'});
    `;

    // Message
    const messageEl = document.createElement('div');
    messageEl.className = 'toast-message';
    messageEl.style.cssText = `
      flex: 1;
      font-size: var(--font-size-sm);
      line-height: 1.5;
      color: var(--color-text-primary);
    `;
    messageEl.textContent = message;

    // Action button (optional)
    let actionButton = null;
    if (action && actionLabel) {
      actionButton = document.createElement('button');
      actionButton.className = 'btn btn-sm';
      actionButton.textContent = actionLabel;
      actionButton.style.cssText = `
        flex-shrink: 0;
        padding: var(--spacing-xs) var(--spacing-sm);
        font-size: var(--font-size-xs);
      `;
      actionButton.addEventListener('click', () => {
        if (onAction) onAction();
        dismissToast(toastId);
      });
    }

    // Close button
    let closeButton = null;
    if (dismissible) {
      closeButton = document.createElement('button');
      closeButton.className = 'toast-close';
      closeButton.setAttribute('aria-label', 'Close notification');
      closeButton.innerHTML = '×';
      closeButton.style.cssText = `
        flex-shrink: 0;
        background: none;
        border: none;
        font-size: var(--font-size-xl);
        color: var(--color-text-secondary);
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--radius-sm);
        transition: background-color var(--transition-fast);
      `;
      closeButton.addEventListener('click', () => dismissToast(toastId));
      closeButton.addEventListener('mouseenter', function() {
        this.style.backgroundColor = 'var(--color-gray-100)';
      });
      closeButton.addEventListener('mouseleave', function() {
        this.style.backgroundColor = 'transparent';
      });
    }

    // Assemble toast
    toast.appendChild(icon);
    toast.appendChild(messageEl);
    if (actionButton) toast.appendChild(actionButton);
    if (closeButton) toast.appendChild(closeButton);

    // Add to container
    toastContainer.appendChild(toast);

    // Auto-dismiss
    if (duration > 0) {
      setTimeout(() => {
        dismissToast(toastId);
      }, duration);
    }

    return toastId;
  };

  /**
   * Dismiss a toast
   * @param {string} toastId - Toast ID
   */
  window.dismissToast = function(toastId) {
    const toast = document.getElementById(toastId);
    if (!toast) return;

    toast.style.animation = 'slideOutRight 0.3s ease-in';
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  };

  // Add CSS animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideInRight {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    
    @keyframes slideOutRight {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);

})();

