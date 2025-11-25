/**
 * Unit tests for charts.js
 * Tests for Chart.js integration and chart rendering
 */

describe('charts.js', function() {
  let originalChart;

  beforeEach(function() {
    // Mock Chart.js
    originalChart = window.Chart;
    window.Chart = jasmine.createSpy('Chart').and.returnValue({
      destroy: jasmine.createSpy('destroy'),
      update: jasmine.createSpy('update')
    });
    
    // Mock console methods
    spyOn(console, 'error');
    
    // Setup DOM
    document.body.innerHTML = '';
  });

  afterEach(function() {
    // Restore Chart
    window.Chart = originalChart;
    
    // Clean up
    document.body.innerHTML = '';
  });

  describe('createScanTrendsChart', function() {
    beforeEach(function() {
      const canvas = document.createElement('canvas');
      canvas.id = 'scan-trends-chart';
      document.body.appendChild(canvas);
    });

    it('should create a line chart with correct data', function() {
      const data = {
        labels: ['Jan', 'Feb', 'Mar'],
        scans: [10, 15, 12],
        passed: [8, 12, 10],
        failed: [2, 3, 2]
      };
      
      const chart = createScanTrendsChart('scan-trends-chart', data);
      
      expect(window.Chart).toHaveBeenCalled();
      expect(chart).toBeTruthy();
    });

    it('should handle missing canvas element', function() {
      const chart = createScanTrendsChart('non-existent-canvas', {});
      
      expect(console.error).toHaveBeenCalled();
      expect(chart).toBeNull();
    });

    it('should use default data when not provided', function() {
      const chart = createScanTrendsChart('scan-trends-chart', {});
      
      expect(window.Chart).toHaveBeenCalled();
    });
  });

  describe('createSeverityChart', function() {
    beforeEach(function() {
      const canvas = document.createElement('canvas');
      canvas.id = 'severity-chart';
      document.body.appendChild(canvas);
    });

    it('should create a donut chart with severity data', function() {
      const data = {
        critical: 5,
        high: 10,
        medium: 15,
        low: 20
      };
      
      const chart = createSeverityChart('severity-chart', data);
      
      expect(window.Chart).toHaveBeenCalled();
      expect(chart).toBeTruthy();
    });

    it('should handle zero values', function() {
      const data = {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
      };
      
      const chart = createSeverityChart('severity-chart', data);
      
      expect(window.Chart).toHaveBeenCalled();
    });
  });

  describe('createPassFailChart', function() {
    beforeEach(function() {
      const canvas = document.createElement('canvas');
      canvas.id = 'pass-fail-chart';
      document.body.appendChild(canvas);
    });

    it('should create a bar chart with pass/fail data', function() {
      const data = {
        passed: 25,
        failed: 5
      };
      
      const chart = createPassFailChart('pass-fail-chart', data);
      
      expect(window.Chart).toHaveBeenCalled();
      expect(chart).toBeTruthy();
    });

    it('should handle zero values', function() {
      const data = {
        passed: 0,
        failed: 0
      };
      
      const chart = createPassFailChart('pass-fail-chart', data);
      
      expect(window.Chart).toHaveBeenCalled();
    });
  });

  describe('Chart accessibility', function() {
    beforeEach(function() {
      const canvas = document.createElement('canvas');
      canvas.id = 'test-chart';
      canvas.setAttribute('role', 'img');
      canvas.setAttribute('aria-label', 'Test chart');
      document.body.appendChild(canvas);
    });

    it('should preserve ARIA attributes on canvas', function() {
      const canvas = document.getElementById('test-chart');
      expect(canvas.getAttribute('role')).toBe('img');
      expect(canvas.getAttribute('aria-label')).toBe('Test chart');
    });
  });
});

