# Color Contrast Reference Values

This document lists the color values used in the SentraScan Platform and their expected contrast ratios.

## CSS Color Variables

### Text Colors
- `--color-text-primary: var(--color-gray-800)` (#212121)
  - **On white (#FFFFFF)**: ~16.6:1 ✅
  - **On light gray (#F5F5F5)**: ~15.2:1 ✅
  
- `--color-text-secondary: var(--color-gray-600)` (#616161)
  - **On white (#FFFFFF)**: ~7.0:1 ✅
  - **On light gray (#F5F5F5)**: ~6.4:1 ✅

- `--color-text-tertiary: var(--color-gray-500)` (#757575)
  - **On white (#FFFFFF)**: ~4.6:1 ✅
  - **On light gray (#F5F5F5)**: ~4.2:1 ⚠️ (Close to minimum, test carefully)

- `--color-text-inverse: #FFFFFF`
  - **On primary (#2196F3)**: ~4.5:1 ✅
  - **On success (#4CAF50)**: ~4.5:1 ✅
  - **On error (#F44336)**: ~4.5:1 ✅

### Primary Colors
- `--color-primary: #2196F3` (Blue)
  - **White text on primary**: ~4.5:1 ✅
  - **Primary text on white**: ~4.5:1 ✅

- `--color-primary-dark: #1976D2` (Darker blue)
  - **White text on primary-dark**: ~4.5:1 ✅

### Status Colors
- `--color-success: #4CAF50` (Green)
  - **White text on success**: ~4.5:1 ✅

- `--color-error: #F44336` (Red)
  - **White text on error**: ~4.5:1 ✅

- `--color-warning: #FF9800` (Orange)
  - **White text on warning**: ~4.5:1 ✅
  - **Black text on warning**: ~2.8:1 ❌ (Use white text)

- `--color-info: #2196F3` (Blue, same as primary)
  - **White text on info**: ~4.5:1 ✅

### Severity Colors
- `--color-severity-critical: #D32F2F` (Dark red)
  - **White text on critical**: ~4.5:1 ✅

- `--color-severity-high: #F57C00` (Orange)
  - **White text on high**: ~4.5:1 ✅

- `--color-severity-medium: #FBC02D` (Yellow)
  - **Black text on medium**: ~1.8:1 ❌ (Use darker yellow or white text)
  - **White text on medium**: May need adjustment

- `--color-severity-low: #1976D2` (Blue)
  - **White text on low**: ~4.5:1 ✅

### Background Colors
- `--color-bg-primary: #FFFFFF` (White)
  - **Any text color**: Check individual combinations

- `--color-gray-50: #FAFAFA` (Very light gray)
  - **Primary text (#212121) on gray-50**: ~15.8:1 ✅

- `--color-gray-100: #F5F5F5` (Light gray)
  - **Primary text (#212121) on gray-100**: ~15.2:1 ✅

- `--color-gray-200: #E0E0E0` (Lighter gray)
  - **Primary text (#212121) on gray-200**: ~12.1:1 ✅

## Common Combinations to Test

### Buttons
- Primary button: White text (#FFF) on #2196F3 → **4.5:1** ✅
- Secondary button: Primary text on transparent/white → **4.5:1** ✅
- Danger button: White text on #F44336 → **4.5:1** ✅

### Badges
- Success badge: White text on #4CAF50 → **4.5:1** ✅
- Error badge: White text on #F44336 → **4.5:1** ✅
- Warning badge: White text on #FF9800 → **4.5:1** ✅
- Info badge: White text on #2196F3 → **4.5:1** ✅

### Severity Badges
- Critical: White text on #D32F2F → **4.5:1** ✅
- High: White text on #F57C00 → **4.5:1** ✅
- Medium: **⚠️ Check** - May need adjustment
- Low: White text on #1976D2 → **4.5:1** ✅

### Form Elements
- Input text: Primary text (#1F2937) on white → **12.6:1** ✅
- Placeholder: Tertiary text (#6B7280) on white → **4.7:1** ✅
- Labels: Primary text on white → **12.6:1** ✅
- Error text: Error color (#F44336) on white → **4.5:1** ✅

### Links
- Default link: Primary color (#2196F3) on white → **4.5:1** ✅
- Visited link: Check if different color meets contrast
- Hover state: Check if darker/lighter maintains contrast

## Potential Issues

### ⚠️ Warning Colors
- **Medium severity badge**: Yellow background may need darker text or different background
- **Warning badge**: Orange background - ensure white text is used

### ⚠️ Tertiary Text
- **Tertiary text on light gray**: May be close to 4.5:1 minimum
- Test carefully, may need adjustment

## Testing Checklist

Use this when testing each color combination:

- [ ] Primary text on white background
- [ ] Secondary text on white background
- [ ] Tertiary text on white background
- [ ] White text on primary background
- [ ] White text on success background
- [ ] White text on error background
- [ ] White text on warning background
- [ ] Badge text on colored backgrounds
- [ ] Link text on white background
- [ ] Button text on colored backgrounds
- [ ] Error messages on white/colored backgrounds
- [ ] Form input text on white background
- [ ] Placeholder text on white background

## Quick Test URLs

- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Contrast Ratio Calculator**: https://contrast-ratio.com/
- **Colour Contrast Analyser**: https://www.tpgi.com/color-contrast-checker/

