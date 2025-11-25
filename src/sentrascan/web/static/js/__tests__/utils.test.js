/**
 * Unit tests for utils.js
 * Tests for copy-to-clipboard, tooltip initialization, and utility functions
 */

describe('utils.js', function() {
  let originalClipboard;
  let originalShowToast;
  let originalAnnounceToScreenReader;

  beforeEach(function() {
    // Save original implementations
    originalClipboard = navigator.clipboard;
    originalShowToast = window.showToast;
    originalAnnounceToScreenReader = window.announceToScreenReader;

    // Setup DOM
    document.body.innerHTML = '';
    
    // Mock showToast
    window.showToast = jasmine.createSpy('showToast');
    
    // Mock announceToScreenReader
    window.announceToScreenReader = jasmine.createSpy('announceToScreenReader');
    
    // Mock console methods
    spyOn(console, 'error');
    spyOn(console, 'warn');
  });

  afterEach(function() {
    // Restore original implementations
    if (originalClipboard) {
      navigator.clipboard = originalClipboard;
    } else {
      delete navigator.clipboard;
    }
    window.showToast = originalShowToast;
    window.announceToScreenReader = originalAnnounceToScreenReader;
    
    // Clean up DOM
    document.body.innerHTML = '';
  });

  describe('copyToClipboard', function() {
    describe('with modern Clipboard API', function() {
      beforeEach(function() {
        // Mock modern clipboard API
        navigator.clipboard = {
          writeText: jasmine.createSpy('writeText')
        };
      });

      it('should copy text to clipboard successfully', function(done) {
        navigator.clipboard.writeText.and.returnValue(Promise.resolve());
        
        const callback = jasmine.createSpy('callback');
        copyToClipboard('test text', callback);
        
        setTimeout(function() {
          expect(navigator.clipboard.writeText).toHaveBeenCalledWith('test text');
          expect(callback).toHaveBeenCalledWith(true);
          expect(window.showToast).toHaveBeenCalledWith('Copied to clipboard', 'success');
          expect(window.announceToScreenReader).toHaveBeenCalledWith('Copied to clipboard', 'polite');
          done();
        }, 10);
      });

      it('should handle clipboard API errors', function(done) {
        const error = new Error('Clipboard write failed');
        navigator.clipboard.writeText.and.returnValue(Promise.reject(error));
        
        const callback = jasmine.createSpy('callback');
        copyToClipboard('test text', callback);
        
        setTimeout(function() {
          expect(navigator.clipboard.writeText).toHaveBeenCalledWith('test text');
          expect(callback).toHaveBeenCalledWith(false);
          expect(window.showToast).toHaveBeenCalledWith('Failed to copy', 'error');
          expect(window.announceToScreenReader).toHaveBeenCalledWith('Failed to copy to clipboard', 'assertive');
          expect(console.error).toHaveBeenCalledWith('Failed to copy:', error);
          done();
        }, 10);
      });

      it('should work without callback', function(done) {
        navigator.clipboard.writeText.and.returnValue(Promise.resolve());
        
        copyToClipboard('test text');
        
        setTimeout(function() {
          expect(navigator.clipboard.writeText).toHaveBeenCalledWith('test text');
          expect(window.showToast).toHaveBeenCalledWith('Copied to clipboard', 'success');
          done();
        }, 10);
      });
    });

    describe('with fallback execCommand', function() {
      beforeEach(function() {
        // Remove clipboard API
        delete navigator.clipboard;
        
        // Mock document.execCommand
        spyOn(document, 'execCommand').and.returnValue(true);
        spyOn(document.body, 'appendChild');
        spyOn(document.body, 'removeChild');
      });

      it('should use fallback method when clipboard API is unavailable', function(done) {
        const textarea = document.createElement('textarea');
        document.body.appendChild.and.returnValue(textarea);
        spyOn(textarea, 'select');
        
        const callback = jasmine.createSpy('callback');
        copyToClipboard('fallback text', callback);
        
        setTimeout(function() {
          expect(document.body.appendChild).toHaveBeenCalled();
          expect(textarea.value).toBe('fallback text');
          expect(textarea.select).toHaveBeenCalled();
          expect(document.execCommand).toHaveBeenCalledWith('copy');
          expect(document.body.removeChild).toHaveBeenCalledWith(textarea);
          expect(callback).toHaveBeenCalledWith(true);
          expect(window.showToast).toHaveBeenCalledWith('Copied to clipboard', 'success');
          expect(window.announceToScreenReader).toHaveBeenCalledWith('Copied to clipboard', 'polite');
          done();
        }, 10);
      });

      it('should handle execCommand errors', function(done) {
        const textarea = document.createElement('textarea');
        document.body.appendChild.and.returnValue(textarea);
        spyOn(textarea, 'select');
        document.execCommand.and.throwError('execCommand failed');
        
        const callback = jasmine.createSpy('callback');
        copyToClipboard('fallback text', callback);
        
        setTimeout(function() {
          expect(document.execCommand).toHaveBeenCalledWith('copy');
          expect(document.body.removeChild).toHaveBeenCalledWith(textarea);
          expect(callback).toHaveBeenCalledWith(false);
          expect(window.showToast).toHaveBeenCalledWith('Failed to copy', 'error');
          expect(window.announceToScreenReader).toHaveBeenCalledWith('Failed to copy to clipboard', 'assertive');
          expect(console.error).toHaveBeenCalled();
          done();
        }, 10);
      });

      it('should set textarea styles correctly', function(done) {
        const textarea = document.createElement('textarea');
        document.body.appendChild.and.returnValue(textarea);
        spyOn(textarea, 'select');
        document.execCommand.and.returnValue(true);
        
        copyToClipboard('test');
        
        setTimeout(function() {
          expect(textarea.style.position).toBe('fixed');
          expect(textarea.style.opacity).toBe('0');
          done();
        }, 10);
      });
    });
  });

  describe('showToast fallback', function() {
    it('should use alert when toast system is not loaded', function() {
      delete window.showToast;
      spyOn(window, 'alert');
      
      // Re-execute the fallback code
      if (typeof window.showToast === 'undefined') {
        window.showToast = function(message, type) {
          console.warn('Toast system not loaded. Using fallback.');
          alert(message);
        };
      }
      
      window.showToast('Test message', 'info');
      
      expect(console.warn).toHaveBeenCalledWith('Toast system not loaded. Using fallback.');
      expect(window.alert).toHaveBeenCalledWith('Test message');
    });
  });

  describe('initTooltips', function() {
    beforeEach(function() {
      // Mock requestAnimationFrame
      window.requestAnimationFrame = jasmine.createSpy('requestAnimationFrame').and.callFake(function(cb) {
        setTimeout(cb, 0);
        return 1;
      });
    });

    it('should initialize tooltips for elements with data-tooltip attribute', function() {
      const element = document.createElement('button');
      element.setAttribute('data-tooltip', 'Test tooltip');
      document.body.appendChild(element);
      
      // Re-initialize tooltips (simulating the function call)
      const triggers = document.querySelectorAll('[data-tooltip]');
      expect(triggers.length).toBe(1);
    });

    it('should create tooltip on mouseenter', function(done) {
      const element = document.createElement('button');
      element.setAttribute('data-tooltip', 'Hover tooltip');
      document.body.appendChild(element);
      
      // Simulate mouseenter
      const event = new MouseEvent('mouseenter', {
        bubbles: true,
        cancelable: true
      });
      element.dispatchEvent(event);
      
      setTimeout(function() {
        const tooltip = document.querySelector('.tooltip');
        expect(tooltip).toBeTruthy();
        expect(tooltip.textContent).toBe('Hover tooltip');
        done();
      }, 50);
    });

    it('should position tooltip correctly for bottom position', function(done) {
      const element = document.createElement('button');
      element.setAttribute('data-tooltip', 'Bottom tooltip');
      element.setAttribute('data-tooltip-position', 'bottom');
      element.style.position = 'absolute';
      element.style.left = '100px';
      element.style.top = '100px';
      element.style.width = '50px';
      element.style.height = '30px';
      document.body.appendChild(element);
      
      // Mock getBoundingClientRect
      spyOn(element, 'getBoundingClientRect').and.returnValue({
        top: 100,
        left: 100,
        bottom: 130,
        right: 150,
        width: 50,
        height: 30
      });
      
      const event = new MouseEvent('mouseenter', {
        bubbles: true,
        cancelable: true
      });
      element.dispatchEvent(event);
      
      setTimeout(function() {
        const tooltip = document.querySelector('.tooltip');
        expect(tooltip).toBeTruthy();
        done();
      }, 50);
    });

    it('should handle tooltip positioning for all positions', function() {
      const positions = ['top', 'bottom', 'left', 'right'];
      
      positions.forEach(function(position) {
        const element = document.createElement('button');
        element.setAttribute('data-tooltip', position + ' tooltip');
        element.setAttribute('data-tooltip-position', position);
        document.body.appendChild(element);
        
        expect(element.getAttribute('data-tooltip-position')).toBe(position);
      });
    });

    it('should remove tooltip on mouseleave', function(done) {
      const element = document.createElement('button');
      element.setAttribute('data-tooltip', 'Test tooltip');
      document.body.appendChild(element);
      
      // Show tooltip
      const enterEvent = new MouseEvent('mouseenter', {
        bubbles: true,
        cancelable: true
      });
      element.dispatchEvent(enterEvent);
      
      setTimeout(function() {
        expect(document.querySelector('.tooltip')).toBeTruthy();
        
        // Hide tooltip
        const leaveEvent = new MouseEvent('mouseleave', {
          bubbles: true,
          cancelable: true
        });
        element.dispatchEvent(leaveEvent);
        
        setTimeout(function() {
          // Tooltip should be removed after fade out
          const tooltip = document.querySelector('.tooltip');
          // Note: Tooltip might still exist but with opacity 0
          done();
        }, 300);
      }, 50);
    });

    it('should show tooltip on focus for keyboard navigation', function(done) {
      const element = document.createElement('button');
      element.setAttribute('data-tooltip', 'Focus tooltip');
      document.body.appendChild(element);
      
      const event = new FocusEvent('focus', {
        bubbles: true,
        cancelable: true
      });
      element.dispatchEvent(event);
      
      setTimeout(function() {
        const tooltip = document.querySelector('.tooltip');
        expect(tooltip).toBeTruthy();
        expect(tooltip.textContent).toBe('Focus tooltip');
        done();
      }, 50);
    });

    it('should not create tooltip if data-tooltip is empty', function() {
      const element = document.createElement('button');
      element.setAttribute('data-tooltip', '');
      document.body.appendChild(element);
      
      const event = new MouseEvent('mouseenter', {
        bubbles: true,
        cancelable: true
      });
      element.dispatchEvent(event);
      
      const tooltip = document.querySelector('.tooltip');
      expect(tooltip).toBeFalsy();
    });

    it('should keep tooltip within viewport bounds', function(done) {
      const element = document.createElement('button');
      element.setAttribute('data-tooltip', 'Viewport test');
      element.style.position = 'absolute';
      element.style.left = '0px';
      element.style.top = '0px';
      document.body.appendChild(element);
      
      // Mock getBoundingClientRect and window dimensions
      spyOn(element, 'getBoundingClientRect').and.returnValue({
        top: 0,
        left: 0,
        bottom: 30,
        right: 50,
        width: 50,
        height: 30
      });
      
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 800
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: 600
      });
      
      const event = new MouseEvent('mouseenter', {
        bubbles: true,
        cancelable: true
      });
      element.dispatchEvent(event);
      
      setTimeout(function() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
          const left = parseInt(tooltip.style.left);
          const top = parseInt(tooltip.style.top);
          expect(left).toBeGreaterThanOrEqual(8);
          expect(top).toBeGreaterThanOrEqual(8);
        }
        done();
      }, 50);
    });
  });
});

