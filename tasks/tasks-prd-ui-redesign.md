# Task List: SentraScan Platform UI Redesign

Based on PRD: `prd-ui-redesign.md`

## Relevant Files

### Templates (Jinja2)
- `src/sentrascan/web/templates/base.html` - Base template with navigation, header, footer (enhanced)
- `src/sentrascan/web/templates/dashboard.html` - New dashboard page with statistics and charts
- `src/sentrascan/web/templates/index.html` - Enhanced scan list page with filtering and sorting
- `src/sentrascan/web/templates/scan_detail.html` - Enhanced scan detail page with expandable findings
- `src/sentrascan/web/templates/scan_forms.html` - Enhanced scan trigger forms with validation
- `src/sentrascan/web/templates/baselines.html` - Enhanced baselines list page
- `src/sentrascan/web/templates/baseline_compare.html` - Enhanced baseline comparison with visual diff
- `src/sentrascan/web/templates/login.html` - Enhanced login page
- `src/sentrascan/web/templates/scan_submitted.html` - Success/confirmation page (may be merged)
- `src/sentrascan/web/templates/components/_scan_card.html` - Reusable scan card component
- `src/sentrascan/web/templates/components/_finding_row.html` - Reusable finding row component
- `src/sentrascan/web/templates/components/_stat_card.html` - Reusable statistics card component
- `src/sentrascan/web/templates/components/_modal.html` - Reusable modal/dialog component
- `src/sentrascan/web/templates/components/_toast.html` - Toast notification component
- `src/sentrascan/web/templates/errors/404.html` - 404 error page
- `src/sentrascan/web/templates/errors/500.html` - 500 error page

### Static Files (CSS/JS)
- `src/sentrascan/web/static/css/main.css` - Main stylesheet with design system variables
- `src/sentrascan/web/static/css/components.css` - Component-specific styles
- `src/sentrascan/web/static/css/responsive.css` - Responsive design breakpoints
- `src/sentrascan/web/static/js/main.js` - Main JavaScript file with core functionality
- `src/sentrascan/web/static/js/charts.js` - Chart rendering and data visualization
- `src/sentrascan/web/static/js/realtime.js` - Real-time updates (WebSocket/SSE)
- `src/sentrascan/web/static/js/utils.js` - Utility functions (copy-to-clipboard, formatters, etc.)
- `src/sentrascan/web/static/js/filters.js` - Filtering and search functionality
- `src/sentrascan/web/static/js/modals.js` - Modal/dialog management
- `src/sentrascan/web/static/js/toasts.js` - Toast notification system
- `src/sentrascan/web/static/js/navigation.js` - Mobile navigation and menu handling
- `src/sentrascan/web/static/js/accessibility.js` - Accessibility enhancements (keyboard nav, ARIA)

### Backend Files
- `src/sentrascan/server.py` - FastAPI server (add static file serving, new endpoints for dashboard stats, real-time updates)
- `src/sentrascan/core/models.py` - Database models (may need minor additions)

### Configuration Files
- `pyproject.toml` - Add frontend dependencies if needed (e.g., Tailwind CSS, Chart.js)
- `package.json` - If using npm for frontend tooling (optional)

### Test Files
- `tests/test_ui_dashboard.py` - Tests for dashboard page rendering and functionality
- `tests/test_ui_scan_list.py` - Tests for scan list page filtering, sorting, pagination
- `tests/test_ui_scan_detail.py` - Tests for scan detail page and findings display
- `tests/test_ui_forms.py` - Tests for scan form validation and submission
- `tests/test_ui_baselines.py` - Tests for baselines page and comparison
- `tests/test_ui_accessibility.py` - Accessibility tests (keyboard nav, ARIA, screen reader)
- `tests/test_ui_responsive.py` - Responsive design tests
- `tests/test_ui_realtime.py` - Real-time update functionality tests
- `tests/test_ui_export.py` - Export functionality tests
- `tests/test_ui_integration.py` - End-to-end UI integration tests
- `tests/test_ui_performance.py` - Performance tests for Core Web Vitals (FCP, LCP, TTI, CLS)
- `tests/test_ui_errors_empty.py` - Tests for error handling (404, 500, API errors) and empty states
- `tests/test_ui_aria.py` - Tests for ARIA attributes implementation and accessibility compliance
- `tests/test_ui_form_validation.py` - Tests for form validation and error message display
- `tests/test_ui_modal_focus_esc.py` - Tests for modal focus trap and ESC key functionality
- `tests/test_ui_mobile_navigation.py` - Tests for mobile navigation (hamburger menu, drawer, touch targets)
- `tests/test_ui_progressive_enhancement.py` - Tests for progressive enhancement (functionality without JavaScript)
- `tests/test_ui_toast_stacking.py` - Tests for toast notification stacking and auto-dismiss functionality
- `tests/test_ui_chart_accessibility.py` - Tests for chart accessibility (keyboard navigation, ARIA labels)
- `tests/README.md` - Comprehensive test documentation
- `tests/TEST_COVERAGE_REPORT.md` - Test coverage report and metrics

### Notes

- Static files should be organized in `src/sentrascan/web/static/` directory
- FastAPI needs to be configured to serve static files using `StaticFiles`
- Consider using Tailwind CSS via CDN or build process
- Chart.js can be included via CDN or npm
- All JavaScript should be modular and follow ES6+ standards
- Test files should use pytest and may include Playwright/Selenium for E2E tests

## Tasks

- [x] 1.0 Design System & Foundation Setup
  - [x] 1.1 Create static files directory structure (`src/sentrascan/web/static/css/`, `js/`, `images/`)
  - [x] 1.2 Set up CSS design system with CSS variables for colors, typography, spacing (8px base unit)
  - [x] 1.3 Define color palette in CSS variables (primary, severity colors, neutrals, semantic colors)
  - [x] 1.4 Create typography system (headings, body, monospace) with responsive font sizes
  - [x] 1.5 Create base component styles (buttons, inputs, cards, tables, badges) with all states (default, hover, active, disabled, focus)
  - [x] 1.6 Implement spacing system using consistent scale (4px, 8px, 16px, 24px, 32px, 48px, 48px, 64px)
  - [x] 1.7 Create icon system (SVG icons or icon font) for common actions and status indicators
  - [x] 1.8 Set up responsive breakpoints in CSS (mobile: <768px, tablet: 768px-1023px, desktop: 1024px+)
  - [x] 1.9 Create utility classes for common patterns (if not using Tailwind)
  - [x] 1.10 Configure FastAPI to serve static files from `src/sentrascan/web/static/`

- [x] 2.0 Core Pages Redesign (Dashboard, Login, Navigation)
  - [x] 2.1 Enhance `base.html` with semantic HTML structure (header, nav, main, footer)
  - [x] 2.2 Implement responsive navigation header with logo, main nav links, and user menu
  - [x] 2.3 Create mobile hamburger menu with slide-out drawer and overlay
  - [x] 2.4 Add keyboard navigation support for mobile menu (ESC to close, focus trap)
  - [x] 2.5 Implement breadcrumb navigation component for detail pages
  - [x] 2.6 Add active page highlighting in navigation
  - [x] 2.7 Create footer component with version info (optional)
  - [x] 2.8 Redesign `login.html` with centered form, proper labels, show/hide password toggle
  - [x] 2.9 Add form validation and error display to login page
  - [x] 2.10 Implement accessibility features for login (ARIA labels, keyboard navigation, focus management)
  - [x] 2.11 Create new `dashboard.html` template with statistics cards layout
  - [x] 2.12 Implement statistics cards component (total scans, pass rate, findings count, severity breakdown)
  - [x] 2.13 Add dashboard filtering controls (scan type, time range, status)
  - [x] 2.14 Create recent activity feed section showing last 10 scans
  - [x] 2.15 Add quick action buttons for triggering new scans
  - [x] 2.16 Implement dashboard auto-refresh functionality (every 30 seconds)
  - [x] 2.17 Add export functionality for dashboard data (CSV, JSON)
  - [x] 2.18 Create backend endpoint for dashboard statistics (`/api/v1/dashboard/stats`)

- [x] 3.0 Scan Pages Enhancement (List, Detail, Forms)
  - [x] 3.1 Enhance `index.html` (scan list) with modern table design and hover effects
  - [x] 3.2 Implement sortable table columns (Time, Type, Target, Status, Severity counts)
  - [x] 3.3 Add status badges with icons (completed, queued, running, failed)
  - [x] 3.4 Implement tooltip component for truncated target paths
  - [x] 3.5 Create advanced filtering UI (scan type, status, date range, severity threshold, search)
  - [x] 3.6 Implement pagination component with page size selector, prev/next, page numbers, total count
  - [x] 3.7 Add clickable table rows that navigate to scan details
  - [x] 3.8 Enhance `scan_detail.html` with comprehensive header section (ID, timestamp, type, status, target path)
  - [x] 3.9 Add copy-to-clipboard button for scan ID and target path
  - [x] 3.10 Create severity summary section with cards or bars
  - [x] 3.11 Add action buttons (Download JSON Report, Download SBOM, Compare with Baseline)
  - [x] 3.12 Implement findings table with expandable rows for full details
  - [x] 3.13 Create findings grouping by severity with collapsible sections
  - [x] 3.14 Add "Expand/Collapse All" functionality for findings groups
  - [x] 3.15 Implement findings filtering (severity, category, scanner, search)
  - [x] 3.16 Add findings sorting (severity, category, scanner, title)
  - [x] 3.17 Create finding detail view with formatted description, location, evidence, remediation
  - [x] 3.18 Add copy-to-clipboard for individual finding data
  - [x] 3.19 Implement bulk selection for findings (optional)
  - [x] 3.20 Enhance `scan_forms.html` with tabbed interface for Model vs MCP scans
  - [x] 3.21 Add form sections with visual separation and inline help text
  - [x] 3.22 Implement form field validation with clear error messages
  - [x] 3.23 Add form field states (required indicators, validation errors, disabled states)
  - [x] 3.24 Create collapsible "Advanced" sections for optional fields
  - [x] 3.25 Implement loading states during form submission
  - [x] 3.26 Add redirect to scan detail page after successful submission

- [x] 4.0 Baselines & Comparison Features
  - [x] 4.1 Enhance `baselines.html` with modern table design
  - [x] 4.2 Implement sortable columns (Time, Type, Name, Hash, Active status)
  - [x] 4.3 Add action buttons (View, Compare, Delete if applicable)
  - [x] 4.4 Create "Create Baseline" button on scan detail page
  - [x] 4.5 Implement baseline creation modal/form with name and description fields
  - [x] 4.6 Add confirmation dialog before baseline creation
  - [x] 4.7 Enhance `baseline_compare.html` with side-by-side layout
  - [x] 4.8 Implement visual diff highlighting (added: green, removed: red, changed: yellow)
  - [x] 4.9 Create synchronized scrolling for side-by-side comparison
  - [x] 4.10 Add collapsible sections for unchanged content
  - [x] 4.11 Implement path-based navigation (click to jump to specific diff)
  - [x] 4.12 Create expandable tree view for nested JSON structures
  - [x] 4.13 Add JSON syntax highlighting
  - [x] 4.14 Implement line numbers for JSON content
  - [x] 4.15 Add copy-to-clipboard for JSON sections
  - [x] 4.16 Create search/filter functionality within diff results
  - [x] 4.17 Add export functionality for baseline comparison (JSON, formatted text)

- [x] 5.0 Interactive Features & Accessibility (Real-time, Charts, Notifications, A11y)
  - [x] 5.1 Create modal/dialog component with focus trap and ESC key support
  - [x] 5.2 Implement confirmation dialogs for destructive actions
  - [x] 5.3 Create dropdown menu component with keyboard navigation
  - [x] 5.4 Implement tabs/accordion component for scan type selection and grouped findings
  - [x] 5.5 Create tooltip component for hover tooltips and help text
  - [x] 5.6 Set up real-time update system (WebSocket or Server-Sent Events)
  - [x] 5.7 Create backend endpoint for real-time scan status updates (`/api/v1/scans/{scan_id}/status` or WebSocket)
  - [x] 5.8 Implement client-side connection to real-time update endpoint
  - [x] 5.9 Add auto-update functionality for scan status (queued → running → completed)
  - [x] 5.10 Create progress indicator for running scans
  - [x] 5.11 Implement toast notification system with success, error, and info types
  - [x] 5.12 Add dismissible toasts with close button and auto-dismiss (5 seconds)
  - [x] 5.13 Create toast stacking for multiple notifications
  - [x] 5.14 Implement loading states (skeleton screens, spinners, progress bars)
  - [x] 5.15 Add disabled states during async operations
  - [x] 5.16 Set up Chart.js or similar library for data visualization
  - [x] 5.17 Create line chart for scan trends over time
  - [x] 5.18 Create pie/donut chart for severity distribution
  - [x] 5.19 Create bar chart for pass/fail ratios
  - [x] 5.20 Add chart interactions (hover tooltips, click to filter)
  - [x] 5.21 Implement ARIA labels and keyboard navigation for charts
  - [x] 5.22 Add global search functionality in header (optional)
  - [x] 5.23 Implement advanced filtering with multi-select, date pickers, filter chips
  - [x] 5.24 Add "Clear all filters" button with active filter indicators
  - [x] 5.25 Ensure all interactive elements are keyboard accessible
  - [x] 5.26 Implement logical tab order throughout the application
  - [x] 5.27 Add skip links for main content
  - [x] 5.28 Ensure all focusable elements have visible focus indicators
  - [x] 5.29 Add semantic HTML elements (header, nav, main, footer, article, section) where appropriate
  - [x] 5.30 Implement ARIA labels for all interactive elements
  - [x] 5.31 Add ARIA live regions for dynamic content updates
  - [x] 5.32 Ensure all images and icons have alt text
  - [x] 5.33 Associate all form labels with inputs using proper HTML attributes
  - [x] 5.34 Add ARIA-describedby for error messages
  - [x] 5.35 Implement fieldset and legend for grouped form inputs
  - [x] 5.36 Ensure all tables have proper headers (th) with scope attributes
  - [x] 5.37 Add table captions or titles for context
  - [x] 5.38 Implement responsive table handling with horizontal scroll on mobile
  - [x] 5.39 Verify color contrast ratios meet WCAG AA standards (4.5:1 for normal text, 3:1 for large text)
  - [x] 5.40 Ensure color is not the only indicator (add icons, text, patterns)
  - [x] 5.41 Implement touch-friendly targets (minimum 44x44px) with adequate spacing
  - [x] 5.42 Add export functionality for scan list (CSV)
  - [x] 5.43 Add export functionality for findings (CSV)
  - [x] 5.44 Create print-friendly views for reports
  - [x] 5.45 Implement error pages (404, 500) with user-friendly messages
  - [x] 5.46 Add empty states for scan list, findings, search results, charts
  - [x] 5.47 Optimize page load times (lazy loading, code splitting, minification)
  - [x] 5.48 Implement efficient data loading (pagination, debounced search, cached responses)

- [ ] 6.0 Testing & Quality Assurance
  - [x] 6.1 Write unit tests for utility functions (`utils.js`) - copy-to-clipboard, formatters, etc.
  - [x] 6.2 Write unit tests for filter functionality (`filters.js`)
  - [x] 6.3 Write unit tests for modal management (`modals.js`)
  - [x] 6.4 Write unit tests for toast notification system (`toasts.js`)
  - [x] 6.5 Write unit tests for real-time update handling (`realtime.js`)
  - [x] 6.6 Write unit tests for chart rendering (`charts.js`)
  - [x] 6.7 Create integration tests for dashboard page rendering and statistics display
  - [x] 6.8 Create integration tests for scan list page (filtering, sorting, pagination)
  - [x] 6.9 Create integration tests for scan detail page (findings display, expand/collapse)
  - [x] 6.10 Create integration tests for scan forms (validation, submission)
  - [x] 6.11 Create integration tests for baselines page and comparison functionality
  - [x] 6.12 Create accessibility tests using automated tools (axe DevTools, WAVE, Lighthouse)
  - [x] 6.13 Perform manual keyboard navigation testing (tab order, focus management, keyboard shortcuts)
  - [x] 6.14 Perform manual screen reader testing (NVDA, JAWS, VoiceOver)
  - [x] 6.15 Test color contrast ratios using contrast checker tools
  - [x] 6.16 Create responsive design tests (mobile, tablet, desktop breakpoints)
  - [x] 6.17 Test real-time update functionality (WebSocket/SSE connection, status updates)
  - [x] 6.18 Test export functionality (CSV, JSON exports)
  - [x] 6.19 Create end-to-end tests for critical user flows (login, trigger scan, view results)
  - [x] 6.20 Test cross-browser compatibility (Chrome, Firefox, Safari, Edge - last 2 versions)
  - [x] 6.21 Perform performance testing (FCP < 1.5s, LCP < 2.5s, TTI < 3.5s, CLS < 0.1)
  - [x] 6.22 Test error handling and empty states
  - [x] 6.23 Verify all ARIA attributes are correctly implemented
  - [x] 6.24 Test form validation and error messages
  - [x] 6.25 Test modal focus trap and ESC key functionality
  - [x] 6.26 Test mobile navigation (hamburger menu, drawer, touch targets)
  - [x] 6.27 Verify all interactive elements work without JavaScript (progressive enhancement)
  - [x] 6.28 Test toast notification stacking and auto-dismiss
  - [x] 6.29 Test chart accessibility (keyboard navigation, ARIA labels)
  - [x] 6.30 Create test documentation and test coverage report
