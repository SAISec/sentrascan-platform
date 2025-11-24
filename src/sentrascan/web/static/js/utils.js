/**
 * SentraScan Platform - Utility Functions
 * Common utility functions for the application
 */

(function() {
  'use strict';

  // ============================================
  // Copy to Clipboard
  // ============================================

  window.copyToClipboard = function(text, callback) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function() {
        if (callback) callback(true);
        showToast('Copied to clipboard', 'success');
        // Announce to screen readers
        if (typeof announceToScreenReader !== 'undefined') {
          announceToScreenReader('Copied to clipboard', 'polite');
        }
      }).catch(function(err) {
        console.error('Failed to copy:', err);
        if (callback) callback(false);
        showToast('Failed to copy', 'error');
        // Announce to screen readers
        if (typeof announceToScreenReader !== 'undefined') {
          announceToScreenReader('Failed to copy to clipboard', 'assertive');
        }
      });
    } else {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        document.body.removeChild(textarea);
        if (callback) callback(true);
        showToast('Copied to clipboard', 'success');
        // Announce to screen readers
        if (typeof announceToScreenReader !== 'undefined') {
          announceToScreenReader('Copied to clipboard', 'polite');
        }
      } catch (err) {
        document.body.removeChild(textarea);
        console.error('Failed to copy:', err);
        if (callback) callback(false);
        showToast('Failed to copy', 'error');
        // Announce to screen readers
        if (typeof announceToScreenReader !== 'undefined') {
          announceToScreenReader('Failed to copy to clipboard', 'assertive');
        }
      }
    }
  };

  // ============================================
  // Toast Notification (delegates to toast.js)
  // ============================================

  // Toast functionality is now in toast.js
  // This is kept for backward compatibility
  if (typeof window.showToast === 'undefined') {
    window.showToast = function(message, type) {
      console.warn('Toast system not loaded. Using fallback.');
      alert(message);
    };
  }

  // ============================================
  // Tooltip Implementation
  // ============================================

  function initTooltips() {
    const triggers = document.querySelectorAll('[data-tooltip]');
    
    triggers.forEach(trigger => {
      let tooltip = null;
      let timeout = null;
      
      function showTooltip(e) {
        clearTimeout(timeout);
        
        const text = trigger.getAttribute('data-tooltip');
        const position = trigger.getAttribute('data-tooltip-position') || 'bottom';
        
        if (!text) return;
        
        // Remove existing tooltip
        if (tooltip) {
          document.body.removeChild(tooltip);
        }
        
        // Create tooltip
        tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
          position: absolute;
          background: var(--color-gray-800);
          color: var(--color-text-inverse);
          padding: 6px 12px;
          border-radius: var(--radius-sm);
          font-size: var(--font-size-xs);
          white-space: nowrap;
          z-index: var(--z-index-tooltip);
          pointer-events: none;
          opacity: 0;
          transition: opacity 0.2s;
        `;
        
        document.body.appendChild(tooltip);
        
        // Position tooltip
        const rect = trigger.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let top, left;
        switch (position) {
          case 'top':
            top = rect.top - tooltipRect.height - 8;
            left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
            break;
          case 'bottom':
            top = rect.bottom + 8;
            left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
            break;
          case 'left':
            top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
            left = rect.left - tooltipRect.width - 8;
            break;
          case 'right':
            top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
            left = rect.right + 8;
            break;
          default:
            top = rect.bottom + 8;
            left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        }
        
        // Keep tooltip within viewport
        left = Math.max(8, Math.min(left, window.innerWidth - tooltipRect.width - 8));
        top = Math.max(8, Math.min(top, window.innerHeight - tooltipRect.height - 8));
        
        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
        
        // Show tooltip
        requestAnimationFrame(() => {
          tooltip.style.opacity = '1';
        });
      }
      
      function hideTooltip() {
        timeout = setTimeout(() => {
          if (tooltip) {
            tooltip.style.opacity = '0';
            setTimeout(() => {
              if (tooltip && tooltip.parentNode) {
                document.body.removeChild(tooltip);
              }
              tooltip = null;
            }, 200);
          }
        }, 100);
      }
      
      trigger.addEventListener('mouseenter', showTooltip);
      trigger.addEventListener('mouseleave', hideTooltip);
      trigger.addEventListener('focus', showTooltip);
      trigger.addEventListener('blur', hideTooltip);
    });
  }

  // Initialize tooltips on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTooltips);
  } else {
    initTooltips();
  }

  // Re-initialize tooltips when new content is added
  const observer = new MutationObserver(function(mutations) {
    initTooltips();
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

})();

