'use client'

import React, { useState } from 'react';
import { useApp, appActions } from '../context/AppContext';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { state, dispatch } = useApp();
  const { activeTab } = state;

  return (
    <header className="header">
      <div className="header-container">
        <div className="logo-section left">
          <h1 className="nexteleven-logo">NextEleven</h1>
        </div>
        
        <div className="logo-section centered">
          <h1 className="app-subtitle">Professional Tattoo AI</h1>
        </div>
        
        <div className="hamburger-menu" onClick={() => setIsMenuOpen(!isMenuOpen)}>
          <div className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></div>
          <div className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></div>
          <div className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></div>
        </div>
      </div>
      
      {isMenuOpen && (
        <div className="mobile-menu">
          <nav className="nav">
            <ul>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'chat' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('chat'));
                    setIsMenuOpen(false);
                  }}
                >
                  AI Chat
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'features' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('features'));
                    setIsMenuOpen(false);
                  }}
                >
                  Features
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'appointments' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('appointments'));
                    setIsMenuOpen(false);
                  }}
                >
                  Book Appointment
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'analytics' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('analytics'));
                    setIsMenuOpen(false);
                  }}
                >
                  Analytics
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'pipelines' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('pipelines'));
                    setIsMenuOpen(false);
                  }}
                >
                  Pipelines
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'information' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('information'));
                    setIsMenuOpen(false);
                  }}
                >
                  Information
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'about' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('about'));
                    setIsMenuOpen(false);
                  }}
                >
                  About
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'services' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('services'));
                    setIsMenuOpen(false);
                  }}
                >
                  Services
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'gallery' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('gallery'));
                    setIsMenuOpen(false);
                  }}
                >
                  Gallery
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'contact' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('contact'));
                    setIsMenuOpen(false);
                  }}
                >
                  Contact
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'pricing' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('pricing'));
                    setIsMenuOpen(false);
                  }}
                >
                  Pricing
                </button>
              </li>
              <li>
                <button 
                  className={`nav-link ${activeTab === 'artists' ? 'active' : ''}`}
                  onClick={() => {
                    dispatch(appActions.setActiveTab('artists'));
                    setIsMenuOpen(false);
                  }}
                >
                  Artists
                </button>
              </li>
            </ul>
          </nav>
        </div>
      )}
    </header>
  );
}