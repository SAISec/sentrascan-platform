/**
 * Unit tests for realtime.js
 * Tests for Server-Sent Events (SSE) and polling for scan status updates
 */

describe('realtime.js', function() {
  let originalEventSource;
  let originalFetch;
  let originalSetTimeout;
  let originalSetInterval;
  let originalClearInterval;

  beforeEach(function() {
    // Save originals
    originalEventSource = window.EventSource;
    originalFetch = window.fetch;
    
    // Mock console methods
    spyOn(console, 'log');
    spyOn(console, 'error');
    
    // Mock announceToScreenReader
    window.announceToScreenReader = jasmine.createSpy('announceToScreenReader');
    
    // Mock showToast
    window.showToast = jasmine.createSpy('showToast');
    
    // Mock timers
    jasmine.clock().install();
  });

  afterEach(function() {
    // Restore originals
    window.EventSource = originalEventSource;
    window.fetch = originalFetch;
    
    // Clean up connections
    if (window.disconnectScanStatusStream) {
      window.disconnectScanStatusStream('test-scan-id');
    }
    
    // Uninstall clock
    jasmine.clock().uninstall();
  });

  describe('connectScanStatusStream', function() {
    it('should create EventSource connection', function() {
      const mockEventSource = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.OPEN
      };
      
      window.EventSource = jasmine.createSpy('EventSource').and.returnValue(mockEventSource);
      
      const callbacks = {
        onOpen: jasmine.createSpy('onOpen'),
        onUpdate: jasmine.createSpy('onUpdate'),
        onError: jasmine.createSpy('onError')
      };
      
      const eventSource = connectScanStatusStream('test-scan-id', callbacks);
      
      expect(window.EventSource).toHaveBeenCalledWith('/api/v1/scans/test-scan-id/status/stream');
      expect(eventSource).toBe(mockEventSource);
    });

    it('should call onOpen callback when connection opens', function() {
      const mockEventSource = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.OPEN
      };
      
      window.EventSource = jasmine.createSpy('EventSource').and.returnValue(mockEventSource);
      
      const callbacks = {
        onOpen: jasmine.createSpy('onOpen')
      };
      
      connectScanStatusStream('test-scan-id', callbacks);
      
      // Simulate connection open
      if (mockEventSource.onopen) {
        mockEventSource.onopen();
      }
      
      expect(callbacks.onOpen).toHaveBeenCalled();
    });

    it('should call onUpdate callback when receiving status update', function() {
      const mockEventSource = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.OPEN
      };
      
      window.EventSource = jasmine.createSpy('EventSource').and.returnValue(mockEventSource);
      
      const callbacks = {
        onUpdate: jasmine.createSpy('onUpdate')
      };
      
      connectScanStatusStream('test-scan-id', callbacks);
      
      // Simulate message
      const testData = {
        status: 'running',
        total_findings: 5
      };
      
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage({
          data: JSON.stringify(testData)
        });
      }
      
      expect(callbacks.onUpdate).toHaveBeenCalledWith(testData);
    });

    it('should close connection and call onComplete when status is completed', function() {
      const mockEventSource = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.OPEN
      };
      
      window.EventSource = jasmine.createSpy('EventSource').and.returnValue(mockEventSource);
      
      const callbacks = {
        onComplete: jasmine.createSpy('onComplete')
      };
      
      connectScanStatusStream('test-scan-id', callbacks);
      
      // Simulate completed status
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage({
          data: JSON.stringify({ status: 'completed', passed: true })
        });
      }
      
      expect(mockEventSource.close).toHaveBeenCalled();
      expect(callbacks.onComplete).toHaveBeenCalled();
    });

    it('should handle errors and call onError callback', function() {
      const mockEventSource = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.CLOSED
      };
      
      window.EventSource = jasmine.createSpy('EventSource').and.returnValue(mockEventSource);
      
      const callbacks = {
        onError: jasmine.createSpy('onError')
      };
      
      connectScanStatusStream('test-scan-id', callbacks);
      
      // Simulate error
      const error = new Error('Connection failed');
      if (mockEventSource.onerror) {
        mockEventSource.onerror(error);
      }
      
      expect(callbacks.onError).toHaveBeenCalled();
    });

    it('should close existing connection when opening new one for same scan', function() {
      const mockEventSource1 = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.OPEN
      };
      
      const mockEventSource2 = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.OPEN
      };
      
      let callCount = 0;
      window.EventSource = jasmine.createSpy('EventSource').and.callFake(function() {
        callCount++;
        return callCount === 1 ? mockEventSource1 : mockEventSource2;
      });
      
      connectScanStatusStream('test-scan-id', {});
      connectScanStatusStream('test-scan-id', {});
      
      expect(mockEventSource1.close).toHaveBeenCalled();
    });
  });

  describe('disconnectScanStatusStream', function() {
    it('should close and remove connection', function() {
      const mockEventSource = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.OPEN
      };
      
      window.EventSource = jasmine.createSpy('EventSource').and.returnValue(mockEventSource);
      
      connectScanStatusStream('test-scan-id', {});
      disconnectScanStatusStream('test-scan-id');
      
      expect(mockEventSource.close).toHaveBeenCalled();
    });

    it('should handle disconnecting non-existent connection', function() {
      expect(function() {
        disconnectScanStatusStream('non-existent-scan-id');
      }).not.toThrow();
    });
  });

  describe('pollScanStatus', function() {
    it('should poll scan status endpoint', function(done) {
      const mockResponse = {
        ok: true,
        json: jasmine.createSpy('json').and.returnValue(Promise.resolve({
          status: 'running',
          total_findings: 0
        }))
      };
      
      window.fetch = jasmine.createSpy('fetch').and.returnValue(Promise.resolve(mockResponse));
      
      const callbacks = {
        onUpdate: jasmine.createSpy('onUpdate')
      };
      
      pollScanStatus('test-scan-id', callbacks);
      
      setTimeout(function() {
        expect(window.fetch).toHaveBeenCalledWith('/api/v1/scans/test-scan-id/status');
        expect(mockResponse.json).toHaveBeenCalled();
        done();
      }, 10);
    });

    it('should call onUpdate when status changes', function(done) {
      let statusCount = 0;
      const mockResponse = {
        ok: true,
        json: jasmine.createSpy('json').and.callFake(function() {
          statusCount++;
          return Promise.resolve({
            status: statusCount === 1 ? 'running' : 'completed',
            total_findings: 0
          });
        })
      };
      
      window.fetch = jasmine.createSpy('fetch').and.returnValue(Promise.resolve(mockResponse));
      
      const callbacks = {
        onUpdate: jasmine.createSpy('onUpdate'),
        onComplete: jasmine.createSpy('onComplete')
      };
      
      pollScanStatus('test-scan-id', callbacks);
      
      setTimeout(function() {
        expect(callbacks.onUpdate).toHaveBeenCalled();
        done();
      }, 10);
    });

    it('should stop polling when scan is completed', function(done) {
      const mockResponse = {
        ok: true,
        json: jasmine.createSpy('json').and.returnValue(Promise.resolve({
          status: 'completed',
          passed: true,
          total_findings: 5
        }))
      };
      
      window.fetch = jasmine.createSpy('fetch').and.returnValue(Promise.resolve(mockResponse));
      
      const callbacks = {
        onComplete: jasmine.createSpy('onComplete')
      };
      
      const intervalId = pollScanStatus('test-scan-id', callbacks);
      
      setTimeout(function() {
        expect(callbacks.onComplete).toHaveBeenCalled();
        expect(typeof intervalId).toBe('number');
        done();
      }, 10);
    });

    it('should handle fetch errors', function(done) {
      const error = new Error('Network error');
      window.fetch = jasmine.createSpy('fetch').and.returnValue(Promise.reject(error));
      
      const callbacks = {
        onError: jasmine.createSpy('onError')
      };
      
      pollScanStatus('test-scan-id', callbacks);
      
      setTimeout(function() {
        expect(callbacks.onError).toHaveBeenCalled();
        done();
      }, 10);
    });
  });

  describe('autoUpdateScanStatus', function() {
    beforeEach(function() {
      // Mock DOM elements
      const statusEl = document.createElement('div');
      statusEl.id = 'status-element';
      document.body.appendChild(statusEl);
      
      const badgeEl = document.createElement('span');
      badgeEl.id = 'badge-element';
      badgeEl.className = 'badge';
      document.body.appendChild(badgeEl);
      
      const progressEl = document.createElement('div');
      progressEl.id = 'progress-element';
      document.body.appendChild(progressEl);
    });

    it('should update status badge when status changes', function() {
      const badgeElement = document.getElementById('badge-element');
      
      // Mock EventSource
      const mockEventSource = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.OPEN
      };
      
      window.EventSource = jasmine.createSpy('EventSource').and.returnValue(mockEventSource);
      
      autoUpdateScanStatus('test-scan-id', {
        badgeElement: badgeElement
      });
      
      // Simulate status update
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage({
          data: JSON.stringify({ status: 'running' })
        });
      }
      
      expect(badgeElement.className).toContain('badge');
    });

    it('should update progress element when scan is running', function() {
      const progressElement = document.getElementById('progress-element');
      
      const mockEventSource = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.OPEN
      };
      
      window.EventSource = jasmine.createSpy('EventSource').and.returnValue(mockEventSource);
      
      autoUpdateScanStatus('test-scan-id', {
        progressElement: progressElement
      });
      
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage({
          data: JSON.stringify({ status: 'running' })
        });
      }
      
      expect(progressElement.style.display).toBe('block');
    });

    it('should announce status changes to screen readers', function() {
      const mockEventSource = {
        onopen: null,
        onmessage: null,
        onerror: null,
        close: jasmine.createSpy('close'),
        readyState: EventSource.OPEN
      };
      
      window.EventSource = jasmine.createSpy('EventSource').and.returnValue(mockEventSource);
      
      autoUpdateScanStatus('test-scan-id', {});
      
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage({
          data: JSON.stringify({ status: 'completed', passed: true })
        });
      }
      
      expect(window.announceToScreenReader).toHaveBeenCalled();
    });
  });
});

