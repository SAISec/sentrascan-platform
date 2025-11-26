"""
Performance testing for UI pages.

Tests Core Web Vitals:
- FCP (First Contentful Paint) < 1.5s
- LCP (Largest Contentful Paint) < 2.5s
- TTI (Time to Interactive) < 3.5s
- CLS (Cumulative Layout Shift) < 0.1
"""
import pytest
import time
from playwright.sync_api import Page


@pytest.fixture
def authenticated_page(page: Page, api_base, admin_key):
    """Create an authenticated page for performance testing."""
    # Login first
    page.goto(f"{api_base}/login", wait_until="networkidle")
    page.fill('input[name="api_key"]', admin_key)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{api_base}/**", timeout=5000)
    return page


def get_performance_metrics(page: Page):
    """Extract performance metrics from the page using PerformanceObserver."""
    # Wait for page to be fully loaded
    page.wait_for_load_state("networkidle")
    
    # Get all performance metrics using PerformanceObserver
    metrics = page.evaluate("""
        () => {
            return new Promise((resolve) => {
                const perf = performance.getEntriesByType('navigation')[0];
                const paint = performance.getEntriesByType('paint');
                
                // Get FCP (First Contentful Paint)
                const fcpEntry = paint.find(entry => entry.name === 'first-contentful-paint');
                const fcp = fcpEntry ? fcpEntry.startTime : null;
                
                // Measure LCP using PerformanceObserver
                let lcp = 0;
                let lcpObserver;
                try {
                    lcpObserver = new PerformanceObserver((list) => {
                        const entries = list.getEntries();
                        const lastEntry = entries[entries.length - 1];
                        lcp = lastEntry.renderTime || lastEntry.loadTime;
                    });
                    lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
                } catch (e) {
                    // Fallback to loadEventEnd if LCP observer not supported
                    lcp = perf.loadEventEnd - perf.fetchStart;
                }
                
                // Measure CLS using PerformanceObserver
                let cls = 0;
                let clsObserver;
                try {
                    clsObserver = new PerformanceObserver((list) => {
                        for (const entry of list.getEntries()) {
                            if (!entry.hadRecentInput) {
                                cls += entry.value;
                            }
                        }
                    });
                    clsObserver.observe({ type: 'layout-shift', buffered: true });
                } catch (e) {
                    // CLS not supported
                    cls = 0;
                }
                
                // Calculate TTI (Time to Interactive)
                // TTI is when the page is interactive - approximate using domInteractive
                // A more accurate TTI would require measuring when JS execution is complete
                const tti = perf.domInteractive - perf.fetchStart;
                
                // Wait a bit for all metrics to stabilize
                setTimeout(() => {
                    if (lcpObserver) lcpObserver.disconnect();
                    if (clsObserver) clsObserver.disconnect();
                    
                    // If LCP wasn't captured, use loadEventEnd as fallback
                    if (lcp === 0) {
                        lcp = perf.loadEventEnd - perf.fetchStart;
                    }
                    
                    resolve({
                        fcp: fcp,
                        lcp: lcp,
                        tti: tti,
                        cls: cls,
                        domContentLoaded: perf.domContentLoadedEventEnd - perf.fetchStart,
                        loadComplete: perf.loadEventEnd - perf.fetchStart,
                    });
                }, 2000);
            });
        }
    """)
    
    return metrics


@pytest.mark.integration
def test_dashboard_performance(authenticated_page: Page, api_base):
    """Test dashboard page performance metrics."""
    # Navigate to dashboard and measure performance
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    metrics = get_performance_metrics(authenticated_page)
    
    # Assert performance thresholds
    assert metrics['fcp'] is not None, "FCP metric not available"
    assert metrics['fcp'] < 1500, f"FCP {metrics['fcp']}ms exceeds threshold of 1500ms"
    
    assert metrics['lcp'] < 2500, f"LCP {metrics['lcp']}ms exceeds threshold of 2500ms"
    
    assert metrics['tti'] < 3500, f"TTI {metrics['tti']}ms exceeds threshold of 3500ms"
    
    assert metrics['cls'] < 0.1, f"CLS {metrics['cls']} exceeds threshold of 0.1"


@pytest.mark.integration
def test_scan_list_performance(authenticated_page: Page, api_base):
    """Test scan list page performance metrics."""
    # Navigate to scan list and measure performance
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    metrics = get_performance_metrics(authenticated_page)
    
    # Assert performance thresholds
    assert metrics['fcp'] is not None, "FCP metric not available"
    assert metrics['fcp'] < 1500, f"FCP {metrics['fcp']}ms exceeds threshold of 1500ms"
    
    assert metrics['lcp'] < 2500, f"LCP {metrics['lcp']}ms exceeds threshold of 2500ms"
    
    assert metrics['tti'] < 3500, f"TTI {metrics['tti']}ms exceeds threshold of 3500ms"
    
    assert metrics['cls'] < 0.1, f"CLS {metrics['cls']} exceeds threshold of 0.1"


@pytest.mark.integration
def test_scan_detail_performance(authenticated_page: Page, api_base):
    """Test scan detail page performance metrics."""
    # Navigate to a scan detail page (if available)
    # First, try to get a scan ID from the list
    authenticated_page.goto(f"{api_base}/", wait_until="networkidle")
    
    # Look for a scan link
    scan_link = authenticated_page.locator('a[href*="/scan/"]').first
    if scan_link.count() > 0:
        scan_url = scan_link.get_attribute('href')
        if scan_url:
            if not scan_url.startswith('http'):
                scan_url = f"{api_base}{scan_url}"
            
            authenticated_page.goto(scan_url, wait_until="networkidle")
            metrics = get_performance_metrics(authenticated_page)
            
            # Assert performance thresholds
            assert metrics['fcp'] is not None, "FCP metric not available"
            assert metrics['fcp'] < 1500, f"FCP {metrics['fcp']}ms exceeds threshold of 1500ms"
            
            assert metrics['lcp'] < 2500, f"LCP {metrics['lcp']}ms exceeds threshold of 2500ms"
            
            assert metrics['tti'] < 3500, f"TTI {metrics['tti']}ms exceeds threshold of 3500ms"
            
            assert metrics['cls'] < 0.1, f"CLS {metrics['cls']} exceeds threshold of 0.1"
    else:
        pytest.skip("No scan available to test detail page performance")


@pytest.mark.integration
def test_scan_forms_performance(authenticated_page: Page, api_base):
    """Test scan forms page performance metrics."""
    # Navigate to scan forms and measure performance
    authenticated_page.goto(f"{api_base}/ui/scan", wait_until="networkidle")
    
    metrics = get_performance_metrics(authenticated_page)
    
    # Assert performance thresholds
    assert metrics['fcp'] is not None, "FCP metric not available"
    assert metrics['fcp'] < 1500, f"FCP {metrics['fcp']}ms exceeds threshold of 1500ms"
    
    assert metrics['lcp'] < 2500, f"LCP {metrics['lcp']}ms exceeds threshold of 2500ms"
    
    assert metrics['tti'] < 3500, f"TTI {metrics['tti']}ms exceeds threshold of 3500ms"
    
    assert metrics['cls'] < 0.1, f"CLS {metrics['cls']} exceeds threshold of 0.1"


@pytest.mark.integration
def test_baselines_performance(authenticated_page: Page, api_base):
    """Test baselines page performance metrics."""
    # Navigate to baselines and measure performance
    authenticated_page.goto(f"{api_base}/baselines", wait_until="networkidle")
    
    metrics = get_performance_metrics(authenticated_page)
    
    # Assert performance thresholds
    assert metrics['fcp'] is not None, "FCP metric not available"
    assert metrics['fcp'] < 1500, f"FCP {metrics['fcp']}ms exceeds threshold of 1500ms"
    
    assert metrics['lcp'] < 2500, f"LCP {metrics['lcp']}ms exceeds threshold of 2500ms"
    
    assert metrics['tti'] < 3500, f"TTI {metrics['tti']}ms exceeds threshold of 3500ms"
    
    assert metrics['cls'] < 0.1, f"CLS {metrics['cls']} exceeds threshold of 0.1"

