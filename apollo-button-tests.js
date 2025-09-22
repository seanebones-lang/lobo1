#!/usr/bin/env node

/**
 * APOLLO BUTTON TESTS
 * Comprehensive testing for every button and interactive element
 * Designed by APOLLO 1.0.0 for NextEleven Tattoo AI
 */

const puppeteer = require('puppeteer');

class ApolloButtonTests {
  constructor() {
    this.browser = null;
    this.page = null;
    this.buttonTests = [];
    this.results = [];
  }

  async runButtonTests() {
    console.log('🔘 APOLLO BUTTON TESTS STARTING...');
    console.log('=' * 60);
    
    try {
      await this.initialize();
      await this.discoverAllButtons();
      await this.testAllButtons();
      await this.generateButtonReport();
      
    } catch (error) {
      console.error('❌ Button test error:', error);
    } finally {
      if (this.browser) {
        await this.browser.close();
      }
    }
  }

  async initialize() {
    this.browser = await puppeteer.launch({
      headless: false, // Keep visible to see button interactions
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    this.page = await this.browser.newPage();
    
    // Set viewport for consistent testing
    await this.page.setViewport({ width: 1920, height: 1080 });
  }

  async discoverAllButtons() {
    console.log('🔍 Discovering all buttons and interactive elements...');
    
    // Navigate to main page first
    await this.page.goto('http://localhost:3000', { waitUntil: 'networkidle2' });
    await this.page.waitForTimeout(2000);
    
    // Define button selectors to test
    const buttonSelectors = [
      // Navigation buttons
      { selector: '[data-testid="hamburger-menu"]', name: 'Hamburger Menu Toggle', category: 'Navigation' },
      { selector: '.mobile-menu .nav-link', name: 'Mobile Menu Links', category: 'Navigation', multiple: true },
      
      // Tab navigation buttons
      { selector: '.tab-btn[data-tab="chat"]', name: 'Chat Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="features"]', name: 'Features Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="about"]', name: 'About Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="appointments"]', name: 'Appointments Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="artists"]', name: 'Artists Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="analytics"]', name: 'Analytics Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="pipelines"]', name: 'Pipelines Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="information"]', name: 'Information Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="services"]', name: 'Services Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="gallery"]', name: 'Gallery Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="contact"]', name: 'Contact Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="pricing"]', name: 'Pricing Tab Button', category: 'Tab Navigation' },
      { selector: '.tab-btn[data-tab="interfaces"]', name: 'Interfaces Tab Button', category: 'Tab Navigation' },
      
      // Action buttons
      { selector: '.book-button', name: 'Book Appointment Button', category: 'Action Buttons' },
      { selector: '.chat-button', name: 'Chat Submit Button', category: 'Action Buttons' },
      { selector: '.pricing-button', name: 'Pricing Plan Buttons', category: 'Action Buttons', multiple: true },
      { selector: '.interface-button', name: 'Interface Panel Buttons', category: 'Action Buttons', multiple: true },
      { selector: '.quick-action-button', name: 'Quick Action Buttons', category: 'Action Buttons', multiple: true },
      { selector: '.refresh-button', name: 'Refresh Button', category: 'Action Buttons' },
      { selector: '.subscriber-action-button', name: 'Subscriber Action Buttons', category: 'Action Buttons', multiple: true },
      
      // Form buttons
      { selector: '.form-group button', name: 'Form Submit Buttons', category: 'Form Buttons', multiple: true },
      { selector: '.contact-form button', name: 'Contact Form Submit', category: 'Form Buttons' },
      
      // Generic buttons
      { selector: 'button', name: 'Generic Buttons', category: 'Generic Buttons', multiple: true },
      { selector: 'input[type="button"]', name: 'Input Buttons', category: 'Input Buttons', multiple: true },
      { selector: 'input[type="submit"]', name: 'Submit Buttons', category: 'Input Buttons', multiple: true }
    ];
    
    // Discover buttons on different pages
    const pages = [
      { url: '/', name: 'Home Page' },
      { url: '/chat', name: 'Chat Page' },
      { url: '/appointments', name: 'Appointments Page' },
      { url: '/services', name: 'Services Page' },
      { url: '/interfaces', name: 'Interfaces Page' },
      { url: '/contact', name: 'Contact Page' }
    ];
    
    for (const page of pages) {
      console.log(`🔍 Scanning ${page.name}...`);
      
      try {
        await this.page.goto(`http://localhost:3000${page.url}`, { waitUntil: 'networkidle2' });
        await this.page.waitForTimeout(1000);
        
        for (const buttonSpec of buttonSelectors) {
          const buttons = await this.page.$$(buttonSpec.selector);
          
          if (buttons.length > 0) {
            const testLimit = buttonSpec.multiple ? Math.min(buttons.length, 3) : 1;
            
            for (let i = 0; i < testLimit; i++) {
              this.buttonTests.push({
                selector: buttonSpec.selector,
                name: `${buttonSpec.name} #${i + 1}`,
                category: buttonSpec.category,
                page: page.name,
                url: page.url,
                index: i
              });
            }
          }
        }
      } catch (error) {
        console.log(`⚠️  Could not scan ${page.name}: ${error.message}`);
      }
    }
    
    console.log(`✅ Discovered ${this.buttonTests.length} buttons to test`);
  }

  async testAllButtons() {
    console.log('\n🔘 Testing all discovered buttons...');
    
    for (const buttonTest of this.buttonTests) {
      await this.testSingleButton(buttonTest);
    }
  }

  async testSingleButton(buttonTest) {
    try {
      // Navigate to the button's page
      await this.page.goto(`http://localhost:3000${buttonTest.url}`, { waitUntil: 'networkidle2' });
      await this.page.waitForTimeout(1000);
      
      // Find the specific button
      const buttons = await this.page.$$(buttonTest.selector);
      const button = buttons[buttonTest.index];
      
      if (!button) {
        this.results.push({
          ...buttonTest,
          status: 'NOT_FOUND',
          details: 'Button element not found on page',
          timestamp: new Date().toISOString()
        });
        console.log(`❌ ${buttonTest.name}: NOT FOUND`);
        return;
      }
      
      // Check if button is visible
      const isVisible = await button.isIntersectingViewport();
      if (!isVisible) {
        this.results.push({
          ...buttonTest,
          status: 'NOT_VISIBLE',
          details: 'Button is not visible in viewport',
          timestamp: new Date().toISOString()
        });
        console.log(`⚠️  ${buttonTest.name}: NOT VISIBLE`);
        return;
      }
      
      // Check if button is enabled
      const isEnabled = await this.page.evaluate(el => !el.disabled, button);
      if (!isEnabled) {
        this.results.push({
          ...buttonTest,
          status: 'DISABLED',
          details: 'Button is disabled',
          timestamp: new Date().toISOString()
        });
        console.log(`⚠️  ${buttonTest.name}: DISABLED`);
        return;
      }
      
      // Test button click
      const beforeClick = await this.page.evaluate(() => window.location.href);
      await button.click();
      await this.page.waitForTimeout(500);
      
      // Check for any navigation or state change
      const afterClick = await this.page.evaluate(() => window.location.href);
      const hasStateChange = beforeClick !== afterClick;
      
      // Check for any errors in console
      const logs = await this.page.evaluate(() => {
        return window.console._logs || [];
      });
      
      const hasErrors = logs.some(log => log.level === 'error');
      
      if (hasErrors) {
        this.results.push({
          ...buttonTest,
          status: 'ERROR',
          details: 'Button click caused console errors',
          timestamp: new Date().toISOString()
        });
        console.log(`❌ ${buttonTest.name}: ERROR`);
      } else {
        this.results.push({
          ...buttonTest,
          status: 'PASS',
          details: `Button clicked successfully. Navigation: ${hasStateChange}`,
          timestamp: new Date().toISOString()
        });
        console.log(`✅ ${buttonTest.name}: PASS`);
      }
      
    } catch (error) {
      this.results.push({
        ...buttonTest,
        status: 'EXCEPTION',
        details: error.message,
        timestamp: new Date().toISOString()
      });
      console.log(`❌ ${buttonTest.name}: EXCEPTION - ${error.message}`);
    }
  }

  async generateButtonReport() {
    const total = this.results.length;
    const passed = this.results.filter(r => r.status === 'PASS').length;
    const failed = this.results.filter(r => ['ERROR', 'EXCEPTION'].includes(r.status)).length;
    const warnings = this.results.filter(r => ['NOT_VISIBLE', 'DISABLED'].includes(r.status)).length;
    const notFound = this.results.filter(r => r.status === 'NOT_FOUND').length;
    
    const passRate = ((passed / total) * 100).toFixed(1);
    
    console.log('\n' + '=' * 60);
    console.log('🔘 APOLLO BUTTON TEST RESULTS');
    console.log('=' * 60);
    console.log(`📊 Total Buttons Tested: ${total}`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`⚠️  Warnings: ${warnings}`);
    console.log(`🔍 Not Found: ${notFound}`);
    console.log(`📈 Pass Rate: ${passRate}%`);
    console.log('=' * 60);
    
    // Group results by category
    const categories = {};
    this.results.forEach(result => {
      if (!categories[result.category]) {
        categories[result.category] = { total: 0, passed: 0, failed: 0, warnings: 0 };
      }
      categories[result.category].total++;
      if (result.status === 'PASS') categories[result.category].passed++;
      else if (['ERROR', 'EXCEPTION'].includes(result.status)) categories[result.category].failed++;
      else if (['NOT_VISIBLE', 'DISABLED'].includes(result.status)) categories[result.category].warnings++;
    });
    
    console.log('\n📊 RESULTS BY CATEGORY:');
    console.log('-' * 40);
    Object.entries(categories).forEach(([category, stats]) => {
      const categoryPassRate = ((stats.passed / stats.total) * 100).toFixed(1);
      console.log(`${category}: ${stats.passed}/${stats.total} (${categoryPassRate}%)`);
      if (stats.failed > 0) console.log(`  ❌ Failed: ${stats.failed}`);
      if (stats.warnings > 0) console.log(`  ⚠️  Warnings: ${stats.warnings}`);
    });
    
    console.log('\n🔍 DETAILED RESULTS:');
    console.log('-' * 40);
    this.results.forEach(result => {
      const icon = result.status === 'PASS' ? '✅' : 
                   ['ERROR', 'EXCEPTION'].includes(result.status) ? '❌' : 
                   ['NOT_VISIBLE', 'DISABLED'].includes(result.status) ? '⚠️' : '🔍';
      console.log(`${icon} ${result.name} (${result.category})`);
      console.log(`   Status: ${result.status}`);
      console.log(`   Details: ${result.details}`);
      console.log(`   Page: ${result.page}`);
    });
    
    console.log('=' * 60);
    
    if (passRate >= 90) {
      console.log('🎉 EXCELLENT BUTTON TEST RESULTS - All buttons working properly!');
    } else if (passRate >= 80) {
      console.log('✅ GOOD BUTTON TEST RESULTS - Minor issues to address');
    } else if (passRate >= 70) {
      console.log('⚠️  MODERATE BUTTON TEST RESULTS - Several issues need attention');
    } else {
      console.log('🚨 POOR BUTTON TEST RESULTS - Critical issues found!');
    }
    
    // Save detailed report
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        total,
        passed,
        failed,
        warnings,
        notFound,
        passRate: `${passRate}%`
      },
      categories,
      results: this.results
    };
    
    const fs = require('fs');
    const path = require('path');
    const reportPath = path.join(__dirname, 'apollo-button-test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`\n📄 Detailed report saved: ${reportPath}`);
    
    return report;
  }
}

// Run button tests
if (require.main === module) {
  const buttonTests = new ApolloButtonTests();
  buttonTests.runButtonTests().catch(console.error);
}

module.exports = ApolloButtonTests;
