'use client'

import React from 'react';
import { 
  Palette, 
  MessageCircle, 
  Zap,
  Sparkles,
  Award,
  Star,
  ArrowRight,
  Grid3X3,
  Settings,
  Users,
  Bot,
  BarChart3,
  Code
} from 'lucide-react';

// APOLLO-APPROVED Interface Selector with Two-Panel Design
export default function InterfacesPage() {
  const handleArtistClick = () => {
    // Navigate to artist interface
    window.location.href = '/interfaces/artist';
  };

  const handleClientClick = () => {
    // Navigate to client interface
    window.location.href = '/interfaces/client';
  };

  return (
    <div className="interfaces-page">
      {/* APOLLO-APPROVED Header */}
      <div className="interfaces-header">
        <h1>APOLLO Interface Suite</h1>
        <p>Professional Artist & Client Interfaces with 10/10 Quality Standard</p>
      </div>

      {/* APOLLO-APPROVED Two-Panel Layout */}
      <div className="interfaces-panels">
        {/* Artist Interface Panel */}
        <div className="interface-panel artist-panel" onClick={handleArtistClick}>
          <div className="interface-panel-icon">
            <Palette />
          </div>
          <h2>Artist Interface</h2>
          <p>Professional dashboard with customizable grid system, portfolio management, and real-time analytics for tattoo artists.</p>
          
          <ul className="interface-features">
            <li>Customizable color themes</li>
            <li>Dynamic grid system (1-6 columns)</li>
            <li>Portfolio management</li>
            <li>Real-time revenue tracking</li>
            <li>Typography controls</li>
            <li>Mobile responsive design</li>
          </ul>
          
          <button className="interface-button">
            <ArrowRight />
            Access Artist Interface
          </button>
        </div>

        {/* Client Interface Panel */}
        <div className="interface-panel client-panel" onClick={handleClientClick}>
          <div className="interface-panel-icon">
            <MessageCircle />
          </div>
          <h2>Client Interface</h2>
          <p>Text-based conversational UI with voice recognition and AI-powered responses for seamless customer interactions.</p>
          
          <ul className="interface-features">
            <li>Voice recognition support</li>
            <li>Natural language processing</li>
            <li>Quick action buttons</li>
            <li>Message history tracking</li>
            <li>Attachment support</li>
            <li>Real-time typing indicators</li>
          </ul>
          
          <button className="interface-button">
            <ArrowRight />
            Access Client Interface
          </button>
        </div>
      </div>

      {/* APOLLO Quality Features */}
      <div className="mt-12 text-center">
        <h3 className="text-2xl font-bold text-white mb-8">APOLLO Quality Features</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-800px mx-auto">
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <span className="text-sm text-gray-300">Real-time Processing</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-sm text-gray-300">AI-Powered</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
              <Award className="w-6 h-6 text-white" />
            </div>
            <span className="text-sm text-gray-300">10/10 Quality</span>
          </div>
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 bg-orange-500 rounded-lg flex items-center justify-center">
              <Star className="w-6 h-6 text-white" />
            </div>
            <span className="text-sm text-gray-300">Premium Features</span>
          </div>
        </div>
      </div>
    </div>
  );
}
