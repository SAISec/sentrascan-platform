/**
 * Unit tests for toast.js
 * Tests for toast notification system with stacking, auto-dismiss, and accessibility
 */

describe('toast.js', function() {
  let originalShowToast;
  let originalAnnounceToScreenReader;

  beforeEach(function() {
    // Clean up DOM
    document.body.innerHTML = '';
    document.head.innerHTML = '';
    
    // Mock announceToScreenReader
    window.announceToScreenReader = jasmine.createSpy('announceToScreenReader');
    
    // Mock console methods
    spyOn(console, 'log');
    spyOn(console, 'error');
    
    // Load toast.js will create the container
  });

  afterEach(function() {
    // Clean up
    const container = document.getElementById('toast-container');
    if (container) {
      container.innerHTML = '';
    }
  });

  describe('showToast', function() {
    it('should create and display a toast notification', function() {
      const toastId = showToast('Test message', 'info');
      
      const toast = document.getElementById(toastId);
      expect(toast).toBeTruthy();
      expect(toast.classList.contains('toast')).toBe(true);
      expect(toast.classList.contains('toast-info')).toBe(true);
      expect(toast.getAttribute('role')).toBe('alert');
    });

    it('should create toast with correct type classes', function() {
      const types = ['success', 'error', 'warning', 'info'];
      
      types.forEach(function(type) {
        const toastId = showToast('Test', type);
        const toast = document.getElementById(toastId);
        expect(toast.classList.contains(`toast-${type}`)).toBe(true);
        dismissToast(toastId);
      });
    });

    it('should set correct aria-live attribute based on type', function() {
      const errorToastId = showToast('Error message', 'error');
      const errorToast = document.getElementById(errorToastId);
      expect(errorToast.getAttribute('aria-live')).toBe('assertive');
      dismissToast(errorToastId);
      
      const infoToastId = showToast('Info message', 'info');
      const infoToast = document.getElementById(infoToastId);
      expect(infoToast.getAttribute('aria-live')).toBe('polite');
      dismissToast(infoToastId);
    });

    it('should display toast message', function() {
      const message = 'This is a test toast message';
      const toastId = showToast(message, 'info');
      
      const toast = document.getElementById(toastId);
      const messageEl = toast.querySelector('.toast-message');
      expect(messageEl).toBeTruthy();
      expect(messageEl.textContent).toBe(message);
    });

    it('should display icon based on type', function() {
      const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
      };
      
      Object.keys(icons).forEach(function(type) {
        const toastId = showToast('Test', type);
        const toast = document.getElementById(toastId);
        const icon = toast.querySelector('.toast-icon');
        expect(icon).toBeTruthy();
        expect(icon.textContent).toBe(icons[type]);
        dismissToast(toastId);
      });
    });

    it('should auto-dismiss after duration', function(done) {
      const toastId = showToast('Auto-dismiss test', 'info', { duration: 100 });
      
      setTimeout(function() {
        const toast = document.getElementById(toastId);
        expect(toast).toBeFalsy();
        done();
      }, 200);
    });

    it('should not auto-dismiss if duration is 0', function(done) {
      const toastId = showToast('No auto-dismiss', 'info', { duration: 0 });
      
      setTimeout(function() {
        const toast = document.getElementById(toastId);
        expect(toast).toBeTruthy();
        dismissToast(toastId);
        done();
      }, 100);
    });

    it('should add close button when dismissible is true', function() {
      const toastId = showToast('Dismissible toast', 'info', { dismissible: true });
      
      const toast = document.getElementById(toastId);
      const closeButton = toast.querySelector('.toast-close');
      expect(closeButton).toBeTruthy();
      expect(closeButton.getAttribute('aria-label')).toBe('Close notification');
    });

    it('should not add close button when dismissible is false', function() {
      const toastId = showToast('Non-dismissible toast', 'info', { dismissible: false });
      
      const toast = document.getElementById(toastId);
      const closeButton = toast.querySelector('.toast-close');
      expect(closeButton).toBeFalsy();
    });

    it('should add action button when provided', function() {
      const actionLabel = 'Undo';
      const onAction = jasmine.createSpy('onAction');
      const toastId = showToast('Action toast', 'info', {
        action: true,
        actionLabel: actionLabel,
        onAction: onAction
      });
      
      const toast = document.getElementById(toastId);
      const actionButton = toast.querySelector('.btn');
      expect(actionButton).toBeTruthy();
      expect(actionButton.textContent).toBe(actionLabel);
      
      actionButton.click();
      expect(onAction).toHaveBeenCalled();
    });

    it('should return unique toast ID', function() {
      const id1 = showToast('Toast 1', 'info');
      const id2 = showToast('Toast 2', 'info');
      
      expect(id1).not.toBe(id2);
      expect(id1).toContain('toast-');
      expect(id2).toContain('toast-');
    });

    it('should stack multiple toasts', function() {
      showToast('Toast 1', 'info');
      showToast('Toast 2', 'success');
      showToast('Toast 3', 'error');
      
      const container = document.getElementById('toast-container');
      expect(container.children.length).toBe(3);
    });
  });

  describe('dismissToast', function() {
    it('should remove toast from DOM', function(done) {
      const toastId = showToast('Test toast', 'info');
      const toast = document.getElementById(toastId);
      expect(toast).toBeTruthy();
      
      dismissToast(toastId);
      
      setTimeout(function() {
        const removedToast = document.getElementById(toastId);
        expect(removedToast).toBeFalsy();
        done();
      }, 350);
    });

    it('should handle dismissing non-existent toast gracefully', function() {
      expect(function() {
        dismissToast('non-existent-toast');
      }).not.toThrow();
    });

    it('should apply slide-out animation when dismissing', function() {
      const toastId = showToast('Test toast', 'info');
      const toast = document.getElementById(toastId);
      
      dismissToast(toastId);
      
      expect(toast.style.animation).toContain('slideOutRight');
    });
  });

  describe('Toast container', function() {
    it('should create toast container on load', function() {
      const container = document.getElementById('toast-container');
      expect(container).toBeTruthy();
      expect(container.getAttribute('aria-live')).toBe('polite');
      expect(container.getAttribute('aria-atomic')).toBe('false');
    });

    it('should have correct container styles', function() {
      const container = document.getElementById('toast-container');
      expect(container.style.position).toBe('fixed');
      expect(container.style.top).toBe('20px');
      expect(container.style.right).toBe('20px');
    });
  });
});

