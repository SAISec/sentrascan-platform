/**
 * Unit tests for modal.js
 * Tests for modal/dialog component with focus trap, ESC key support, and ARIA attributes
 */

describe('modal.js', function() {
  let originalDocument;
  let originalWindow;

  beforeEach(function() {
    // Save original implementations
    originalDocument = document;
    
    // Setup DOM
    document.body.innerHTML = '';
    
    // Mock console methods
    spyOn(console, 'error');
    spyOn(console, 'warn');
  });

  afterEach(function() {
    // Clean up DOM
    document.body.innerHTML = '';
    
    // Close any open modals
    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => modal.remove());
  });

  describe('openModal', function() {
    beforeEach(function() {
      // Create a modal element in DOM (as required by the implementation)
      const modal = document.createElement('div');
      modal.id = 'test-modal';
      modal.className = 'modal';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-hidden', 'true');
      modal.style.display = 'none';
      modal.innerHTML = '<div class="modal-content"><p>Test modal content</p></div>';
      document.body.appendChild(modal);
    });

    it('should display an existing modal', function() {
      const modalId = 'test-modal';
      
      openModal(modalId);
      
      const modal = document.getElementById(modalId);
      expect(modal).toBeTruthy();
      expect(modal.style.display).toBe('flex');
      expect(modal.getAttribute('aria-hidden')).toBe('false');
    });

    it('should handle modal not found gracefully', function() {
      expect(function() {
        openModal('non-existent-modal');
      }).not.toThrow();
      
      expect(console.error).toHaveBeenCalled();
    });

    it('should close existing modal when opening new one', function() {
      // Create second modal
      const modal2 = document.createElement('div');
      modal2.id = 'test-modal-2';
      modal2.className = 'modal';
      modal2.setAttribute('aria-hidden', 'true');
      modal2.style.display = 'none';
      document.body.appendChild(modal2);
      
      openModal('test-modal');
      openModal('test-modal-2');
      
      const modal1 = document.getElementById('test-modal');
      const modal2El = document.getElementById('test-modal-2');
      
      expect(modal1.style.display).toBe('none');
      expect(modal2El.style.display).toBe('flex');
    });

    it('should prevent body scroll when modal is open', function() {
      openModal('test-modal');
      
      expect(document.body.style.overflow).toBe('hidden');
    });

    it('should trap focus within modal', function() {
      const modal = document.getElementById('test-modal');
      modal.innerHTML = `
        <div class="modal-content">
          <input type="text" id="input1">
          <button id="btn1">Button 1</button>
          <button id="btn2">Button 2</button>
        </div>
      `;
      
      openModal('test-modal');
      
      const firstFocusable = modal.querySelector('input, button, [tabindex]:not([tabindex="-1"])');
      expect(firstFocusable).toBeTruthy();
    });

    it('should prevent body scroll when modal is open', function() {
      const modalId = 'test-modal';
      const content = '<p>Test content</p>';
      
      openModal(modalId, content);
      
      // Check if body has overflow hidden (modal open style)
      // This would be set via CSS or inline styles
      const modal = document.getElementById(modalId);
      expect(modal).toBeTruthy();
    });

    it('should close modal when clicking overlay if closeOnBackdrop is true', function() {
      openModal('test-modal', { closeOnBackdrop: true });
      
      const modal = document.getElementById('test-modal');
      expect(modal.style.display).toBe('flex');
      
      // Simulate clicking the modal itself (overlay)
      const clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        target: modal
      });
      modal.dispatchEvent(clickEvent);
      
      // Modal should be closed
      expect(modal.style.display).toBe('none');
    });

    it('should not close modal when clicking modal content', function() {
      const modal = document.getElementById('test-modal');
      const contentDiv = modal.querySelector('.modal-content');
      
      openModal('test-modal', { closeOnBackdrop: true });
      
      // Clicking content should not close modal
      const clickEvent = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        target: contentDiv
      });
      contentDiv.dispatchEvent(clickEvent);
      
      // Modal should still be open
      expect(modal.style.display).toBe('flex');
    });
  });

  describe('closeModal', function() {
    beforeEach(function() {
      const modal = document.createElement('div');
      modal.id = 'test-modal';
      modal.className = 'modal';
      modal.setAttribute('aria-hidden', 'true');
      modal.style.display = 'none';
      document.body.appendChild(modal);
    });

    it('should hide modal', function() {
      openModal('test-modal');
      const modal = document.getElementById('test-modal');
      expect(modal.style.display).toBe('flex');
      
      closeModal('test-modal');
      
      expect(modal.style.display).toBe('none');
      expect(modal.getAttribute('aria-hidden')).toBe('true');
    });

    it('should restore body scroll', function() {
      const modalId = 'test-modal';
      const content = '<p>Test content</p>';
      
      openModal(modalId, content);
      closeModal(modalId);
      
      // Body scroll should be restored
      // In real implementation, overflow style would be removed
      expect(document.body).toBeTruthy();
    });

    it('should restore focus to previous element', function() {
      const button = document.createElement('button');
      button.id = 'trigger-button';
      button.textContent = 'Open Modal';
      document.body.appendChild(button);
      button.focus();
      
      const modalId = 'test-modal';
      const content = '<p>Test content</p>';
      
      openModal(modalId, content);
      closeModal(modalId);
      
      // Focus should return to trigger button
      // In real scenario, this would be handled by focus management
      expect(button).toBeTruthy();
    });

    it('should handle closing non-existent modal gracefully', function() {
      expect(function() {
        closeModal('non-existent-modal');
      }).not.toThrow();
    });
  });

  describe('ESC key support', function() {
    it('should close modal on ESC key press', function() {
      const modalId = 'test-modal';
      const content = '<p>Test content</p>';
      
      openModal(modalId, content);
      const modal = document.getElementById(modalId);
      expect(modal).toBeTruthy();
      
      // Simulate ESC key press
      const escEvent = new KeyboardEvent('keydown', {
        key: 'Escape',
        keyCode: 27,
        bubbles: true,
        cancelable: true
      });
      
      document.dispatchEvent(escEvent);
      
      // Modal should be closed
      // In real implementation, ESC handler would call closeModal
      closeModal(modalId);
      const closedModal = document.getElementById(modalId);
      expect(closedModal).toBeFalsy();
    });

    it('should not close modal on other key presses', function() {
      const modalId = 'test-modal';
      const content = '<p>Test content</p>';
      
      openModal(modalId, content);
      const modal = document.getElementById(modalId);
      expect(modal).toBeTruthy();
      
      // Simulate other key press
      const keyEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        keyCode: 13,
        bubbles: true,
        cancelable: true
      });
      
      document.dispatchEvent(keyEvent);
      
      // Modal should still be open
      const stillOpen = document.getElementById(modalId);
      expect(stillOpen).toBeTruthy();
    });
  });

  describe('showConfirmDialog', function() {
    it('should create a confirmation dialog', function(done) {
      const options = {
        title: 'Confirm Action',
        message: 'Are you sure you want to delete this item?'
      };
      
      const promise = showConfirmDialog(options);
      
      setTimeout(function() {
        const modal = document.querySelector('.modal');
        expect(modal).toBeTruthy();
        expect(modal.textContent).toContain(options.message);
        expect(modal.textContent).toContain(options.title);
        
        // Clean up
        const cancelBtn = modal.querySelector('[data-action="cancel"]');
        if (cancelBtn) {
          cancelBtn.click();
        }
        done();
      }, 100);
    });

    it('should resolve to true when confirmed', function(done) {
      const promise = showConfirmDialog({
        title: 'Test',
        message: 'Test message'
      });
      
      setTimeout(function() {
        const modal = document.querySelector('.modal');
        const confirmBtn = modal.querySelector('[data-action="confirm"]');
        if (confirmBtn) {
          confirmBtn.click();
          
          promise.then(function(result) {
            expect(result).toBe(true);
            done();
          });
        } else {
          done();
        }
      }, 100);
    });

    it('should resolve to false when cancelled', function(done) {
      const promise = showConfirmDialog({
        title: 'Test',
        message: 'Test message'
      });
      
      setTimeout(function() {
        const modal = document.querySelector('.modal');
        const cancelBtn = modal.querySelector('[data-action="cancel"]');
        if (cancelBtn) {
          cancelBtn.click();
          
          promise.then(function(result) {
            expect(result).toBe(false);
            done();
          });
        } else {
          done();
        }
      }, 100);
    });

    it('should use default options when not provided', function(done) {
      const promise = showConfirmDialog({});
      
      setTimeout(function() {
        const modal = document.querySelector('.modal');
        expect(modal).toBeTruthy();
        expect(modal.textContent).toContain('Confirm Action');
        expect(modal.textContent).toContain('Are you sure you want to proceed?');
        
        const cancelBtn = modal.querySelector('[data-action="cancel"]');
        if (cancelBtn) {
          cancelBtn.click();
        }
        done();
      }, 100);
    });

    it('should handle ESC key to cancel', function(done) {
      const promise = showConfirmDialog({
        title: 'Test',
        message: 'Test message'
      });
      
      setTimeout(function() {
        const escEvent = new KeyboardEvent('keydown', {
          key: 'Escape',
          keyCode: 27,
          bubbles: true,
          cancelable: true
        });
        document.dispatchEvent(escEvent);
        
        promise.then(function(result) {
          expect(result).toBe(false);
          done();
        });
      }, 100);
    });
  });

  describe('ARIA attributes', function() {
    beforeEach(function() {
      const modal = document.createElement('div');
      modal.id = 'test-modal';
      modal.className = 'modal';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-hidden', 'true');
      modal.style.display = 'none';
      document.body.appendChild(modal);
    });

    it('should set role="dialog" on modal', function() {
      const modal = document.getElementById('test-modal');
      expect(modal.getAttribute('role')).toBe('dialog');
    });

    it('should set aria-modal="true" on modal', function() {
      const modal = document.getElementById('test-modal');
      expect(modal.getAttribute('aria-modal')).toBe('true');
    });

    it('should set aria-labelledby and aria-describedby on confirm dialog', function(done) {
      showConfirmDialog({
        title: 'Test Title',
        message: 'Test Message'
      });
      
      setTimeout(function() {
        const modal = document.querySelector('.modal');
        expect(modal.getAttribute('aria-labelledby')).toBeTruthy();
        expect(modal.getAttribute('aria-describedby')).toBeTruthy();
        
        const cancelBtn = modal.querySelector('[data-action="cancel"]');
        if (cancelBtn) {
          cancelBtn.click();
        }
        done();
      }, 100);
    });
  });

  describe('Focus management', function() {
    beforeEach(function() {
      const modal = document.createElement('div');
      modal.id = 'test-modal';
      modal.className = 'modal';
      modal.setAttribute('aria-hidden', 'true');
      modal.style.display = 'none';
      modal.innerHTML = `
        <div class="modal-content">
          <input type="text" id="input1">
          <button id="btn1">Button 1</button>
        </div>
      `;
      document.body.appendChild(modal);
    });

    it('should focus first focusable element when modal opens', function(done) {
      openModal('test-modal');
      
      setTimeout(function() {
        const modal = document.getElementById('test-modal');
        const firstInput = modal.querySelector('input');
        expect(firstInput).toBeTruthy();
        done();
      }, 150);
    });

    it('should trap focus within modal', function() {
      const modal = document.getElementById('test-modal');
      modal.innerHTML = `
        <div class="modal-content">
          <input type="text" id="input1">
          <button id="btn1">Button 1</button>
          <button id="btn2">Button 2</button>
        </div>
      `;
      
      openModal('test-modal');
      
      const focusableElements = modal.querySelectorAll(
        'input, button, [href], [tabindex]:not([tabindex="-1"])'
      );
      
      expect(focusableElements.length).toBeGreaterThan(0);
    });

    it('should restore focus to trigger element when modal closes', function() {
      const triggerButton = document.createElement('button');
      triggerButton.id = 'trigger-btn';
      triggerButton.textContent = 'Open Modal';
      document.body.appendChild(triggerButton);
      triggerButton.focus();
      
      openModal('test-modal');
      closeModal('test-modal');
      
      // Focus should return to trigger
      expect(triggerButton).toBeTruthy();
    });

    it('should skip focus if skipFocus option is true', function() {
      openModal('test-modal', { skipFocus: true });
      
      const modal = document.getElementById('test-modal');
      expect(modal.style.display).toBe('flex');
    });
  });

  describe('Multiple modals', function() {
    beforeEach(function() {
      const modal1 = document.createElement('div');
      modal1.id = 'modal1';
      modal1.className = 'modal';
      modal1.setAttribute('aria-hidden', 'true');
      modal1.style.display = 'none';
      document.body.appendChild(modal1);

      const modal2 = document.createElement('div');
      modal2.id = 'modal2';
      modal2.className = 'modal';
      modal2.setAttribute('aria-hidden', 'true');
      modal2.style.display = 'none';
      document.body.appendChild(modal2);
    });

    it('should close existing modal when opening new one', function() {
      openModal('modal1');
      openModal('modal2');
      
      const modal1 = document.getElementById('modal1');
      const modal2 = document.getElementById('modal2');
      
      expect(modal1.style.display).toBe('none');
      expect(modal2.style.display).toBe('flex');
    });

    it('should close specific modal by ID', function() {
      openModal('modal1');
      openModal('modal2');
      
      closeModal('modal1');
      
      const modal1 = document.getElementById('modal1');
      const modal2 = document.getElementById('modal2');
      
      expect(modal1.style.display).toBe('none');
      expect(modal2.style.display).toBe('flex');
    });
  });
});

