# Responsive Design Testing Quick Checklist

Quick reference for responsive design testing.

## Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## Quick Test Setup

1. **Open DevTools** (F12)
2. **Enable Responsive Mode** (Ctrl+Shift+M)
3. **Select Device** or enter custom width
4. **Test Different Sizes**

## Essential Checks (Every Page)

### Mobile
- [ ] No horizontal scrolling
- [ ] Content is readable
- [ ] Navigation menu works
- [ ] Touch targets are adequate (44x44px)
- [ ] Forms are usable
- [ ] Tables are scrollable

### Tablet
- [ ] Layout is comfortable
- [ ] Content is readable
- [ ] Navigation works
- [ ] Tables are accessible

### Desktop
- [ ] Layout uses space well
- [ ] Content is not too wide
- [ ] Navigation is visible
- [ ] All features accessible

## Page-Specific Quick Checks

### Login
- [ ] Mobile: Card is appropriately sized
- [ ] Desktop: Card is centered with max-width

### Dashboard
- [ ] Mobile: Stat cards stack
- [ ] Mobile: Charts are readable
- [ ] Desktop: Stat cards in grid

### Scan List
- [ ] Mobile: Table scrolls horizontally
- [ ] Mobile: Filters stack
- [ ] Desktop: Table fully visible

### Scan Detail
- [ ] Mobile: Findings table scrolls
- [ ] Mobile: Buttons stack/wrap
- [ ] Desktop: Full layout visible

### Scan Forms
- [ ] Mobile: Form fields full width
- [ ] Mobile: Tabs accessible
- [ ] Desktop: Form has max-width

### Baselines
- [ ] Mobile: Table scrolls
- [ ] Mobile: Form stacks
- [ ] Desktop: Full layout

### Baseline Compare
- [ ] Mobile: Diff stacks vertically
- [ ] Desktop: Side-by-side layout

## Component Checks

### Navigation
- [ ] Mobile: Hamburger menu
- [ ] Desktop: Horizontal nav

### Tables
- [ ] Mobile: Horizontal scroll
- [ ] Desktop: Fully visible

### Modals
- [ ] Mobile: Full-screen or sized
- [ ] Desktop: Centered with max-width

### Forms
- [ ] Mobile: Fields full width
- [ ] Desktop: Appropriate max-width

## Critical Issues (Must Fix)

- [ ] Horizontal scrolling on mobile
- [ ] Text too small to read
- [ ] Touch targets too small
- [ ] Content cut off
- [ ] Navigation not accessible
- [ ] Forms unusable on mobile

## Test Dimensions

**Mobile**: 375px, 414px
**Tablet**: 768px, 1024px
**Desktop**: 1280px, 1920px

## Test Results

**Page**: _________________
**Date**: _________________
**Tester**: _________________
**Browser**: _________________

**Mobile**: ✅ Pass / ❌ Fail
**Tablet**: ✅ Pass / ❌ Fail
**Desktop**: ✅ Pass / ❌ Fail

**Issues**:
1. 
2. 
3. 

