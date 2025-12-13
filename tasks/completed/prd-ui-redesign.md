# Product Requirements Document: SentraScan Platform UI Redesign

## Introduction/Overview

The SentraScan Platform currently uses a basic HTML/CSS interface that lacks modern design patterns, accessibility features, and user experience enhancements. This PRD outlines a complete UI redesign to transform the platform into a modern, accessible, and user-friendly security scanning dashboard that serves both security engineers and developers.

**Problem Statement:** The current UI is functional but lacks:
- Modern visual design and visual hierarchy
- Responsive design for mobile/tablet devices
- Interactive components and real-time feedback
- Data visualization and statistics
- Accessibility compliance (WCAG)
- Enhanced user experience features

**Goal:** Redesign the entire UI to provide a modern, minimal, accessible interface that improves usability for both technical security professionals and developers while maintaining all existing functionality.

---

## Goals

1. **Visual Design:** Implement a modern, minimal design system with clean lines, ample whitespace, and clear visual hierarchy
2. **Responsive Design:** Ensure full functionality across desktop, tablet, and mobile devices
3. **Accessibility:** Achieve WCAG 2.1 AA compliance for all users
4. **User Experience:** Add interactive components, real-time updates, and intuitive navigation
5. **Data Visualization:** Provide dashboard statistics, charts, and visual representations of scan data
6. **Performance:** Maintain fast page loads and smooth interactions
7. **Compatibility:** Support both security engineers (data-focused) and developers (action-oriented) workflows

---

## User Stories

1. **As a security engineer**, I want to see a dashboard with overall statistics and trends so that I can quickly assess the security posture of scanned assets.

2. **As a developer**, I want to quickly trigger scans and see immediate feedback so that I can integrate security checks into my workflow.

3. **As a user**, I want to view scan details with expandable findings grouped by severity so that I can focus on critical issues first.

4. **As a user**, I want to filter and search findings by multiple criteria so that I can find specific issues quickly.

5. **As a user**, I want to see real-time status updates for running scans so that I know when results are available.

6. **As a user**, I want to compare baselines side-by-side with visual highlighting so that I can easily identify changes.

7. **As a user with accessibility needs**, I want to navigate and use all features with keyboard-only input and screen readers so that I can work effectively.

8. **As a mobile user**, I want to access all features on my device so that I can review scans while away from my desk.

9. **As a user**, I want to receive notifications when scans complete so that I don't need to constantly refresh the page.

10. **As a user**, I want to export scan data and reports in various formats so that I can share findings with my team.

---

## Functional Requirements

### FR-1: Design System & Visual Foundation

1. The system must implement a modern, minimal design with:
   - Clean typography hierarchy (headings, body, captions)
   - Consistent spacing system (4px or 8px base unit)
   - Subtle color palette with high contrast ratios (WCAG AA minimum)
   - Consistent border radius and shadow system
   - Icon system for common actions and status indicators

2. The system must use a color scheme that:
   - Uses semantic colors for severity levels (Critical: #9C27B0/purple, High: #F44336/red, Medium: #FF9800/orange, Low: #4CAF50/green)
   - Provides sufficient contrast for text (minimum 4.5:1 for normal text, 3:1 for large text)
   - Supports both light and dark mode (optional but recommended)

3. The system must implement consistent component styling:
   - Buttons with clear states (default, hover, active, disabled)
   - Form inputs with labels, placeholders, and error states
   - Cards/containers with subtle borders or shadows
   - Tables with hover states and clear column headers
   - Badges and status indicators with consistent sizing

### FR-2: Responsive Design

4. The system must be fully responsive with:
   - Desktop layout (1024px+): Full multi-column layouts, sidebars, expanded tables
   - Tablet layout (768px-1023px): Adjusted column layouts, collapsible sidebars
   - Mobile layout (<768px): Single column, stacked elements, mobile-friendly navigation

5. The system must implement responsive navigation:
   - Desktop: Horizontal navigation bar
   - Mobile: Hamburger menu with slide-out drawer
   - All navigation must be keyboard accessible

6. The system must ensure all interactive elements are touch-friendly:
   - Minimum touch target size of 44x44px
   - Adequate spacing between clickable elements
   - Swipe gestures for mobile tables (optional)

### FR-3: Dashboard Page (Home)

7. The system must display a dashboard with:
   - Statistics cards showing:
     - Total scans count
     - Overall pass rate percentage
     - Total findings count
     - Breakdown by severity (Critical, High, Medium, Low)
   - Recent activity feed showing last 10 scans with key information
   - Quick action buttons to trigger new scans (Model or MCP)
   - Charts/graphs showing:
     - Scan trends over time (line chart)
     - Severity distribution (pie or donut chart)
     - Pass/fail ratio (bar chart)

8. The system must allow filtering dashboard data by:
   - Scan type (Model, MCP, All)
   - Time range (Last 7 days, 30 days, 90 days, All time)
   - Status (Passed, Failed, All)

9. The system must auto-refresh dashboard statistics every 30 seconds when on the dashboard page.

10. The system must provide export functionality for dashboard data (CSV, JSON).

### FR-4: Scan List Page (Enhanced Index)

11. The system must display scans in an enhanced table with:
   - Sortable columns (Time, Type, Target, Status, Severity counts)
   - Row hover effects for better visibility
   - Clickable rows that navigate to scan details
   - Status badges with icons
   - Truncated target paths with tooltips showing full path

12. The system must provide advanced filtering:
   - Filter by scan type (Model, MCP, All)
   - Filter by status (Passed, Failed, All)
   - Filter by date range (date picker)
   - Filter by severity threshold (show only scans with Critical/High findings)
   - Search by target path (text input)

13. The system must implement pagination with:
   - Page size selector (10, 20, 50, 100 items per page)
   - Previous/Next buttons
   - Page number indicators
   - Total count display

14. The system must show scan status indicators:
   - Completed scans: Green checkmark or red X
   - Queued scans: Yellow clock icon
   - Running scans: Animated spinner
   - Failed scans: Error icon

### FR-5: Scan Detail Page

15. The system must display comprehensive scan information:
   - Header section with:
     - Scan ID and timestamp
     - Scan type badge
     - Overall status (Pass/Fail) with large visual indicator
     - Target path with copy-to-clipboard button
     - Duration and scan metadata
   - Summary section with severity counts displayed as cards or bars
   - Action buttons: Download JSON Report, Download SBOM (if available), Compare with Baseline

16. The system must display findings in an enhanced table with:
   - Expandable rows showing full details (description, location, evidence, remediation)
   - Grouping by severity (collapsible sections)
   - Filtering by:
     - Severity (Critical, High, Medium, Low)
     - Category
     - Scanner
     - Search by title/description
   - Sorting by severity, category, scanner, or title
   - Bulk actions (select multiple findings)

17. The system must show finding details in expandable sections:
   - Title and severity badge
   - Category and scanner information
   - Full description with formatted text
   - Location information (if available)
   - Evidence (formatted JSON or structured display)
   - Remediation steps (if available)
   - Copy-to-clipboard for individual finding data

18. The system must provide visual grouping:
   - Group findings by severity with collapsible headers
   - Show count badges on group headers
   - Allow expanding/collapsing all groups at once

19. The system must implement finding actions:
   - Mark as reviewed (if user tracking is added)
   - Export individual finding
   - Link to similar findings (if applicable)

### FR-6: Scan Forms (Run Scan Page)

20. The system must provide enhanced scan trigger forms:
   - Tabbed interface or accordion for Model vs MCP scans
   - Clear form sections with visual separation
   - Inline help text and tooltips for form fields
   - Validation with clear error messages
   - Success/error toast notifications after submission

21. The system must show form field states:
   - Required fields clearly marked
   - Validation errors displayed inline
   - Disabled states for fields when dependencies aren't met
   - Loading states during form submission

22. The system must provide scan options:
   - Model Scan: Model path, Strict mode, Generate SBOM, Policy path, Async option
   - MCP Scan: Auto-discover toggle, Config paths (textarea), Policy path, Async option
   - Advanced options in collapsible sections

23. The system must redirect to scan detail page after successful submission with a success message.

### FR-7: Baselines Page

24. The system must display baselines in an enhanced table:
   - Sortable columns (Time, Type, Name, Hash, Active status)
   - Active status toggle (if user has admin role)
   - Actions: View, Compare, Delete (if applicable)

25. The system must provide baseline comparison interface:
   - Side-by-side layout showing two baselines
   - Visual diff highlighting:
     - Added items: Green background
     - Removed items: Red background
     - Changed items: Yellow/orange background
   - Collapsible sections for unchanged content
   - Path-based navigation (click to jump to specific diff)
   - Export diff report

26. The system must allow creating baselines from scan results:
   - Button on scan detail page: "Create Baseline"
   - Modal or form with baseline name and description
   - Confirmation before creation

### FR-8: Baseline Comparison Page

27. The system must display baseline comparison with:
   - Header showing both baseline IDs, names, and creation dates
   - Side-by-side diff view with synchronized scrolling
   - Visual indicators for:
     - Added paths (green highlight)
     - Removed paths (red highlight)
     - Changed values (yellow highlight with before/after)
   - Expandable tree view for nested JSON structures
   - Search/filter within diff results
   - Export comparison report

28. The system must format JSON content:
   - Syntax highlighting for JSON
   - Collapsible nested objects/arrays
   - Line numbers for reference
   - Copy-to-clipboard for sections

### FR-9: Login Page

29. The system must provide an enhanced login experience:
   - Clean, centered login form
   - Clear error messages for invalid credentials
   - Password field with show/hide toggle (for API key visibility)
   - "Remember me" option (if session management supports it)
   - Accessibility: Proper labels, ARIA attributes, keyboard navigation

30. The system must handle authentication states:
   - Redirect to dashboard after successful login
   - Show user information in header (if available)
   - Logout button in navigation

### FR-10: Navigation & Layout

31. The system must implement a consistent navigation structure:
   - Header with:
     - Logo/brand name
     - Main navigation links (Dashboard, Scans, Baselines, Run Scan)
     - User menu (Login/Logout, Settings if applicable)
   - Breadcrumbs on detail pages
   - Footer with version info and links (optional)

32. The system must provide navigation states:
   - Active page highlighting
   - Disabled states for unauthorized pages
   - Loading indicators during navigation

### FR-11: Interactive Components

33. The system must implement modals/dialogs for:
   - Confirmation dialogs (delete, create baseline, etc.)
   - Form submissions with loading states
   - Error messages
   - Information tooltips

34. The system must implement dropdown menus:
   - Filter dropdowns
   - Action menus (three-dot menus)
   - User menu
   - All dropdowns must be keyboard accessible

35. The system must implement tabs/accordions:
   - Scan type selection (Model/MCP)
   - Grouped findings by severity
   - Settings sections

36. The system must implement tooltips:
   - Hover tooltips for truncated text
   - Help tooltips for form fields
   - Status explanations

### FR-12: Real-Time Updates & Notifications

37. The system must provide real-time scan status updates:
   - WebSocket or Server-Sent Events (SSE) connection
   - Auto-update scan status from "queued" to "running" to "completed"
   - Update scan detail page when scan completes
   - Show progress indicator for running scans (if available)

38. The system must implement toast notifications:
   - Success notifications (scan submitted, baseline created)
   - Error notifications (scan failed, validation errors)
   - Info notifications (scan completed, updates available)
   - Dismissible with close button
   - Auto-dismiss after 5 seconds (configurable)
   - Stack multiple notifications

39. The system must provide loading states:
   - Skeleton screens for data loading
   - Spinner indicators for async operations
   - Progress bars for long-running operations
   - Disabled states during operations

### FR-13: Search & Filtering

40. The system must provide global search (optional):
   - Search bar in header
   - Search across scans, findings, baselines
   - Search results page with categorized results

41. The system must implement advanced filtering:
   - Multi-select filters
   - Date range pickers
   - Clear all filters button
   - Active filter indicators (chips/badges)
   - Save filter presets (optional)

### FR-14: Data Visualization

42. The system must display charts and graphs:
   - Line charts for trends over time
   - Pie/donut charts for severity distribution
   - Bar charts for pass/fail ratios
   - Stacked bar charts for findings by category
   - All charts must be accessible (ARIA labels, keyboard navigation)

43. The system must provide chart interactions:
   - Hover tooltips with detailed data
   - Click to filter by selected data point
   - Zoom/pan for time-series data (optional)
   - Export charts as images (optional)

### FR-15: Accessibility (WCAG 2.1 AA Compliance)

44. The system must ensure keyboard navigation:
   - All interactive elements accessible via keyboard
   - Logical tab order
   - Skip links for main content
   - Focus indicators on all focusable elements
   - Keyboard shortcuts for common actions (optional)

45. The system must provide screen reader support:
   - Semantic HTML elements (header, nav, main, footer, article, section)
   - ARIA labels for all interactive elements
   - ARIA live regions for dynamic content updates
   - Alt text for all images and icons
   - Form labels associated with inputs

46. The system must ensure color contrast:
   - Minimum 4.5:1 contrast ratio for normal text
   - Minimum 3:1 contrast ratio for large text (18pt+)
   - Color is not the only indicator (use icons, text, patterns)

47. The system must provide accessible forms:
   - Labels for all form inputs
   - Error messages associated with inputs (ARIA-describedby)
   - Required fields clearly indicated
   - Fieldset and legend for grouped inputs

48. The system must ensure accessible tables:
   - Table headers (th elements)
   - Scope attributes for header cells
   - Caption or title for table context
   - Responsive table handling (horizontal scroll on mobile with proper labeling)

49. The system must provide accessible modals:
   - Focus trap within modal
   - Focus return to trigger after close
   - ESC key to close
   - ARIA modal attributes

### FR-16: Performance & Optimization

50. The system must optimize page load times:
   - Lazy loading for images and below-fold content
   - Code splitting for JavaScript (if using a framework)
   - Minified CSS and JavaScript
   - Efficient database queries (pagination, indexing)

51. The system must implement efficient data loading:
   - Pagination for large datasets
   - Virtual scrolling for very long lists (optional)
   - Debounced search inputs
   - Cached API responses where appropriate

### FR-17: Error Handling & User Feedback

52. The system must display user-friendly error messages:
   - Clear, actionable error messages
   - Inline validation errors
   - Global error boundary (if using React/Vue)
   - 404 page for not found resources
   - 500 page for server errors

53. The system must handle empty states:
   - Empty scan list with "Run your first scan" CTA
   - Empty findings list with success message
   - Empty search results with suggestions
   - No data messages for charts

### FR-18: Export & Reporting

54. The system must provide export functionality:
   - Export scan list as CSV
   - Export scan detail as JSON
   - Export findings as CSV
   - Export baseline comparison as JSON or formatted text
   - Print-friendly views for reports

---

## Non-Goals (Out of Scope)

1. **Backend API Changes:** This redesign focuses on the UI layer only. Backend API endpoints should remain compatible, though new endpoints may be added for real-time updates.

2. **User Management:** Advanced user management features (user roles beyond existing admin/viewer, user profiles, etc.) are out of scope unless they're minimal additions.

3. **Advanced Analytics:** Complex analytics features like custom dashboards, saved queries, or advanced reporting are out of scope for this initial redesign.

4. **Mobile App:** Native mobile applications (iOS/Android) are out of scope. Focus is on responsive web design.

5. **Offline Support:** Progressive Web App (PWA) features and offline functionality are out of scope.

6. **Internationalization (i18n):** Multi-language support is out of scope for this redesign.

7. **Custom Themes:** User-customizable themes beyond light/dark mode are out of scope.

8. **Real-time Collaboration:** Features like shared workspaces or collaborative editing are out of scope.

9. **Advanced Workflows:** Workflow automation, scheduled scans, or CI/CD integrations are out of scope.

10. **Video Tutorials or Onboarding:** Interactive tutorials or guided tours are out of scope (though tooltips and help text are included).

---

## Design Considerations

### Design System

- **Color Palette:**
  - Primary: Use a professional blue or teal (#2196F3 or #009688)
  - Severity Colors: Critical (#9C27B0), High (#F44336), Medium (#FF9800), Low (#4CAF50)
  - Neutral Grays: For backgrounds, borders, text (#F5F5F5, #E0E0E0, #757575, #212121)
  - Success: #4CAF50
  - Error: #F44336
  - Warning: #FF9800
  - Info: #2196F3

- **Typography:**
  - Headings: Sans-serif, bold (e.g., Inter, Roboto, or system font stack)
  - Body: Sans-serif, regular weight
  - Monospace: For code, IDs, paths (e.g., 'Courier New', monospace)
  - Font sizes: Responsive scale (16px base, 1.25rem, 1.5rem, 2rem for headings)

- **Spacing:**
  - Base unit: 8px
  - Consistent spacing scale: 4px, 8px, 16px, 24px, 32px, 48px, 64px

- **Components:**
  - Buttons: Rounded corners (4-8px), padding 12px 24px, clear hover/active states
  - Cards: Subtle shadow or border, padding 16-24px, rounded corners
  - Inputs: Border, padding 8-12px, focus ring, error states
  - Tables: Striped rows (optional), hover effects, clear borders

### UI Framework Recommendation

Since no preference was specified, recommend using:
- **Tailwind CSS** for utility-first styling (flexible, modern, good performance)
- **Vanilla JavaScript** or **Alpine.js** for interactivity (lightweight, no heavy framework)
- **Chart.js** or **D3.js** for data visualization
- **HTMX** (optional) for enhanced interactivity without heavy JavaScript

Alternative: If a full framework is preferred:
- **Vue.js** or **React** with component libraries (Vuetify, Material-UI)
- However, this would require more significant refactoring

### Layout Structure

```
┌─────────────────────────────────────────┐
│ Header (Logo, Nav, User Menu)          │
├─────────────────────────────────────────┤
│                                         │
│  Main Content Area                      │
│  (Breadcrumbs, Page Content)           │
│                                         │
│                                         │
└─────────────────────────────────────────┘
│ Footer (Optional)                       │
└─────────────────────────────────────────┘
```

### Mobile Navigation

- Hamburger menu icon in header
- Slide-out drawer from left
- Overlay background when drawer is open
- Close button and ESC key support

---

## Technical Considerations

### Technology Stack

1. **Frontend:**
   - HTML5, CSS3 (or Tailwind CSS)
   - JavaScript (ES6+) or Alpine.js for interactivity
   - Chart.js or similar for data visualization
   - WebSocket client or EventSource for real-time updates

2. **Backend Integration:**
   - Maintain existing FastAPI endpoints
   - Add WebSocket or SSE endpoint for real-time updates (if not exists)
   - Ensure API responses are JSON (already compatible)

3. **Templating:**
   - Continue using Jinja2 templates (FastAPI default)
   - Consider component-based approach (Jinja2 macros or include files)
   - Separate CSS/JS files for better organization

### File Structure

```
src/sentrascan/web/
├── templates/
│   ├── base.html (enhanced)
│   ├── dashboard.html (new)
│   ├── index.html (enhanced)
│   ├── scan_detail.html (enhanced)
│   ├── scan_forms.html (enhanced)
│   ├── baselines.html (enhanced)
│   ├── baseline_compare.html (enhanced)
│   ├── login.html (enhanced)
│   └── components/ (new, for reusable components)
│       ├── _scan_card.html
│       ├── _finding_row.html
│       └── _stat_card.html
├── static/ (new)
│   ├── css/
│   │   ├── main.css (or use Tailwind)
│   │   └── components.css
│   ├── js/
│   │   ├── main.js
│   │   ├── charts.js
│   │   ├── realtime.js
│   │   └── utils.js
│   └── images/
│       └── (icons, logos)
```

### Real-Time Updates

- Option 1: WebSocket endpoint in FastAPI (using `websockets` or `fastapi-websocket`)
- Option 2: Server-Sent Events (SSE) - simpler, one-way
- Option 3: Polling (fallback, less ideal but simpler)

### Accessibility Testing

- Use automated tools: axe DevTools, WAVE, Lighthouse
- Manual testing with screen readers (NVDA, JAWS, VoiceOver)
- Keyboard-only navigation testing
- Color contrast checker tools

### Performance Targets

- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Cumulative Layout Shift (CLS): < 0.1

---

## Success Metrics

1. **User Experience:**
   - Reduced time to complete common tasks (trigger scan, view findings) by 30%
   - User satisfaction score (if measured) > 4/5
   - Reduced support tickets related to UI confusion

2. **Accessibility:**
   - WCAG 2.1 AA compliance verified by automated and manual testing
   - Zero critical accessibility violations
   - Keyboard navigation works for all features

3. **Performance:**
   - Page load times < 2s on average connection
   - Smooth interactions (60fps animations)
   - Real-time updates with < 1s latency

4. **Adoption:**
   - Increased usage of UI vs CLI/API (if measurable)
   - Mobile usage increases (if tracking available)

5. **Visual Design:**
   - Consistent design system across all pages
   - Professional appearance suitable for enterprise use

---

## Open Questions

1. **Real-Time Implementation:** Should we use WebSockets or Server-Sent Events for real-time updates? (Recommendation: SSE for simplicity, WebSocket if bidirectional needed)

2. **Chart Library:** Which charting library should we use? (Recommendation: Chart.js for simplicity, D3.js for more customization)

3. **Dark Mode:** Should dark mode be implemented in the initial release or as a follow-up? (Recommendation: Include if time permits, otherwise Phase 2)

4. **Component Library:** Should we build custom components or use a lightweight library? (Recommendation: Custom with Tailwind for full control)

5. **Backend Changes:** Do we need to add new API endpoints for dashboard statistics, or can we calculate on the frontend? (Recommendation: Add optimized endpoints for better performance)

6. **Testing Strategy:** What level of automated testing is needed for the UI? (Recommendation: Manual testing + accessibility audits, automated E2E tests optional)

7. **Migration Strategy:** Should we implement the redesign incrementally (page by page) or as a complete replacement? (Recommendation: Complete replacement for consistency, but can be deployed behind a feature flag)

8. **Browser Support:** What browsers and versions must be supported? (Recommendation: Modern browsers - Chrome, Firefox, Safari, Edge - last 2 versions)

---

## Implementation Phases (Suggested)

### Phase 1: Foundation (Week 1-2)
- Set up design system (colors, typography, spacing)
- Create base template with navigation
- Implement responsive layout structure
- Set up CSS framework (Tailwind or custom)

### Phase 2: Core Pages (Week 3-4)
- Redesign login page
- Redesign dashboard with statistics
- Redesign scan list page
- Redesign scan detail page

### Phase 3: Enhanced Features (Week 5-6)
- Implement scan forms with enhancements
- Redesign baselines page
- Implement baseline comparison with visual diff
- Add data visualization (charts)

### Phase 4: UX Enhancements (Week 7-8)
- Implement real-time updates
- Add toast notifications
- Implement search and advanced filtering
- Add loading states and skeletons

### Phase 5: Accessibility & Polish (Week 9-10)
- Accessibility audit and fixes
- Keyboard navigation testing
- Screen reader testing
- Performance optimization
- Cross-browser testing
- Final design polish

---

## Notes for Junior Developers

- **Start with the base template:** The `base.html` file is the foundation. Enhance it first with proper semantic HTML and navigation.

- **Use semantic HTML:** Always use appropriate HTML elements (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, etc.) for better accessibility and SEO.

- **CSS Organization:** If using custom CSS, organize it into sections: reset/normalize, variables, base styles, components, utilities.

- **JavaScript Best Practices:** Keep JavaScript modular, use event delegation where possible, and ensure all interactive elements work without JavaScript as a progressive enhancement.

- **Accessibility First:** Test with keyboard navigation and screen readers as you build, not as an afterthought.

- **Mobile First:** Design for mobile first, then enhance for larger screens. This makes responsive design easier.

- **Component Reusability:** Create reusable components (Jinja2 macros or include files) for common elements like cards, badges, buttons.

- **Testing:** Test each page on multiple screen sizes and browsers as you build.

---

## Appendix: Current UI Analysis

### Current Strengths
- Functional and works for basic use cases
- Simple, no heavy dependencies
- Fast page loads

### Current Weaknesses
- Basic styling, lacks visual hierarchy
- Not responsive (mobile experience is poor)
- Limited interactivity
- No real-time updates
- No data visualization
- Accessibility concerns (missing ARIA labels, keyboard navigation issues)
- No loading states or user feedback
- Basic error handling
- Limited filtering and search capabilities

### Pages to Redesign
1. `base.html` - Base template with navigation
2. `index.html` - Scan list (enhance to dashboard)
3. `scan_detail.html` - Scan details with findings
4. `scan_forms.html` - Scan trigger forms
5. `baselines.html` - Baselines list
6. `baseline_compare.html` - Baseline comparison
7. `login.html` - Login page
8. `scan_submitted.html` - Success/confirmation page (can be merged into scan_detail with real-time updates)

---

**Document Version:** 1.0  
**Last Updated:** [Current Date]  
**Status:** Draft - Ready for Review

