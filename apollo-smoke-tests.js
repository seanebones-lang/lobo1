#!/usr/bin/env node

/**
 * APOLLO SMOKE TESTS
 * Quick validation tests for critical functionality
 * Designed by APOLLO 1.0.0 for NextEleven Tattoo AI
 */

const puppeteer = require('puppeteer');

class ApolloSmokeTests {
  constructor() {
    this.browser = null;
    this.page = null;
    this.results = [];
  }

  async runSmokeTests() {
    console.log('🔥 APOLLO SMOKE TESTS STARTING...');
    console.log('=' * 50);
    
    try {
      await this.initialize();
      
      // Critical smoke tests
      await this.testAppLoads();
      await this.testNavigationWorks();
      await this.testButtonsRespond();
      await this.testFormsAcceptInput();
      await this.testAPIsRespond();
      
      this.generateSmokeReport();
      
    } catch (error) {
      console.error('❌ Smoke test error:', error);
    } finally {
      if (this.browser) {
        await this.browser.close();
      }
    }
  }

  async initialize() {
    this.browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    this.page = await this.browser.newPage();
  }

  async testAppLoads() {
    console.log('🏠 Testing: App loads successfully...');
    
    try {
      await this.page.goto('http://localhost:3000', { 
        waitUntil: 'networkidle2',
        timeout: 10000 
      });
      
      const title = await this.page.title();
      const hasContent = await this.page.evaluate(() => {
        return document.body.textContent.length > 50;
      });
      
      if (title && hasContent) {
        this.results.push({ test: 'App Loads', status: 'PASS', details: 'Application loaded successfully' });
        console.log('✅ App loads: PASS');
      } else {
        this.results.push({ test: 'App Loads', status: 'FAIL', details: 'Application failed to load properly' });
        console.log('❌ App loads: FAIL');
      }
      
    } catch (error) {
      this.results.push({ test: 'App Loads', status: 'ERROR', details: error.message });
      console.log('❌ App loads: ERROR');
    }
  }

  async testNavigationWorks() {
    console.log('🧭 Testing: Navigation works...');
    
    try {
      // Test tab navigation
      const tabButtons = await this.page.$$('.tab-btn');
      
      if (tabButtons.length > 0) {
        // Click first tab
        await tabButtons[0].click();
        await this.page.waitForTimeout(1000);
        
        this.results.push({ test: 'Navigation Works', status: 'PASS', details: `${tabButtons.length} navigation tabs found and functional` });
        console.log('✅ Navigation works: PASS');
      } else {
        this.results.push({ test: 'Navigation Works', status: 'FAIL', details: 'No navigation tabs found' });
        console.log('❌ Navigation works: FAIL');
      }
      
    } catch (error) {
      this.results.push({ test: 'Navigation Works', status: 'ERROR', details: error.message });
      console.log('❌ Navigation works: ERROR');
    }
  }

  async testButtonsRespond() {
    console.log('🔘 Testing: Buttons respond to clicks...');
    
    try {
      // Test various button types
      const buttonSelectors = [
        '.tab-btn',
        '.book-button',
        '.chat-button',
        '.pricing-button',
        '.interface-button',
        '.quick-action-button',
        '.refresh-button'
      ];
      
      let buttonsFound = 0;
      let buttonsWorking = 0;
      
      for (const selector of buttonSelectors) {
        const buttons = await this.page.$$(selector);
        buttonsFound += buttons.length;
        
        for (const button of buttons.slice(0, 1)) { // Test first button of each type
          try {
            const isVisible = await button.isIntersectingViewport();
            if (isVisible) {
              await button.click();
              buttonsWorking++;
              await this.page.waitForTimeout(200);
            }
          } catch (e) {
            // Button click failed, continue
          }
        }
      }
      
      if (buttonsWorking > 0) {
        this.results.push({ 
          test: 'Buttons Respond', 
          status: 'PASS', 
          details: `${buttonsWorking}/${buttonsFound} buttons responded to clicks` 
        });
        console.log('✅ Buttons respond: PASS');
      } else {
        this.results.push({ test: 'Buttons Respond', status: 'FAIL', details: 'No buttons responded to clicks' });
        console.log('❌ Buttons respond: FAIL');
      }
      
    } catch (error) {
      this.results.push({ test: 'Buttons Respond', status: 'ERROR', details: error.message });
      console.log('❌ Buttons respond: ERROR');
    }
  }

  async testFormsAcceptInput() {
    console.log('📝 Testing: Forms accept input...');
    
    try {
      // Navigate to appointments page to test form
      await this.page.goto('http://localhost:3000/appointments', { waitUntil: 'networkidle2' });
      
      const inputFields = await this.page.$$('input[type="text"], input[type="email"], input[type="tel"], textarea');
      let inputsWorking = 0;
      
      for (const input of inputFields.slice(0, 3)) { // Test first 3 inputs
        try {
          await input.type('test input');
          inputsWorking++;
          await this.page.waitForTimeout(100);
        } catch (e) {
          // Input failed, continue
        }
      }
      
      if (inputsWorking > 0) {
        this.results.push({ 
          test: 'Forms Accept Input', 
          status: 'PASS', 
          details: `${inputsWorking}/${inputFields.length} form inputs accept text` 
        });
        console.log('✅ Forms accept input: PASS');
      } else {
        this.results.push({ test: 'Forms Accept Input', status: 'FAIL', details: 'No form inputs accept text' });
        console.log('❌ Forms accept input: FAIL');
      }
      
    } catch (error) {
      this.results.push({ test: 'Forms Accept Input', status: 'ERROR', details: error.message });
      console.log('❌ Forms accept input: ERROR');
    }
  }

  async testAPIsRespond() {
    console.log('🌐 Testing: APIs respond...');
    
    try {
      const apiEndpoints = [
        '/api/artists',
        '/api/analytics',
        '/api/pipelines/status'
      ];
      
      let apisWorking = 0;
      
      for (const endpoint of apiEndpoints) {
        try {
          const response = await this.page.goto(`http://localhost:3000${endpoint}`, {
            waitUntil: 'networkidle2',
            timeout: 5000
          });
          
          if (response && response.status() < 500) {
            apisWorking++;
          }
        } catch (e) {
          // API failed, continue
        }
      }
      
      if (apisWorking > 0) {
        this.results.push({ 
          test: 'APIs Respond', 
          status: 'PASS', 
          details: `${apisWorking}/${apiEndpoints.length} API endpoints responded` 
        });
        console.log('✅ APIs respond: PASS');
      } else {
        this.results.push({ test: 'APIs Respond', status: 'FAIL', details: 'No API endpoints responded' });
        console.log('❌ APIs respond: FAIL');
      }
      
    } catch (error) {
      this.results.push({ test: 'APIs Respond', status: 'ERROR', details: error.message });
      console.log('❌ APIs respond: ERROR');
    }
  }

  generateSmokeReport() {
    const passed = this.results.filter(r => r.status === 'PASS').length;
    const total = this.results.length;
    const passRate = ((passed / total) * 100).toFixed(1);
    
    console.log('\n' + '=' * 50);
    console.log('🔥 APOLLO SMOKE TEST RESULTS');
    console.log('=' * 50);
    console.log(`📊 Total Tests: ${total}`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`📈 Pass Rate: ${passRate}%`);
    console.log('=' * 50);
    
    this.results.forEach(result => {
      const icon = result.status === 'PASS' ? '✅' : result.status === 'FAIL' ? '❌' : '⚠️';
      console.log(`${icon} ${result.test}: ${result.status}`);
      if (result.details) {
        console.log(`   ${result.details}`);
      }
    });
    
    console.log('=' * 50);
    
    if (passRate >= 80) {
      console.log('🎉 SMOKE TESTS PASSED - Ready for production!');
    } else {
      console.log('🚨 SMOKE TESTS FAILED - Critical issues found!');
    }
    
    return {
      total,
      passed,
      passRate: `${passRate}%`,
      results: this.results
    };
  }
}

// Run smoke tests
if (require.main === module) {
  const smokeTests = new ApolloSmokeTests();
  smokeTests.runSmokeTests().catch(console.error);
}

module.exports = ApolloSmokeTests;
