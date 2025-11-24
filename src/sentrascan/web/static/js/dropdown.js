/**
 * SentraScan Platform - Dropdown Menu Component
 * Reusable dropdown with keyboard navigation and accessibility
 */

(function() {
  'use strict';

  /**
   * Initialize all dropdowns on the page
   */
  function initDropdowns() {
    document.querySelectorAll('[data-dropdown]').forEach(trigger => {
      const dropdownId = trigger.getAttribute('data-dropdown');
      const dropdown = document.getElementById(dropdownId);
      
      if (!dropdown) {
        console.warn(`Dropdown with ID "${dropdownId}" not found`);
        return;
      }

      setupDropdown(trigger, dropdown);
    });
  }

  /**
   * Set up a dropdown
   */
  function setupDropdown(trigger, dropdown) {
    let isOpen = false;
    let focusableItems = [];

    // Set ARIA attributes
    trigger.setAttribute('aria-haspopup', 'true');
    trigger.setAttribute('aria-expanded', 'false');
    dropdown.setAttribute('role', 'menu');
    dropdown.setAttribute('aria-hidden', 'true');

    // Get menu items
    const getMenuItems = () => {
      return Array.from(dropdown.querySelectorAll('a, button, [role="menuitem"]'));
    };

    // Open dropdown
    const open = () => {
      isOpen = true;
      dropdown.style.display = 'block';
      trigger.setAttribute('aria-expanded', 'true');
      dropdown.setAttribute('aria-hidden', 'false');
      
      focusableItems = getMenuItems();
      
      // Focus first item
      if (focusableItems.length > 0) {
        setTimeout(() => {
          focusableItems[0].focus();
        }, 50);
      }

      // Close on outside click
      const clickHandler = (e) => {
        if (!dropdown.contains(e.target) && !trigger.contains(e.target)) {
          close();
        }
      };
      setTimeout(() => {
        document.addEventListener('click', clickHandler);
        dropdown._clickHandler = clickHandler;
      }, 0);

      // Close on ESC
      const escHandler = (e) => {
        if (e.key === 'Escape') {
          close();
          trigger.focus();
        }
      };
      document.addEventListener('keydown', escHandler);
      dropdown._escHandler = escHandler;
    };

    // Close dropdown
    const close = () => {
      isOpen = false;
      dropdown.style.display = 'none';
      trigger.setAttribute('aria-expanded', 'false');
      dropdown.setAttribute('aria-hidden', 'true');
      
      // Remove event handlers
      if (dropdown._clickHandler) {
        document.removeEventListener('click', dropdown._clickHandler);
        delete dropdown._clickHandler;
      }
      if (dropdown._escHandler) {
        document.removeEventListener('keydown', dropdown._escHandler);
        delete dropdown._escHandler;
      }
    };

    // Toggle dropdown
    const toggle = () => {
      if (isOpen) {
        close();
      } else {
        open();
      }
    };

    // Keyboard navigation
    const handleKeyDown = (e) => {
      if (!isOpen) {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
          e.preventDefault();
          open();
        }
        return;
      }

      const items = getMenuItems();
      if (items.length === 0) return;

      const currentIndex = items.indexOf(document.activeElement);

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          const nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
          items[nextIndex].focus();
          break;
        case 'ArrowUp':
          e.preventDefault();
          const prevIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
          items[prevIndex].focus();
          break;
        case 'Home':
          e.preventDefault();
          items[0].focus();
          break;
        case 'End':
          e.preventDefault();
          items[items.length - 1].focus();
          break;
        case 'Escape':
          e.preventDefault();
          close();
          trigger.focus();
          break;
      }
    };

    // Set up event listeners
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggle();
    });

    trigger.addEventListener('keydown', handleKeyDown);

    // Close when clicking menu items
    dropdown.addEventListener('click', (e) => {
      if (e.target.closest('a, button, [role="menuitem"]')) {
        close();
      }
    });

    // Keyboard navigation within dropdown
    dropdown.addEventListener('keydown', handleKeyDown);
  }

  // Initialize on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDropdowns);
  } else {
    initDropdowns();
  }

  // Re-initialize when new content is added
  const observer = new MutationObserver(() => {
    initDropdowns();
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

})();

