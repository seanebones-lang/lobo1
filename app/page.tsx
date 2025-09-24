'use client'

import ChatInterface from './components/ChatInterface';
import Features from './components/Features';
import AppointmentBooking from './components/AppointmentBooking';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import PipelineDashboard from './components/PipelineDashboard';
import InformationDashboard from './components/InformationDashboard';
import SubscriberIntegrationDashboard from './components/SubscriberIntegrationDashboard';
import ComponentErrorBoundary from './components/ComponentErrorBoundary';
import { useApp, appActions } from './context/AppContext';
import { Palette, MessageCircle, Zap } from 'lucide-react';

export default function Home() {
  const { state, dispatch } = useApp();
  const { activeTab } = state;

  return (
    <div className="main">

      <div className="tab-content">
                    {activeTab === 'chat' && (
                      <div className="chat-tab-content">
                        <ComponentErrorBoundary componentName="ChatInterface">
                          <ChatInterface />
                        </ComponentErrorBoundary>
                        <ComponentErrorBoundary componentName="Features">
                          <Features />
                        </ComponentErrorBoundary>
                      </div>
                    )}
        
        {activeTab === 'features' && (
          <div>
            <Features />
          </div>
        )}
        
                    {activeTab === 'appointments' && (
                      <div>
                        <ComponentErrorBoundary componentName="AppointmentBooking">
                          <AppointmentBooking />
                        </ComponentErrorBoundary>
                      </div>
                    )}
                    
                    {activeTab === 'analytics' && (
                      <div>
                        <ComponentErrorBoundary componentName="AnalyticsDashboard">
                          <AnalyticsDashboard />
                        </ComponentErrorBoundary>
                      </div>
                    )}
                    
                    {activeTab === 'pipelines' && (
                      <div>
                        <ComponentErrorBoundary componentName="PipelineDashboard">
                          <PipelineDashboard />
                        </ComponentErrorBoundary>
                      </div>
                    )}
                    
                    {activeTab === 'information' && (
                      <div>
                        <ComponentErrorBoundary componentName="InformationDashboard">
                          <InformationDashboard />
                        </ComponentErrorBoundary>
                      </div>
                    )}
                    {activeTab === 'integrations' && (
                      <div>
                        <ComponentErrorBoundary componentName="SubscriberIntegrationDashboard">
                          <SubscriberIntegrationDashboard userId="demo_user_123" />
                        </ComponentErrorBoundary>
                      </div>
                    )}
                    
                    {activeTab === 'interfaces' && (
                      <div className="space-y-6">
                        <div className="text-center py-12">
                          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                            APOLLO Interface Suite
                          </h2>
                          <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
                            Professional Artist & Client Interfaces with 10/10 Quality Standard
                          </p>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                            <a
                              href="/interfaces"
                              className="group bg-gradient-to-r from-purple-500 to-blue-500 p-8 rounded-lg text-white hover:from-purple-600 hover:to-blue-600 transition-all duration-300 transform hover:scale-105"
                            >
                              <div className="text-center">
                                <Palette className="w-16 h-16 mx-auto mb-4 group-hover:scale-110 transition-transform duration-300" />
                                <h3 className="text-2xl font-bold mb-2">Artist Interface</h3>
                                <p className="text-purple-100 mb-4">
                                  Customizable dashboard with grid system, portfolio management, and real-time analytics
                                </p>
                                <div className="flex items-center justify-center gap-2 text-sm">
                                  <span className="bg-white bg-opacity-20 px-2 py-1 rounded">Swift-based</span>
                                  <span className="bg-white bg-opacity-20 px-2 py-1 rounded">Customizable</span>
                                  <span className="bg-white bg-opacity-20 px-2 py-1 rounded">10/10 Quality</span>
                                </div>
                              </div>
                            </a>
                            
                            <a
                              href="/interfaces"
                              className="group bg-gradient-to-r from-blue-500 to-green-500 p-8 rounded-lg text-white hover:from-blue-600 hover:to-green-600 transition-all duration-300 transform hover:scale-105"
                            >
                              <div className="text-center">
                                <MessageCircle className="w-16 h-16 mx-auto mb-4 group-hover:scale-110 transition-transform duration-300" />
                                <h3 className="text-2xl font-bold mb-2">Client Interface</h3>
                                <p className="text-blue-100 mb-4">
                                  Text-based conversational UI with voice recognition and AI-powered responses
                                </p>
                                <div className="flex items-center justify-center gap-2 text-sm">
                                  <span className="bg-white bg-opacity-20 px-2 py-1 rounded">Swift-based</span>
                                  <span className="bg-white bg-opacity-20 px-2 py-1 rounded">Conversational</span>
                                  <span className="bg-white bg-opacity-20 px-2 py-1 rounded">10/10 Quality</span>
                                </div>
                              </div>
                            </a>
                          </div>
                          <div className="mt-8">
                            <a
                              href="/interfaces"
                              className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
                            >
                              <Zap className="w-5 h-5" />
                              View Interface Suite
                            </a>
                          </div>
                        </div>
                      </div>
                    )}
        
        {activeTab === 'about' && (
          <div className="features-container">
            <h2 className="features-header">About NextEleven Tattoo AI</h2>
            <div className="about-content">
              <p className="about-paragraph">
                NextEleven Tattoo AI is a professional-grade artificial intelligence system 
                designed specifically for tattoo shops. Built exclusively with APOLLO 1.0.0 
                software technology, it provides seamless customer interactions while maintaining 
                the highest standards of professionalism.
              </p>
              
              <p className="about-paragraph">
                Our system combines advanced APOLLO AI capabilities with intuitive design, featuring:
              </p>
              
              <ul className="about-list">
                <li>Real-time appointment booking and scheduling</li>
                <li>Dynamic pricing calculations and estimates</li>
                <li>Comprehensive aftercare guidance and documentation</li>
                <li>Secure payment processing and transaction management</li>
                <li>Professional artist portfolio and consultation services</li>
                <li>Advanced analytics and business intelligence</li>
              </ul>
              
              <p>
                Powered exclusively by APOLLO 1.0.0 software, NextEleven Tattoo AI delivers 
                an unparalleled experience that converts visitors into loyal customers while 
                streamlining your business operations.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'services' && (
          <div className="features-container">
            <h2 className="features-header">APOLLO-Powered Services & Pricing</h2>
            <p style={{textAlign: 'center', color: 'rgba(255,255,255,0.8)', marginBottom: '2rem', fontSize: '1.1rem'}}>
              Choose your APOLLO experience level. All plans include core APOLLO 1.0.0 features with premium upgrades available.
            </p>
            
            <div className="services-pricing-container">
              {/* Basic Plan - $9.99 */}
              <div className="pricing-column">
                <div className="pricing-header">
                  <h3 className="pricing-title">Basic Plan</h3>
                  <div className="pricing-price">$9.99</div>
                  <div className="pricing-period">per month</div>
                </div>
                
                <ul className="pricing-features">
                  <li>APOLLO 1.0.0 Core Engine</li>
                  <li>Basic appointment booking</li>
                  <li>Standard customer chat</li>
                  <li>Basic pricing estimates</li>
                  <li>Email notifications</li>
                  <li>Standard aftercare guides</li>
                  <li>Basic analytics dashboard</li>
                  <li>1 artist profile</li>
                </ul>
                
                <button className="pricing-button">Choose Basic</button>
              </div>
              
              {/* Premium Plan - $19.99 */}
              <div className="pricing-column premium">
                <div className="pricing-header">
                  <h3 className="pricing-title">Premium Plan</h3>
                  <div className="pricing-price">$19.99</div>
                  <div className="pricing-period">per month</div>
                </div>
                
                <ul className="pricing-features">
                  <li>APOLLO 1.0.0 Full Suite</li>
                  <li>Advanced appointment booking</li>
                  <li>AI-powered customer chat</li>
                  <li>Dynamic pricing calculations</li>
                  <li>Multi-channel notifications</li>
                  <li>Personalized aftercare plans</li>
                  <li>Advanced analytics & insights</li>
                  <li>Unlimited artist profiles</li>
                  <li>Voice recognition support</li>
                  <li>Priority customer support</li>
                  <li>Custom branding options</li>
                  <li>API access & integrations</li>
                </ul>
                
                <button className="pricing-button">Choose Premium</button>
              </div>
            </div>
            
            {/* A La Carte Features */}
            <div className="ala-carte-section">
              <h3 className="ala-carte-title">Premium Add-Ons</h3>
              <p className="ala-carte-description">
                Enhance your APOLLO experience with these premium features available for micro-transactions
              </p>
              
              <div className="ala-carte-features">
                <div className="ala-carte-item">
                  <div className="ala-carte-item-name">Advanced AI Analytics</div>
                  <div className="ala-carte-item-price">+$4.99/month</div>
                </div>
                <div className="ala-carte-item">
                  <div className="ala-carte-item-name">Custom Branding Suite</div>
                  <div className="ala-carte-item-price">+$7.99/month</div>
                </div>
                <div className="ala-carte-item">
                  <div className="ala-carte-item-name">Multi-Location Support</div>
                  <div className="ala-carte-item-price">+$9.99/month</div>
                </div>
                <div className="ala-carte-item">
                  <div className="ala-carte-item-name">Priority API Access</div>
                  <div className="ala-carte-item-price">+$5.99/month</div>
                </div>
                <div className="ala-carte-item">
                  <div className="ala-carte-item-name">Advanced Security Features</div>
                  <div className="ala-carte-item-price">+$3.99/month</div>
                </div>
                <div className="ala-carte-item">
                  <div className="ala-carte-item-name">White-Label Solution</div>
                  <div className="ala-carte-item-price">+$14.99/month</div>
                </div>
              </div>
              
              <p style={{color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem', fontStyle: 'italic'}}>
                *All add-ons can be activated/deactivated monthly. Pricing determined by APOLLO optimization algorithms.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'gallery' && (
          <div className="features-container">
            <h2 className="features-header">Portfolio Gallery</h2>
            <div className="gallery-grid">
              <div className="gallery-item">
                <div className="gallery-placeholder">
                  <h4>Traditional Tattoos</h4>
                  <p>Classic American traditional style tattoos</p>
                </div>
              </div>
              <div className="gallery-item">
                <div className="gallery-placeholder">
                  <h4>Realistic Tattoos</h4>
                  <p>Photorealistic and detailed artwork</p>
                </div>
              </div>
              <div className="gallery-item">
                <div className="gallery-placeholder">
                  <h4>Blackwork</h4>
                  <p>Bold black ink designs and patterns</p>
                </div>
              </div>
              <div className="gallery-item">
                <div className="gallery-placeholder">
                  <h4>Watercolor</h4>
                  <p>Artistic watercolor-style tattoos</p>
                </div>
              </div>
              <div className="gallery-item">
                <div className="gallery-placeholder">
                  <h4>Geometric</h4>
                  <p>Precise geometric and mandala designs</p>
                </div>
              </div>
              <div className="gallery-item">
                <div className="gallery-placeholder">
                  <h4>Minimalist</h4>
                  <p>Clean, simple, and elegant designs</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'contact' && (
          <div className="features-container">
            <h2 className="features-header">Contact Us</h2>
            <div className="contact-content">
              <div className="contact-info">
                <h3>Get in Touch</h3>
                <div className="contact-item">
                  <strong>Phone:</strong> (555) 123-4567
                </div>
                <div className="contact-item">
                  <strong>Email:</strong> info@nexteleven.com
                </div>
                <div className="contact-item">
                  <strong>Address:</strong> 123 Tattoo Street, Ink City, IC 12345
                </div>
                <div className="contact-item">
                  <strong>Hours:</strong> Mon-Sat: 10AM-8PM, Sun: 12PM-6PM
                </div>
              </div>
              <div className="contact-form">
                <h3>Send us a Message</h3>
                <form>
                  <input type="text" placeholder="Your Name" />
                  <input type="email" placeholder="Your Email" />
                  <input type="text" placeholder="Subject" />
                  <textarea placeholder="Your Message" rows={5}></textarea>
                  <button type="submit">Send Message</button>
                </form>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'pricing' && (
          <div className="features-container">
            <h2 className="features-header">Pricing & Packages</h2>
            <div className="pricing-grid">
              <div className="pricing-card">
                <h3>Basic Consultation</h3>
                <div className="price">$50</div>
                <ul>
                  <li>30-minute consultation</li>
                  <li>Design discussion</li>
                  <li>Basic aftercare info</li>
                </ul>
                <button>Book Now</button>
              </div>
              <div className="pricing-card featured">
                <h3>Full Service Package</h3>
                <div className="price">$200-500</div>
                <ul>
                  <li>Complete design consultation</li>
                  <li>Custom artwork creation</li>
                  <li>Tattoo session</li>
                  <li>Aftercare package</li>
                  <li>Follow-up support</li>
                </ul>
                <button>Book Now</button>
              </div>
              <div className="pricing-card">
                <h3>Premium Experience</h3>
                <div className="price">$500+</div>
                <ul>
                  <li>VIP consultation</li>
                  <li>Master artist session</li>
                  <li>Premium aftercare</li>
                  <li>Photo documentation</li>
                  <li>Lifetime support</li>
                </ul>
                <button>Book Now</button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'artists' && (
          <div className="features-container">
            <h2 className="features-header">Our Artists</h2>
            <div className="artists-grid">
              <div className="artist-card">
                <div className="artist-avatar">A</div>
                <h3>Alex Rivera</h3>
                <p className="artist-specialty">Traditional & Realistic</p>
                <p className="artist-bio">10+ years experience in traditional American and realistic tattoo styles.</p>
                <div className="artist-rating">★★★★★</div>
              </div>
              <div className="artist-card">
                <div className="artist-avatar">M</div>
                <h3>Maya Chen</h3>
                <p className="artist-specialty">Blackwork & Geometric</p>
                <p className="artist-bio">Specialist in bold blackwork and intricate geometric designs.</p>
                <div className="artist-rating">★★★★★</div>
              </div>
              <div className="artist-card">
                <div className="artist-avatar">J</div>
                <h3>Jordan Smith</h3>
                <p className="artist-specialty">Watercolor & Abstract</p>
                <p className="artist-bio">Creative artist specializing in watercolor and abstract tattoo styles.</p>
                <div className="artist-rating">★★★★☆</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
