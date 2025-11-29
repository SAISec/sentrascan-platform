/**
 * SentraScan Platform - Real-time Updates
 * Server-Sent Events (SSE) client for scan status updates
 */

(function() {
  'use strict';

  let eventSource = null;
  const activeConnections = new Map();

  /**
   * Connect to scan status stream
   * @param {string} scanId - Scan ID to monitor
   * @param {Object} callbacks - Callback functions
   * @returns {EventSource} - EventSource instance
   */
  window.connectScanStatusStream = function(scanId, callbacks = {}) {
    // Close existing connection for this scan
    if (activeConnections.has(scanId)) {
      activeConnections.get(scanId).close();
    }

    const url = `/api/v1/scans/${scanId}/status/stream`;
    const eventSource = new EventSource(url);

    eventSource.onopen = function() {
      console.log(`Connected to scan status stream for ${scanId}`);
      if (callbacks.onOpen) {
        callbacks.onOpen();
      }
    };

    eventSource.onmessage = function(event) {
      try {
        const data = JSON.parse(event.data);
        
        if (data.error) {
          console.error('SSE error:', data.error);
          if (callbacks.onError) {
            callbacks.onError(data.error);
          }
          return;
        }

        if (data.status === 'completed') {
          eventSource.close();
          activeConnections.delete(scanId);
          if (callbacks.onComplete) {
            callbacks.onComplete(data);
          }
          return;
        }

        // Update scan status
        if (callbacks.onUpdate) {
          callbacks.onUpdate(data);
        }
      } catch (e) {
        console.error('Error parsing SSE data:', e);
      }
    };

    eventSource.onerror = function(error) {
      console.error('SSE connection error:', error);
      if (callbacks.onError) {
        callbacks.onError(error);
      }
      
      // Try to reconnect after delay
      if (eventSource.readyState === EventSource.CLOSED) {
        setTimeout(() => {
          if (activeConnections.has(scanId)) {
            connectScanStatusStream(scanId, callbacks);
          }
        }, 5000);
      }
    };

    activeConnections.set(scanId, eventSource);
    return eventSource;
  };

  /**
   * Disconnect from scan status stream
   * @param {string} scanId - Scan ID
   */
  window.disconnectScanStatusStream = function(scanId) {
    if (activeConnections.has(scanId)) {
      activeConnections.get(scanId).close();
      activeConnections.delete(scanId);
    }
  };

  /**
   * Poll scan status (fallback for browsers without SSE support)
   * @param {string} scanId - Scan ID
   * @param {Object} callbacks - Callback functions
   * @returns {number} - Interval ID
   */
  window.pollScanStatus = function(scanId, callbacks = {}) {
    let intervalId = null;
    let lastStatus = null;

    const poll = async function() {
      try {
        const response = await fetch(`/api/v1/scans/${scanId}/status`, {
          credentials: 'include'
        });
        if (!response.ok) {
          throw new Error('Failed to fetch scan status');
        }
        
        const data = await response.json();
        
        if (data.status !== lastStatus) {
          if (callbacks.onUpdate) {
            callbacks.onUpdate(data);
          }
          lastStatus = data.status;
        }

        // Stop polling if scan is completed
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(intervalId);
          if (callbacks.onComplete) {
            callbacks.onComplete(data);
          }
        }
      } catch (error) {
        console.error('Error polling scan status:', error);
        if (callbacks.onError) {
          callbacks.onError(error);
        }
      }
    };

    // Poll immediately, then every 3 seconds
    poll();
    intervalId = setInterval(poll, 3000);

    return intervalId;
  };

  /**
   * Auto-update scan status on scan detail page
   */
  window.autoUpdateScanStatus = function(scanId, options = {}) {
    const {
      statusElement = null,
      badgeElement = null,
      progressElement = null,
      findingsCountElement = null,
      onStatusChange = null,
      usePolling = false
    } = options;

    const updateUI = function(data) {
      // Update status badge
      if (badgeElement) {
        const status = data.status || 'unknown';
        let badgeClass = 'badge-neutral';
        let badgeText = status;
        let badgeIcon = '';

        switch (status) {
          case 'queued':
            badgeClass = 'badge-warning';
            badgeText = 'Queued';
            badgeIcon = '⏱';
            break;
          case 'running':
            badgeClass = 'badge-info';
            badgeText = 'Running';
            badgeIcon = '⟳';
            break;
          case 'completed':
            badgeClass = data.passed ? 'badge-success' : 'badge-error';
            badgeText = data.passed ? 'PASS' : 'FAIL';
            badgeIcon = data.passed ? '✓' : '✕';
            break;
          case 'failed':
            badgeClass = 'badge-error';
            badgeText = 'Failed';
            badgeIcon = '✕';
            break;
        }

        badgeElement.className = `badge ${badgeClass}`;
        badgeElement.innerHTML = `<span aria-hidden="true">${badgeIcon}</span> ${badgeText}`;
        badgeElement.setAttribute('title', `Status: ${status}`);
      }

      // Update status text
      if (statusElement) {
        statusElement.textContent = data.status || 'unknown';
      }

      // Update findings count
      if (findingsCountElement && data.total_findings !== undefined) {
        findingsCountElement.textContent = data.total_findings;
      }

      // Update progress
      if (progressElement) {
        if (data.status === 'running') {
          progressElement.style.display = 'block';
          // Show indeterminate progress
          progressElement.classList.add('progress-bar-indeterminate');
        } else {
          progressElement.style.display = 'none';
          progressElement.classList.remove('progress-bar-indeterminate');
        }
      }

      // Announce status changes to screen readers
      if (typeof announceToScreenReader !== 'undefined') {
        const statusMessages = {
          'queued': 'Scan queued',
          'running': 'Scan is now running',
          'completed': data.passed ? 'Scan completed successfully' : 'Scan completed with failures',
          'failed': 'Scan failed'
        };
        const message = statusMessages[data.status] || `Scan status: ${data.status}`;
        announceToScreenReader(message, data.status === 'failed' ? 'assertive' : 'polite');
      }

      // Call custom callback
      if (onStatusChange) {
        onStatusChange(data);
      }
    };

    // Use SSE if available, otherwise fall back to polling
    if (typeof EventSource !== 'undefined' && !usePolling) {
      return connectScanStatusStream(scanId, {
        onUpdate: updateUI,
        onComplete: function(data) {
          updateUI(data);
          if (typeof showToast !== 'undefined') {
            showToast('Scan completed', data.passed ? 'success' : 'error');
          }
          // Reload page after a short delay to show final results
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        },
        onError: function(error) {
          console.error('SSE error, falling back to polling:', error);
          // Fall back to polling
          pollScanStatus(scanId, {
            onUpdate: updateUI,
            onComplete: function(data) {
              updateUI(data);
              if (typeof showToast !== 'undefined') {
                showToast('Scan completed', data.passed ? 'success' : 'error');
              }
            }
          });
        }
      });
    } else {
      // Use polling
      return pollScanStatus(scanId, {
        onUpdate: updateUI,
        onComplete: function(data) {
          updateUI(data);
          if (typeof showToast !== 'undefined') {
            showToast('Scan completed', data.passed ? 'success' : 'error');
          }
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        }
      });
    }
  };

  // Clean up connections on page unload
  window.addEventListener('beforeunload', function() {
    activeConnections.forEach((eventSource) => {
      eventSource.close();
    });
    activeConnections.clear();
  });

})();

