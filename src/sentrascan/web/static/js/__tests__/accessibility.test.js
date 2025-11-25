/**
 * Accessibility tests using axe-core
 * Automated accessibility testing for WCAG 2.1 AA compliance
 */

describe('Accessibility Tests (axe-core)', function() {
  let axe;

  beforeAll(function(done) {
    // Load axe-core from CDN
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/axe-core@4.8.0/axe.min.js';
    script.onload = function() {
      axe = window.axe;
      done();
    };
    script.onerror = function() {
      console.error('Failed to load axe-core');
      done.fail('Failed to load axe-core');
    };
    document.head.appendChild(script);
  });

  beforeEach(function() {
    // Setup DOM for each test
    document.body.innerHTML = '';
  });

  afterEach(function() {
    // Clean up
    document.body.innerHTML = '';
  });

  describe('Page Structure', function() {
    it('should have proper semantic HTML structure', function(done) {
      document.body.innerHTML = `
        <header>
          <nav>
            <ul>
              <li><a href="/">Home</a></li>
            </ul>
          </nav>
        </header>
        <main>
          <h1>Page Title</h1>
          <section>
            <h2>Section Title</h2>
            <p>Content</p>
          </section>
        </main>
        <footer>
          <p>Footer content</p>
        </footer>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations;
          expect(violations.length).toBe(0);
          
          if (violations.length > 0) {
            console.error('Accessibility violations:', violations);
          }
          
          done();
        });
      } else {
        done();
      }
    });

    it('should have proper heading hierarchy', function(done) {
      document.body.innerHTML = `
        <main>
          <h1>Main Title</h1>
          <h2>Section Title</h2>
          <h3>Subsection Title</h3>
        </main>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'heading-order' || v.id === 'page-has-heading-one'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });
  });

  describe('Form Accessibility', function() {
    it('should have labels associated with form inputs', function(done) {
      document.body.innerHTML = `
        <form>
          <label for="input1">Input Label</label>
          <input type="text" id="input1" name="input1">
          <label for="textarea1">Textarea Label</label>
          <textarea id="textarea1" name="textarea1"></textarea>
          <label for="select1">Select Label</label>
          <select id="select1" name="select1">
            <option value="1">Option 1</option>
          </select>
        </form>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'label' || v.id === 'form-field-multiple-labels'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });

    it('should have proper ARIA attributes for required fields', function(done) {
      document.body.innerHTML = `
        <form>
          <label for="required-input">Required Field</label>
          <input type="text" id="required-input" required aria-required="true">
        </form>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'aria-required-attr'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });

    it('should have error messages associated with inputs', function(done) {
      document.body.innerHTML = `
        <form>
          <label for="error-input">Input with Error</label>
          <input type="text" id="error-input" aria-invalid="true" aria-describedby="error-message">
          <div id="error-message" role="alert">Error message</div>
        </form>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'aria-describedby'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });
  });

  describe('Interactive Elements', function() {
    it('should have accessible buttons', function(done) {
      document.body.innerHTML = `
        <button>Click me</button>
        <button aria-label="Close dialog">×</button>
        <input type="button" value="Submit">
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'button-name' || v.id === 'aria-label'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });

    it('should have proper focus indicators', function(done) {
      document.body.innerHTML = `
        <style>
          button:focus-visible {
            outline: 2px solid blue;
            outline-offset: 2px;
          }
        </style>
        <button>Focusable Button</button>
        <a href="#">Focusable Link</a>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'focus-order-semantics'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });

    it('should have keyboard accessible modals', function(done) {
      document.body.innerHTML = `
        <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <h2 id="modal-title">Modal Title</h2>
          <button class="modal-close" aria-label="Close modal">×</button>
          <p>Modal content</p>
        </div>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'aria-modal' || v.id === 'aria-labelledby'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });
  });

  describe('Images and Icons', function() {
    it('should have alt text for images', function(done) {
      document.body.innerHTML = `
        <img src="test.jpg" alt="Test image description">
        <img src="decorative.jpg" alt="" role="presentation">
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'image-alt'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });

    it('should have aria-hidden for decorative icons', function(done) {
      document.body.innerHTML = `
        <button>
          <span aria-hidden="true">✓</span>
          <span class="sr-only">Success</span>
        </button>
        <div aria-hidden="true">Decorative icon</div>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'aria-hidden-focus'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });
  });

  describe('Tables', function() {
    it('should have proper table headers with scope', function(done) {
      document.body.innerHTML = `
        <table>
          <caption>Test Table</caption>
          <thead>
            <tr>
              <th scope="col">Column 1</th>
              <th scope="col">Column 2</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Data 1</td>
              <td>Data 2</td>
            </tr>
          </tbody>
        </table>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'th-has-data-cells' || v.id === 'scope-value'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });
  });

  describe('Color Contrast', function() {
    it('should meet WCAG AA contrast requirements', function(done) {
      document.body.innerHTML = `
        <style>
          .text-primary {
            color: #333;
            background: #fff;
          }
          .text-secondary {
            color: #666;
            background: #fff;
          }
        </style>
        <p class="text-primary">Primary text</p>
        <p class="text-secondary">Secondary text</p>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'color-contrast'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });
  });

  describe('ARIA Live Regions', function() {
    it('should have proper ARIA live regions for dynamic content', function(done) {
      document.body.innerHTML = `
        <div aria-live="polite" aria-atomic="false" id="live-region">
          Dynamic content will appear here
        </div>
        <div role="alert" aria-live="assertive">
          Important alert message
        </div>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'aria-live'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });
  });

  describe('Skip Links', function() {
    it('should have skip links for main content', function(done) {
      document.body.innerHTML = `
        <a href="#main-content" class="skip-link">Skip to main content</a>
        <header>Navigation</header>
        <main id="main-content">
          <h1>Main Content</h1>
        </main>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'bypass'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });
  });

  describe('Landmarks', function() {
    it('should have proper ARIA landmarks', function(done) {
      document.body.innerHTML = `
        <header role="banner">
          <nav role="navigation">Navigation</nav>
        </header>
        <main role="main">
          <article>
            <section>
              <h1>Article Title</h1>
            </section>
          </article>
        </main>
        <aside role="complementary">Sidebar</aside>
        <footer role="contentinfo">Footer</footer>
      `;

      if (axe) {
        axe.run(document.body, function(err, results) {
          if (err) {
            done.fail(err);
            return;
          }
          
          const violations = results.violations.filter(v => 
            v.id === 'landmark-one-main' || v.id === 'region'
          );
          expect(violations.length).toBe(0);
          done();
        });
      } else {
        done();
      }
    });
  });
});

