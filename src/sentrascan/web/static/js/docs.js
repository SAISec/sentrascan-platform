/**
 * Documentation Viewer
 * Handles markdown rendering, navigation, search, and table of contents
 */

(function() {
  'use strict';

  // Configuration
  const DOCS_BASE_PATH = '/api/v1/docs';
  const DOCS_PAGES = {
    'getting-started': 'getting-started/README.md',
    'user-guide': 'user-guide/README.md',
    'api': 'api/README.md',
    'how-to': 'how-to/README.md',
    'troubleshooting': 'troubleshooting/README.md',
    'faq': 'faq/README.md',
    'best-practices': 'best-practices/README.md',
    'glossary': 'glossary/README.md'
  };

  // State
  let currentPage = null;
  let searchIndex = null;
  let searchTimeout = null;

  // DOM Elements
  const sidebar = document.getElementById('docs-sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const navList = document.getElementById('docs-nav-list');
  const tocList = document.getElementById('docs-toc-list');
  const content = document.getElementById('docs-content');
  const loading = document.getElementById('docs-loading');
  const error = document.getElementById('docs-error');
  const searchInput = document.getElementById('docs-search-input');
  const searchClear = document.getElementById('search-clear');
  const searchResults = document.getElementById('search-results');
  const searchResultsContent = document.getElementById('search-results-content');
  const searchResultsClose = document.getElementById('search-results-close');
  const breadcrumbCurrent = document.getElementById('breadcrumb-current');
  const printButton = document.getElementById('print-docs');

  // Initialize
  function init() {
    // Get page from URL
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page') || 'getting-started';
    
    // Load page
    loadPage(page);
    
    // Setup event listeners
    setupEventListeners();
    
    // Build search index
    buildSearchIndex();
  }

  // Setup event listeners
  function setupEventListeners() {
    // Navigation links
    navList.addEventListener('click', (e) => {
      if (e.target.tagName === 'A') {
        e.preventDefault();
        const page = e.target.getAttribute('data-page');
        loadPage(page);
        updateURL(page);
      }
    });

    // Sidebar toggle (mobile)
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', () => {
        const isExpanded = sidebar.getAttribute('aria-expanded') === 'true';
        sidebar.setAttribute('aria-expanded', !isExpanded);
      });
    }

    // Search
    searchInput.addEventListener('input', handleSearch);
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        performSearch(searchInput.value);
      }
    });
    
    if (searchClear) {
      searchClear.addEventListener('click', () => {
        searchInput.value = '';
        searchClear.style.display = 'none';
        searchResults.setAttribute('aria-hidden', 'true');
      });
    }

    // Search results close
    if (searchResultsClose) {
      searchResultsClose.addEventListener('click', () => {
        searchResults.setAttribute('aria-hidden', 'true');
      });
    }

    // Print
    if (printButton) {
      printButton.addEventListener('click', () => {
        window.print();
      });
    }

    // Scroll to anchor
    window.addEventListener('hashchange', scrollToAnchor);
    
    // Update active TOC item on scroll
    window.addEventListener('scroll', updateActiveTOCItem, { passive: true });
  }

  // Load documentation page
  async function loadPage(page) {
    if (!DOCS_PAGES[page]) {
      showError('Page not found');
      return;
    }

    currentPage = page;
    showLoading();
    updateActiveNav(page);
    updateBreadcrumb(page);

    try {
      const url = `${DOCS_BASE_PATH}/raw/${DOCS_PAGES[page]}`;
      console.log('Loading documentation from:', url);
      const response = await fetch(url);
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Failed to load documentation:', response.status, errorText);
        throw new Error(`Failed to load: ${response.status} ${response.statusText}`);
      }
      
      const markdown = await response.text();
      console.log('Markdown loaded, length:', markdown.length);
      if (!markdown || markdown.trim().length === 0) {
        throw new Error('Documentation file is empty');
      }
      
      renderMarkdown(markdown);
      generateTOC();
      scrollToAnchor();
    } catch (err) {
      console.error('Error loading page:', err);
      showError(err.message);
    }
  }

  // Render markdown
  function renderMarkdown(markdown) {
    // Check if marked is available
    if (typeof marked === 'undefined') {
      console.error('marked library not loaded');
      showError('Markdown renderer not available. Please refresh the page.');
      return;
    }

    // Configure marked
    marked.setOptions({
      breaks: true,
      gfm: true,
      headerIds: true,
      mangle: false
    });

    // Render
    try {
      const html = marked.parse(markdown);
      content.innerHTML = html;
      showContent(); // Show content and hide loading
      
      // Highlight code blocks
      if (window.Prism) {
        Prism.highlightAllUnder(content);
      }

      // Add anchor links to headings
      addAnchorLinks();

      // Fix relative links
      fixLinks();
    } catch (err) {
      console.error('Error rendering markdown:', err);
      showError('Error rendering documentation: ' + err.message);
    }
  }

  // Add anchor links to headings
  function addAnchorLinks() {
    const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
    headings.forEach(heading => {
      if (!heading.id) {
        heading.id = heading.textContent
          .toLowerCase()
          .replace(/[^\w\s-]/g, '')
          .replace(/\s+/g, '-')
          .replace(/-+/g, '-');
      }
      
      const anchor = document.createElement('a');
      anchor.href = `#${heading.id}`;
      anchor.className = 'heading-anchor';
      anchor.setAttribute('aria-label', 'Link to this section');
      anchor.innerHTML = '<span class="icon icon-link" aria-hidden="true"></span>';
      anchor.style.cssText = 'opacity: 0; margin-left: 0.5em; text-decoration: none; transition: opacity 0.2s;';
      
      heading.style.cssText += 'display: flex; align-items: center;';
      heading.appendChild(anchor);
      
      heading.addEventListener('mouseenter', () => {
        anchor.style.opacity = '1';
      });
      
      heading.addEventListener('mouseleave', () => {
        anchor.style.opacity = '0';
      });
    });
  }

  // Fix relative links
  function fixLinks() {
    const links = content.querySelectorAll('a[href^="../"]');
    links.forEach(link => {
      const href = link.getAttribute('href');
      // Convert relative paths to absolute paths
      if (href.startsWith('../')) {
        const parts = href.split('/');
        const targetPage = parts[parts.length - 2]; // e.g., 'user-guide' from '../user-guide/README.md'
        if (DOCS_PAGES[targetPage]) {
          link.href = `/docs?page=${targetPage}`;
          link.addEventListener('click', (e) => {
            e.preventDefault();
            loadPage(targetPage);
            updateURL(targetPage);
          });
        }
      }
    });
  }

  // Generate table of contents
  function generateTOC() {
    tocList.innerHTML = '';
    const headings = content.querySelectorAll('h2, h3, h4');
    
    if (headings.length === 0) {
      return;
    }

    headings.forEach(heading => {
      const level = parseInt(heading.tagName.charAt(1));
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `#${heading.id}`;
      a.textContent = heading.textContent.replace(/\s*#\s*$/, ''); // Remove anchor icon
      a.className = `toc-level-${level}`;
      
      a.addEventListener('click', (e) => {
        e.preventDefault();
        scrollToElement(heading);
      });
      
      li.appendChild(a);
      tocList.appendChild(li);
    });
  }

  // Update active navigation item
  function updateActiveNav(page) {
    navList.querySelectorAll('a').forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('data-page') === page) {
        link.classList.add('active');
      }
    });
  }

  // Update breadcrumb
  function updateBreadcrumb(page) {
    const pageNames = {
      'getting-started': 'Getting Started',
      'user-guide': 'User Guide',
      'api': 'API Documentation',
      'how-to': 'How-To Guides',
      'troubleshooting': 'Troubleshooting',
      'faq': 'FAQ',
      'best-practices': 'Best Practices',
      'glossary': 'Glossary'
    };
    
    breadcrumbCurrent.textContent = pageNames[page] || page;
  }

  // Update URL
  function updateURL(page) {
    const url = new URL(window.location);
    url.searchParams.set('page', page);
    window.history.pushState({ page }, '', url);
  }

  // Scroll to anchor
  function scrollToAnchor() {
    if (window.location.hash) {
      const element = document.querySelector(window.location.hash);
      if (element) {
        setTimeout(() => scrollToElement(element), 100);
      }
    }
  }

  // Scroll to element
  function scrollToElement(element) {
    const offset = 100; // Account for sticky header
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;
    
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  }

  // Update active TOC item on scroll
  function updateActiveTOCItem() {
    const headings = content.querySelectorAll('h2, h3, h4');
    const scrollPosition = window.scrollY + 150; // Offset for sticky header
    
    let activeHeading = null;
    headings.forEach(heading => {
      const headingTop = heading.getBoundingClientRect().top + window.scrollY;
      if (headingTop <= scrollPosition) {
        activeHeading = heading;
      }
    });
    
    tocList.querySelectorAll('a').forEach(link => {
      link.classList.remove('active');
      if (activeHeading && link.getAttribute('href') === `#${activeHeading.id}`) {
        link.classList.add('active');
      }
    });
  }

  // Build search index
  async function buildSearchIndex() {
    try {
      const index = [];
      for (const [pageKey, pagePath] of Object.entries(DOCS_PAGES)) {
        try {
          const response = await fetch(`${DOCS_BASE_PATH}/raw/${pagePath}`);
          if (response.ok) {
            const markdown = await response.text();
            const text = markdown.replace(/[#*`]/g, '').replace(/\n+/g, ' ');
            const words = text.toLowerCase().split(/\s+/).filter(w => w.length > 2);
            
            index.push({
              page: pageKey,
              path: pagePath,
              title: getPageTitle(pageKey),
              text: text,
              words: words
            });
          }
        } catch (err) {
          console.warn(`Failed to index ${pageKey}:`, err);
        }
      }
      searchIndex = index;
    } catch (err) {
      console.error('Error building search index:', err);
    }
  }

  // Get page title
  function getPageTitle(pageKey) {
    const titles = {
      'getting-started': 'Getting Started',
      'user-guide': 'User Guide',
      'api': 'API Documentation',
      'how-to': 'How-To Guides',
      'troubleshooting': 'Troubleshooting',
      'faq': 'FAQ',
      'best-practices': 'Best Practices',
      'glossary': 'Glossary'
    };
    return titles[pageKey] || pageKey;
  }

  // Handle search input
  function handleSearch(e) {
    const query = e.target.value.trim();
    
    if (searchClear) {
      searchClear.style.display = query ? 'block' : 'none';
    }
    
    // Debounce search
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      if (query.length >= 2) {
        performSearch(query);
      } else {
        searchResults.setAttribute('aria-hidden', 'true');
      }
    }, 300);
  }

  // Perform search
  function performSearch(query) {
    if (!searchIndex || query.length < 2) {
      return;
    }

    const queryWords = query.toLowerCase().split(/\s+/);
    const results = [];

    searchIndex.forEach(item => {
      let score = 0;
      const matches = [];
      
      queryWords.forEach(word => {
        const wordMatches = item.text.toLowerCase().match(new RegExp(word, 'gi'));
        if (wordMatches) {
          score += wordMatches.length;
          matches.push(...wordMatches);
        }
      });
      
      if (score > 0) {
        results.push({
          page: item.page,
          title: item.title,
          score: score,
          matches: matches
        });
      }
    });

    // Sort by score
    results.sort((a, b) => b.score - a.score);

    // Display results
    displaySearchResults(results, query);
  }

  // Display search results
  function displaySearchResults(results, query) {
    if (results.length === 0) {
      searchResultsContent.innerHTML = '<p>No results found.</p>';
    } else {
      const html = results.map(result => {
        return `
          <div class="search-result-item" data-page="${result.page}">
            <h3>${highlightText(result.title, query)}</h3>
            <p>Found in ${result.page}</p>
          </div>
        `;
      }).join('');
      
      searchResultsContent.innerHTML = html;
      
      // Add click handlers
      searchResultsContent.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
          const page = item.getAttribute('data-page');
          loadPage(page);
          updateURL(page);
          searchResults.setAttribute('aria-hidden', 'true');
          searchInput.value = '';
          if (searchClear) {
            searchClear.style.display = 'none';
          }
        });
      });
    }
    
    searchResults.setAttribute('aria-hidden', 'false');
  }

  // Highlight text
  function highlightText(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<span class="search-highlight">$1</span>');
  }

  // Show loading
  function showLoading() {
    loading.style.display = 'block';
    error.style.display = 'none';
    content.style.display = 'none';
  }

  // Show error
  function showError(message) {
    loading.style.display = 'none';
    error.style.display = 'block';
    error.textContent = `Error: ${message}`;
    content.style.display = 'none';
  }

  // Show content
  function showContent() {
    loading.style.display = 'none';
    error.style.display = 'none';
    content.style.display = 'block';
  }

  // Handle browser back/forward
  window.addEventListener('popstate', (e) => {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page') || 'getting-started';
    loadPage(page);
  });

  // Wait for required libraries to load (Safari compatibility)
  function waitForLibraries(callback, maxAttempts = 50) {
    let attempts = 0;
    const checkLibraries = () => {
      attempts++;
      // Check if marked is available (required for docs)
      if (typeof marked !== 'undefined') {
        callback();
      } else if (attempts < maxAttempts) {
        // Wait 100ms and try again
        setTimeout(checkLibraries, 100);
      } else {
        console.error('Timeout waiting for marked library to load');
        // Try to initialize anyway - might work if library loads later
        callback();
      }
    };
    checkLibraries();
  }

  // Initialize when DOM is ready and libraries are loaded
  function initializeWhenReady() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        waitForLibraries(init);
      });
    } else {
      waitForLibraries(init);
    }
  }

  initializeWhenReady();
})();

