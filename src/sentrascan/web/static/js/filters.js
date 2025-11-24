/**
 * SentraScan Platform - Filters and Sorting JavaScript
 * Handles table sorting, filtering, and pagination
 */

(function() {
  'use strict';

  // ============================================
  // Table Sorting
  // ============================================

  const sortableHeaders = document.querySelectorAll('.table th.sortable');
  
  sortableHeaders.forEach(header => {
    header.addEventListener('click', function() {
      const sortField = this.getAttribute('data-sort');
      const currentSort = this.getAttribute('data-current-sort') || 'none';
      
      // Determine new sort direction
      let newSort = 'asc';
      if (currentSort === 'asc') {
        newSort = 'desc';
      } else if (currentSort === 'desc') {
        newSort = 'asc';
      }
      
      // Update URL with sort parameters
      const url = new URL(window.location);
      url.searchParams.set('sort', sortField);
      url.searchParams.set('order', newSort);
      
      // Remove page parameter when sorting
      url.searchParams.delete('page');
      
      window.location.href = url.toString();
    });
  });

  // Set current sort state from URL
  const urlParams = new URLSearchParams(window.location.search);
  const currentSort = urlParams.get('sort');
  const currentOrder = urlParams.get('order');
  
  if (currentSort) {
    const header = document.querySelector(`th[data-sort="${currentSort}"]`);
    if (header) {
      header.setAttribute('data-current-sort', currentOrder || 'asc');
      header.classList.add(currentOrder === 'desc' ? 'desc' : 'asc');
    }
  }

})();

