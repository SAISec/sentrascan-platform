/**
 * SentraScan Platform - Tabs Component
 * Reusable tabs with keyboard navigation and accessibility
 */

(function() {
  'use strict';

  /**
   * Initialize all tab components
   */
  function initTabs() {
    document.querySelectorAll('[role="tablist"]').forEach(tablist => {
      setupTabs(tablist);
    });
  }

  /**
   * Set up a tab component
   */
  function setupTabs(tablist) {
    const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
    const panels = tabs.map(tab => {
      const panelId = tab.getAttribute('aria-controls');
      return document.getElementById(panelId);
    }).filter(Boolean);

    if (tabs.length === 0 || panels.length === 0) return;

    // Get current active tab
    const getActiveTab = () => {
      return tabs.find(tab => tab.getAttribute('aria-selected') === 'true');
    };

    // Switch to a specific tab
    const switchToTab = (index) => {
      if (index < 0 || index >= tabs.length) return;

      const tab = tabs[index];
      const panelId = tab.getAttribute('aria-controls');
      const panel = document.getElementById(panelId);

      // Update tabs
      tabs.forEach(t => {
        t.setAttribute('aria-selected', 'false');
        t.classList.remove('active');
        t.style.borderBottomColor = 'transparent';
        t.style.color = 'var(--color-text-secondary)';
      });

      tab.setAttribute('aria-selected', 'true');
      tab.classList.add('active');
      tab.style.borderBottomColor = 'var(--color-primary)';
      tab.style.color = 'var(--color-primary)';

      // Update panels
      panels.forEach(p => {
        p.style.display = 'none';
        p.classList.remove('active');
      });

      if (panel) {
        panel.style.display = 'block';
        panel.classList.add('active');
      }

      // Focus the tab
      tab.focus();
    };

    // Keyboard navigation
    const handleKeyDown = (e) => {
      const currentIndex = tabs.indexOf(getActiveTab());

      switch (e.key) {
        case 'ArrowLeft':
          e.preventDefault();
          const prevIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
          switchToTab(prevIndex);
          break;
        case 'ArrowRight':
          e.preventDefault();
          const nextIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
          switchToTab(nextIndex);
          break;
        case 'Home':
          e.preventDefault();
          switchToTab(0);
          break;
        case 'End':
          e.preventDefault();
          switchToTab(tabs.length - 1);
          break;
      }
    };

    // Set up click handlers
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => {
        switchToTab(index);
      });

      tab.addEventListener('keydown', handleKeyDown);
    });
  }

  // Initialize on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTabs);
  } else {
    initTabs();
  }

  // Re-initialize when new content is added
  const observer = new MutationObserver(() => {
    initTabs();
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Export global function for manual tab switching (for backward compatibility)
  window.switchTab = function(tabName) {
    const tab = document.querySelector(`[role="tab"][aria-controls="${tabName}-tab-panel"]`);
    if (tab) {
      const tablist = tab.closest('[role="tablist"]');
      if (tablist) {
        const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));
        const index = tabs.indexOf(tab);
        if (index >= 0) {
          tab.click();
        }
      }
    }
  };

})();

