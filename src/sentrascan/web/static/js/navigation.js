/**
 * SentraScan Platform - Navigation JavaScript
 * Handles mobile navigation menu, user menu dropdown, and keyboard navigation
 */

(function() {
  'use strict';

  // ============================================
  // Mobile Navigation
  // ============================================

  const mobileToggle = document.querySelector('.nav-mobile-toggle');
  const mobileDrawer = document.querySelector('.nav-mobile-drawer');
  const mobileOverlay = document.querySelector('.nav-mobile-overlay');
  const mobileClose = document.querySelector('.nav-mobile-close');

  // Store reference to focus trap handler for cleanup
  let focusTrapHandler = null;
  let previousActiveElement = null;

  /**
   * Get all focusable elements within a container
   */
  function getFocusableElements(container) {
    if (!container) return [];
    
    const focusableSelectors = [
      'a[href]',
      'button:not([disabled])',
      'textarea:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      '[tabindex]:not([tabindex="-1"])'
    ].join(', ');

    return Array.from(container.querySelectorAll(focusableSelectors))
      .filter(el => {
        // Filter out hidden elements
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               !el.hasAttribute('disabled');
      });
  }

  /**
   * Create focus trap for mobile menu
   */
  function createFocusTrap() {
    if (!mobileDrawer) return;

    const focusableElements = getFocusableElements(mobileDrawer);
    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    return function handleTabKey(e) {
      if (e.key !== 'Tab') return;

      // If only one focusable element, prevent tabbing
      if (focusableElements.length === 1) {
        e.preventDefault();
        firstElement.focus();
        return;
      }

      // If Shift+Tab on first element, move to last
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
        return;
      }

      // If Tab on last element, move to first
      if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
        return;
      }
    };
  }

  /**
   * Remove focus trap
   */
  function removeFocusTrap() {
    if (focusTrapHandler) {
      document.removeEventListener('keydown', focusTrapHandler);
      focusTrapHandler = null;
    }
  }

  /**
   * Open mobile navigation drawer
   */
  function openMobileMenu() {
    if (!mobileDrawer || !mobileOverlay) return;

    // Store the previously focused element
    previousActiveElement = document.activeElement;

    // Show drawer and overlay
    mobileDrawer.style.display = 'block';
    mobileOverlay.style.display = 'block';
    
    // Trigger animation
    requestAnimationFrame(() => {
      mobileDrawer.classList.add('open');
      mobileOverlay.classList.add('show');
    });

    // Update ARIA attributes
    if (mobileToggle) {
      mobileToggle.setAttribute('aria-expanded', 'true');
    }

    // Prevent body scroll
    document.body.style.overflow = 'hidden';

    // Create and activate focus trap
    focusTrapHandler = createFocusTrap();
    if (focusTrapHandler) {
      document.addEventListener('keydown', focusTrapHandler);
    }

    // Focus on close button for accessibility
    if (mobileClose) {
      // Small delay to ensure drawer is visible
      setTimeout(() => {
        mobileClose.focus();
      }, 100);
    }
  }

  /**
   * Close mobile navigation drawer
   */
  function closeMobileMenu() {
    if (!mobileDrawer || !mobileOverlay) return;

    // Remove focus trap
    removeFocusTrap();

    // Remove animation classes
    mobileDrawer.classList.remove('open');
    mobileOverlay.classList.remove('show');

    // Hide after animation completes
    setTimeout(() => {
      mobileDrawer.style.display = 'none';
      mobileOverlay.style.display = 'none';
    }, 300); // Match transition duration

    // Update ARIA attributes
    if (mobileToggle) {
      mobileToggle.setAttribute('aria-expanded', 'false');
    }

    // Restore body scroll
    document.body.style.overflow = '';

    // Return focus to the element that opened the menu
    if (previousActiveElement && previousActiveElement.focus) {
      previousActiveElement.focus();
      previousActiveElement = null;
    } else if (mobileToggle) {
      mobileToggle.focus();
    }
  }

  // Event listeners for mobile menu
  if (mobileToggle) {
    mobileToggle.addEventListener('click', (e) => {
      e.preventDefault();
      openMobileMenu();
    });

    // Keyboard support for toggle button
    mobileToggle.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openMobileMenu();
      }
    });
  }

  if (mobileClose) {
    mobileClose.addEventListener('click', (e) => {
      e.preventDefault();
      closeMobileMenu();
    });

    // Keyboard support for close button
    mobileClose.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        closeMobileMenu();
      }
    });
  }

  if (mobileOverlay) {
    mobileOverlay.addEventListener('click', () => {
      closeMobileMenu();
    });
  }

  // Close mobile menu when clicking on a link
  if (mobileDrawer) {
    const mobileLinks = mobileDrawer.querySelectorAll('a');
    mobileLinks.forEach(link => {
      link.addEventListener('click', () => {
        closeMobileMenu();
      });
    });
  }

  // ============================================
  // User Menu Dropdown (Desktop)
  // ============================================

  const userMenuToggle = document.querySelector('.user-menu-toggle');
  const userMenuDropdown = document.querySelector('.user-menu-dropdown');

  /**
   * Toggle user menu dropdown
   */
  function toggleUserMenu() {
    if (!userMenuDropdown || !userMenuToggle) return;

    const isOpen = userMenuDropdown.style.display === 'block';
    
    if (isOpen) {
      closeUserMenu();
    } else {
      openUserMenu();
    }
  }

  /**
   * Open user menu dropdown
   */
  function openUserMenu() {
    if (!userMenuDropdown || !userMenuToggle) return;

    userMenuDropdown.style.display = 'block';
    userMenuToggle.setAttribute('aria-expanded', 'true');

    // Close on outside click
    setTimeout(() => {
      document.addEventListener('click', handleOutsideClick);
    }, 0);
  }

  /**
   * Close user menu dropdown
   */
  function closeUserMenu() {
    if (!userMenuDropdown || !userMenuToggle) return;

    userMenuDropdown.style.display = 'none';
    userMenuToggle.setAttribute('aria-expanded', 'false');

    // Remove outside click listener
    document.removeEventListener('click', handleOutsideClick);
  }

  /**
   * Handle clicks outside user menu
   */
  function handleOutsideClick(e) {
    if (!userMenuDropdown || !userMenuToggle) return;

    const isClickInside = userMenuDropdown.contains(e.target) || 
                          userMenuToggle.contains(e.target);

    if (!isClickInside) {
      closeUserMenu();
    }
  }

  // Event listeners for user menu
  if (userMenuToggle) {
    userMenuToggle.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      toggleUserMenu();
    });

    // Keyboard support
    userMenuToggle.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleUserMenu();
      } else if (e.key === 'Escape') {
        closeUserMenu();
      }
    });
  }

  // Close user menu when clicking on a link
  if (userMenuDropdown) {
    const userMenuLinks = userMenuDropdown.querySelectorAll('a');
    userMenuLinks.forEach(link => {
      link.addEventListener('click', () => {
        closeUserMenu();
      });
    });
  }

  // ============================================
  // Keyboard Navigation
  // ============================================

  /**
   * Handle ESC key to close menus
   */
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      // Close mobile menu if open
      if (mobileDrawer && mobileDrawer.classList.contains('open')) {
        closeMobileMenu();
      }
      
      // Close user menu if open
      if (userMenuDropdown && userMenuDropdown.style.display === 'block') {
        closeUserMenu();
      }
    }
  });

  // ============================================
  // Active Navigation Link Highlighting
  // ============================================

  /**
   * Set active navigation link based on current URL
   */
  function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (!href) return;
      
      // Remove existing active class
      link.classList.remove('nav-link-active');

      // Normalize paths (remove trailing slashes for comparison)
      const normalizedHref = href.replace(/\/$/, '') || '/';
      const normalizedPath = currentPath.replace(/\/$/, '') || '/';

      // Exact match
      if (normalizedHref === normalizedPath) {
        link.classList.add('nav-link-active');
        return;
      }

      // For non-root paths, check if current path starts with the href
      // This handles cases like /baselines/compare matching /baselines
      if (normalizedHref !== '/' && normalizedPath.startsWith(normalizedHref + '/')) {
        link.classList.add('nav-link-active');
        return;
      }

      // Special case: /ui/scan should match /ui/scan (exact or with query params)
      if (normalizedHref === '/ui/scan' && normalizedPath.startsWith('/ui/scan')) {
        link.classList.add('nav-link-active');
        return;
      }
    });
  }

  // Set active link on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setActiveNavLink);
  } else {
    setActiveNavLink();
  }

  // Update active links when navigating (for SPA-like behavior if implemented)
  window.addEventListener('popstate', setActiveNavLink);

  // ============================================
  // Responsive Behavior
  // ============================================

  /**
   * Handle window resize to close mobile menu on desktop
   */
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      // Close mobile menu if window is resized to desktop size
      if (window.innerWidth >= 768 && mobileDrawer && mobileDrawer.classList.contains('open')) {
        closeMobileMenu();
      }
    }, 250);
  });

})();

