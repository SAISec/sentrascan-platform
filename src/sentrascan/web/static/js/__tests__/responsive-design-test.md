# Responsive Design Testing Guide

This document provides comprehensive instructions for testing the SentraScan Platform across different device sizes and breakpoints to ensure responsive design works correctly.

## Breakpoints

Based on the design system, the following breakpoints are used:

- **Mobile**: < 768px (phones)
- **Tablet**: 768px - 1024px (tablets, small laptops)
- **Desktop**: > 1024px (desktops, large screens)

## Testing Methods

### 1. Browser DevTools Responsive Mode

#### Chrome/Edge
1. Open DevTools (F12)
2. Click device toolbar icon (Ctrl+Shift+M)
3. Select device preset or enter custom dimensions
4. Test different orientations (portrait/landscape)

#### Firefox
1. Open DevTools (F12)
2. Click responsive design mode icon (Ctrl+Shift+M)
3. Select device or enter custom dimensions
4. Test different orientations

#### Safari
1. Enable Develop menu (Preferences → Advanced)
2. Develop → Enter Responsive Design Mode
3. Select device or enter custom dimensions

### 2. Physical Devices

Test on actual devices when possible:
- **Mobile**: iPhone, Android phones
- **Tablet**: iPad, Android tablets
- **Desktop**: Various screen sizes

### 3. Online Testing Tools

- **BrowserStack**: https://www.browserstack.com/
- **Responsive Design Checker**: https://responsivedesignchecker.com/
- **Am I Responsive**: http://ami.responsivedesign.is/

## Testing Checklist

### General Responsive Checks

#### Layout
- [ ] Content doesn't overflow horizontally
- [ ] No horizontal scrolling
- [ ] Content reflows appropriately
- [ ] Spacing is appropriate for screen size
- [ ] Images scale correctly
- [ ] Tables are scrollable or responsive

#### Navigation
- [ ] Mobile menu appears on small screens
- [ ] Hamburger menu is accessible
- [ ] Navigation is usable on touch devices
- [ ] Menu closes after selection
- [ ] Desktop navigation appears on large screens

#### Typography
- [ ] Text is readable at all sizes
- [ ] Font sizes scale appropriately
- [ ] Line heights are comfortable
- [ ] Text doesn't overflow containers

#### Touch Targets
- [ ] Buttons are at least 44x44px
- [ ] Links have adequate spacing
- [ ] Interactive elements are easy to tap
- [ ] No elements are too close together

## Page-Specific Testing

### 1. Login Page (`/login`)

#### Mobile (< 768px)
- [ ] Login card is full width or appropriately sized
- [ ] Form fields are full width
- [ ] Button is full width or appropriately sized
- [ ] Text is readable
- [ ] Password toggle button is accessible
- [ ] No horizontal scrolling

#### Tablet (768px - 1024px)
- [ ] Login card is centered and appropriately sized
- [ ] Form layout is comfortable
- [ ] Button sizing is appropriate

#### Desktop (> 1024px)
- [ ] Login card is centered with max-width
- [ ] Layout is comfortable and not too wide
- [ ] Spacing is appropriate

**Test Dimensions:**
- Mobile: 375px, 414px (iPhone sizes)
- Tablet: 768px, 1024px
- Desktop: 1280px, 1920px

---

### 2. Dashboard Page (`/`)

#### Mobile (< 768px)
- [ ] Stat cards stack vertically
- [ ] Charts are readable and scrollable
- [ ] Table has horizontal scroll
- [ ] Filters stack vertically
- [ ] Navigation uses hamburger menu
- [ ] Global search is accessible

#### Tablet (768px - 1024px)
- [ ] Stat cards may be in grid (2 columns)
- [ ] Charts are appropriately sized
- [ ] Table may be scrollable or responsive
- [ ] Filters are in a comfortable layout

#### Desktop (> 1024px)
- [ ] Stat cards in grid (4 columns)
- [ ] Charts are full width
- [ ] Table is fully visible
- [ ] Filters are in a row
- [ ] Sidebar navigation is visible

**Test Dimensions:**
- Mobile: 375px, 414px
- Tablet: 768px, 1024px
- Desktop: 1280px, 1920px

---

### 3. Scan List Page (`/`)

#### Mobile (< 768px)
- [ ] Filters stack vertically
- [ ] Table has horizontal scroll
- [ ] Pagination is touch-friendly
- [ ] Action buttons are accessible
- [ ] Export button is visible and accessible

#### Tablet (768px - 1024px)
- [ ] Filters may be in a grid
- [ ] Table may be scrollable
- [ ] Layout is comfortable

#### Desktop (> 1024px)
- [ ] Filters are in a row
- [ ] Table is fully visible
- [ ] All columns are visible
- [ ] Pagination is accessible

**Test Dimensions:**
- Mobile: 375px, 414px
- Tablet: 768px, 1024px
- Desktop: 1280px, 1920px

---

### 4. Scan Detail Page (`/scan/{id}`)

#### Mobile (< 768px)
- [ ] Header information stacks vertically
- [ ] Action buttons stack or wrap
- [ ] Findings groups are readable
- [ ] Findings table has horizontal scroll
- [ ] Expand/collapse buttons are touch-friendly
- [ ] Modal is full-screen or appropriately sized

#### Tablet (768px - 1024px)
- [ ] Layout is comfortable
- [ ] Tables may be scrollable
- [ ] Buttons are appropriately sized

#### Desktop (> 1024px)
- [ ] Full layout is visible
- [ ] Tables are fully visible
- [ ] Side-by-side layouts work

**Test Dimensions:**
- Mobile: 375px, 414px
- Tablet: 768px, 1024px
- Desktop: 1280px, 1920px

---

### 5. Scan Forms (`/ui/scan`)

#### Mobile (< 768px)
- [ ] Tabs are scrollable or stack
- [ ] Form fields are full width
- [ ] Checkboxes are touch-friendly
- [ ] Advanced sections are accessible
- [ ] Submit button is full width or accessible
- [ ] Form is usable without zooming

#### Tablet (768px - 1024px)
- [ ] Tabs are accessible
- [ ] Form layout is comfortable
- [ ] All fields are accessible

#### Desktop (> 1024px)
- [ ] Tabs are in a row
- [ ] Form has appropriate max-width
- [ ] Layout is comfortable

**Test Dimensions:**
- Mobile: 375px, 414px
- Tablet: 768px, 1024px
- Desktop: 1280px, 1920px

---

### 6. Baselines Page (`/baselines`)

#### Mobile (< 768px)
- [ ] Comparison form stacks vertically
- [ ] Table has horizontal scroll
- [ ] Action buttons are accessible
- [ ] Create button is visible

#### Tablet (768px - 1024px)
- [ ] Form layout is comfortable
- [ ] Table may be scrollable

#### Desktop (> 1024px)
- [ ] Comparison form is in a row
- [ ] Table is fully visible

**Test Dimensions:**
- Mobile: 375px, 414px
- Tablet: 768px, 1024px
- Desktop: 1280px, 1920px

---

### 7. Baseline Comparison Page (`/baseline/compare`)

#### Mobile (< 768px)
- [ ] Diff view stacks vertically
- [ ] Search and filters are accessible
- [ ] JSON viewer is scrollable
- [ ] Copy buttons are touch-friendly
- [ ] Side-by-side layout becomes stacked

#### Tablet (768px - 1024px)
- [ ] Layout may be side-by-side or stacked
- [ ] Content is readable

#### Desktop (> 1024px)
- [ ] Side-by-side layout works
- [ ] All content is visible

**Test Dimensions:**
- Mobile: 375px, 414px
- Tablet: 768px, 1024px
- Desktop: 1280px, 1920px

## Component-Specific Testing

### Navigation

#### Mobile
- [ ] Hamburger menu appears
- [ ] Menu opens/closes correctly
- [ ] Menu items are touch-friendly (44x44px)
- [ ] Menu doesn't cover content
- [ ] Menu closes on selection

#### Desktop
- [ ] Horizontal navigation is visible
- [ ] Dropdown menus work
- [ ] User menu is accessible

### Tables

#### Mobile
- [ ] Table has horizontal scroll
- [ ] Scroll indicator is visible
- [ ] Headers are sticky or visible
- [ ] Touch scrolling works smoothly

#### Tablet/Desktop
- [ ] Table is fully visible
- [ ] All columns are accessible
- [ ] Sorting works correctly

### Modals

#### Mobile
- [ ] Modal is full-screen or appropriately sized
- [ ] Modal doesn't overflow viewport
- [ ] Close button is accessible
- [ ] Form fields are usable
- [ ] Modal is scrollable if needed

#### Desktop
- [ ] Modal is centered
- [ ] Modal has max-width
- [ ] Content is readable

### Forms

#### Mobile
- [ ] All fields are full width or appropriately sized
- [ ] Labels are above inputs
- [ ] Touch targets are adequate (44x44px)
- [ ] Date pickers are usable
- [ ] Dropdowns are usable

#### Desktop
- [ ] Form has appropriate max-width
- [ ] Labels may be beside inputs
- [ ] Layout is comfortable

### Charts

#### Mobile
- [ ] Charts are readable
- [ ] Charts are scrollable if needed
- [ ] Legends are accessible
- [ ] Tooltips work on touch

#### Desktop
- [ ] Charts are full width
- [ ] All elements are visible
- [ ] Interactions work correctly

## Orientation Testing

### Portrait Mode
- [ ] All content is accessible
- [ ] Navigation works
- [ ] Forms are usable
- [ ] Tables are scrollable

### Landscape Mode
- [ ] Layout adapts appropriately
- [ ] More content may be visible
- [ ] Tables may show more columns
- [ ] Forms may use more horizontal space

## Touch Testing

### Touch Targets
- [ ] All buttons are at least 44x44px
- [ ] Links have adequate spacing
- [ ] Checkboxes are easy to tap
- [ ] Form fields are easy to tap
- [ ] No elements are too close together

### Touch Gestures
- [ ] Swipe works on tables (if implemented)
- [ ] Pinch to zoom works (if enabled)
- [ ] Scroll works smoothly
- [ ] No accidental taps

## Browser Testing

### Mobile Browsers
- [ ] Chrome (Android)
- [ ] Safari (iOS)
- [ ] Firefox (Android)
- [ ] Samsung Internet

### Tablet Browsers
- [ ] Safari (iPad)
- [ ] Chrome (Android tablet)
- [ ] Firefox (Android tablet)

### Desktop Browsers
- [ ] Chrome (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Edge (latest 2 versions)

## Common Issues to Check

### ❌ Problems to Identify

1. **Horizontal Scrolling**
   - Content overflows viewport
   - Fixed width elements too wide
   - Images not responsive

2. **Text Readability**
   - Text too small on mobile
   - Text too large on desktop
   - Line lengths too long

3. **Touch Targets**
   - Buttons too small
   - Links too close together
   - Form fields hard to tap

4. **Layout Issues**
   - Elements overlap
   - Content cut off
   - Spacing too tight or too loose

5. **Navigation Issues**
   - Menu not accessible on mobile
   - Menu covers content
   - Desktop nav appears on mobile

6. **Table Issues**
   - Tables overflow on mobile
   - No horizontal scroll
   - Headers not visible

7. **Modal Issues**
   - Modal too wide for mobile
   - Modal content cut off
   - Close button not accessible

## Test Results Template

### Page: [Page Name]
**Date**: [Date]
**Tester**: [Name]
**Browser**: [Browser/Version]
**Device**: [Device/Size]

#### Mobile (< 768px)
- **Width Tested**: [e.g., 375px, 414px]
- **Layout**: ✅ Pass / ❌ Fail
- **Navigation**: ✅ Pass / ❌ Fail
- **Touch Targets**: ✅ Pass / ❌ Fail
- **Text Readability**: ✅ Pass / ❌ Fail
- **Issues**: [List issues]

#### Tablet (768px - 1024px)
- **Width Tested**: [e.g., 768px, 1024px]
- **Layout**: ✅ Pass / ❌ Fail
- **Navigation**: ✅ Pass / ❌ Fail
- **Touch Targets**: ✅ Pass / ❌ Fail
- **Text Readability**: ✅ Pass / ❌ Fail
- **Issues**: [List issues]

#### Desktop (> 1024px)
- **Width Tested**: [e.g., 1280px, 1920px]
- **Layout**: ✅ Pass / ❌ Fail
- **Navigation**: ✅ Pass / ❌ Fail
- **Text Readability**: ✅ Pass / ❌ Fail
- **Issues**: [List issues]

#### Overall Assessment
- **Status**: ✅ Pass / ❌ Fail / ⚠️ Needs Improvement
- **Critical Issues**: [List critical issues]
- **Recommendations**: [Suggestions]

## Responsive Design Best Practices

### Mobile-First Approach
- Design for mobile first
- Add enhancements for larger screens
- Test on actual devices when possible

### Flexible Layouts
- Use relative units (%, em, rem)
- Avoid fixed widths
- Use max-width for containers

### Responsive Images
- Use srcset for different sizes
- Use appropriate image formats
- Lazy load images

### Touch-Friendly
- Minimum 44x44px touch targets
- Adequate spacing between elements
- Large enough text

### Performance
- Optimize for mobile networks
- Minimize HTTP requests
- Use efficient CSS

## Resources

- [MDN Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [Google Mobile-Friendly Test](https://search.google.com/test/mobile-friendly)
- [Responsive Design Patterns](https://responsivedesign.is/patterns/)
- [Touch Target Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)

