/**
 * SentraScan Platform - Charts Component
 * Chart.js integration for data visualization with accessibility
 */

(function() {
  'use strict';

  // Chart.js configuration
  const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 12,
            family: 'var(--font-family-sans)'
          }
        }
      },
      tooltip: {
        enabled: true,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 12
        },
        cornerRadius: 4
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          font: {
            size: 11
          }
        }
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          font: {
            size: 11
          }
        }
      }
    }
  };

  /**
   * Create a line chart for scan trends over time
   * @param {string} canvasId - Canvas element ID
   * @param {Array} data - Chart data
   * @param {Object} options - Chart options
   * @returns {Chart} - Chart.js instance
   */
  window.createScanTrendsChart = function(canvasId, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas with ID "${canvasId}" not found`);
      return null;
    }

    const ctx = canvas.getContext('2d');
    
    const chartData = {
      labels: data.labels || [],
      datasets: [
        {
          label: 'Total Scans',
          data: data.scans || [],
          borderColor: 'var(--color-primary)',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Passed',
          data: data.passed || [],
          borderColor: 'var(--color-success)',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Failed',
          data: data.failed || [],
          borderColor: 'var(--color-error)',
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    };

    const config = {
      type: 'line',
      data: chartData,
      options: {
        ...chartDefaults.options,
        ...options,
        interaction: {
          intersect: false,
          mode: 'index'
        },
        onHover: (event, activeElements) => {
          canvas.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
        },
        onClick: (event, activeElements) => {
          if (activeElements.length > 0 && options.onClick) {
            const element = activeElements[0];
            options.onClick(element);
          }
        }
      },
      plugins: [{
        id: 'accessibility',
        afterDraw: (chart) => {
          // Add ARIA label
          canvas.setAttribute('role', 'img');
          canvas.setAttribute('aria-label', `Line chart showing scan trends over time. ${data.labels?.length || 0} data points.`);
        }
      }]
    };

    return new Chart(ctx, config);
  };

  /**
   * Create a pie/donut chart for severity distribution
   * @param {string} canvasId - Canvas element ID
   * @param {Object} data - Severity data
   * @param {Object} options - Chart options
   * @returns {Chart} - Chart.js instance
   */
  window.createSeverityChart = function(canvasId, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas with ID "${canvasId}" not found`);
      return null;
    }

    const ctx = canvas.getContext('2d');
    const isDonut = options.type === 'doughnut' || options.type === 'donut';
    
    const chartData = {
      labels: ['Critical', 'High', 'Medium', 'Low'],
      datasets: [{
        data: [
          data.critical || 0,
          data.high || 0,
          data.medium || 0,
          data.low || 0
        ],
        backgroundColor: [
          'var(--color-severity-critical)',
          'var(--color-severity-high)',
          'var(--color-severity-medium)',
          'var(--color-severity-low)'
        ],
        borderWidth: 2,
        borderColor: '#fff'
      }]
    };

    const config = {
      type: isDonut ? 'doughnut' : 'pie',
      data: chartData,
      options: {
        ...chartDefaults.options,
        ...options,
        cutout: isDonut ? '60%' : 0,
        onClick: (event, activeElements) => {
          if (activeElements.length > 0 && options.onClick) {
            const element = activeElements[0];
            const index = element.index;
            const label = chartData.labels[index];
            options.onClick({ index, label, value: chartData.datasets[0].data[index] });
          }
        }
      },
      plugins: [{
        id: 'accessibility',
        afterDraw: (chart) => {
          const total = chartData.datasets[0].data.reduce((a, b) => a + b, 0);
          canvas.setAttribute('role', 'img');
          canvas.setAttribute('aria-label', `${isDonut ? 'Donut' : 'Pie'} chart showing severity distribution. Total: ${total} findings. Critical: ${data.critical || 0}, High: ${data.high || 0}, Medium: ${data.medium || 0}, Low: ${data.low || 0}.`);
        }
      }]
    };

    return new Chart(ctx, config);
  };

  /**
   * Create a bar chart for pass/fail ratios
   * @param {string} canvasId - Canvas element ID
   * @param {Object} data - Pass/fail data
   * @param {Object} options - Chart options
   * @returns {Chart} - Chart.js instance
   */
  window.createPassFailChart = function(canvasId, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas with ID "${canvasId}" not found`);
      return null;
    }

    const ctx = canvas.getContext('2d');
    
    const chartData = {
      labels: data.labels || ['Passed', 'Failed'],
      datasets: [{
        label: 'Scans',
        data: [data.passed || 0, data.failed || 0],
        backgroundColor: [
          'var(--color-success)',
          'var(--color-error)'
        ],
        borderWidth: 0,
        borderRadius: 4
      }]
    };

    const config = {
      type: 'bar',
      data: chartData,
      options: {
        ...chartDefaults.options,
        ...options,
        scales: {
          ...chartDefaults.scales,
          y: {
            ...chartDefaults.scales.y,
            beginAtZero: true
          }
        },
        onClick: (event, activeElements) => {
          if (activeElements.length > 0 && options.onClick) {
            const element = activeElements[0];
            const index = element.index;
            const label = chartData.labels[index];
            options.onClick({ index, label, value: chartData.datasets[0].data[index] });
          }
        }
      },
      plugins: [{
        id: 'accessibility',
        afterDraw: (chart) => {
          canvas.setAttribute('role', 'img');
          canvas.setAttribute('aria-label', `Bar chart showing pass/fail ratios. Passed: ${data.passed || 0}, Failed: ${data.failed || 0}.`);
        }
      }]
    };

    return new Chart(ctx, config);
  };

  /**
   * Initialize all charts on the page
   */
  function initCharts() {
    // Charts will be initialized by individual pages
    // This function can be called to reinitialize after dynamic content loads
  }

  // Export initialization function
  window.initCharts = initCharts;

})();

