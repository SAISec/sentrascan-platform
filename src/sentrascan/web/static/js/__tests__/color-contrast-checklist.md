# Color Contrast Testing Quick Checklist

Quick reference for color contrast testing.

## WCAG AA Requirements

- **Normal Text** (< 18pt): **4.5:1** minimum
- **Large Text** (≥ 18pt): **3:1** minimum
- **UI Components**: **3:1** minimum

## Quick Test Tools

1. **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
2. **Colour Contrast Analyser**: Download desktop app
3. **axe DevTools**: Browser extension
4. **WAVE**: Browser extension
5. **Lighthouse**: Chrome DevTools

## Essential Checks (Every Page)

- [ ] Page heading text meets contrast
- [ ] Body text meets contrast
- [ ] Link text meets contrast
- [ ] Button text meets contrast
- [ ] Form labels meet contrast
- [ ] Input text meets contrast
- [ ] Error messages meet contrast
- [ ] Badge text meets contrast
- [ ] Status messages meet contrast

## Page-Specific Checks

### Login Page
- [ ] Heading text
- [ ] Form labels
- [ ] Input text
- [ ] Button text
- [ ] Error messages
- [ ] Help text

### Dashboard
- [ ] Stat card values
- [ ] Stat card labels
- [ ] Chart text
- [ ] Table text
- [ ] Badge text

### Scan List
- [ ] Filter labels
- [ ] Table headers
- [ ] Table cell text
- [ ] Status badges
- [ ] Link text

### Scan Detail
- [ ] Status badges
- [ ] Severity badges (critical, high, medium, low)
- [ ] Finding text
- [ ] Button text

### Scan Forms
- [ ] Tab text
- [ ] Form labels
- [ ] Input text
- [ ] Error messages
- [ ] Button text

### Baselines
- [ ] Table text
- [ ] Badge text
- [ ] Button text

## Component Checks

### Buttons
- [ ] Default state
- [ ] Hover state
- [ ] Focus state
- [ ] Disabled state

### Badges
- [ ] Success (green)
- [ ] Error (red)
- [ ] Warning (yellow/orange)
- [ ] Info (blue)
- [ ] Neutral (gray)

### Links
- [ ] Default
- [ ] Visited
- [ ] Hover
- [ ] Focus

### Forms
- [ ] Input text
- [ ] Placeholder
- [ ] Labels
- [ ] Help text
- [ ] Error messages

## Critical Issues (Must Fix)

- [ ] Text below 4.5:1 (normal) or 3:1 (large)
- [ ] Button text doesn't meet contrast
- [ ] Badge text doesn't meet contrast
- [ ] Error messages don't meet contrast
- [ ] Links don't meet contrast in all states
- [ ] Disabled elements don't meet contrast

## Test Results

**Page**: _________________
**Date**: _________________
**Tester**: _________________
**Tool**: _________________

**Status**: ✅ Pass / ❌ Fail

**Issues**:
1. 
2. 
3. 

**Fixed**: Yes / No

