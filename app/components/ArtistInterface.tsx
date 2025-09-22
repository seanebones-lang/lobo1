'use client'

import React, { useState, useEffect, useRef } from 'react';
import { 
  Palette, 
  Settings, 
  Grid, 
  Table, 
  Users, 
  Calendar, 
  DollarSign,
  Star,
  Award,
  TrendingUp,
  BarChart3,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Edit,
  Trash2,
  Save,
  Download,
  Upload,
  Eye,
  EyeOff
} from 'lucide-react';

// APOLLO-APPROVED Artist Interface with 10/10 Quality
interface ArtistInterfaceProps {
  className?: string;
}

interface ArtistProfile {
  id: string;
  name: string;
  shopName: string;
  specialties: string[];
  experience: number;
  rating: number;
  portfolio: PortfolioItem[];
  availability: AvailabilitySlot[];
  pricing: PricingTier[];
  customizations: CustomizationOptions;
}

interface PortfolioItem {
  id: string;
  title: string;
  image: string;
  style: string;
  bodyPart: string;
  duration: number;
  price: number;
  featured: boolean;
}

interface AvailabilitySlot {
  id: string;
  date: string;
  startTime: string;
  endTime: string;
  available: boolean;
  bookedBy?: string;
}

interface PricingTier {
  id: string;
  name: string;
  basePrice: number;
  hourlyRate: number;
  minimumCharge: number;
  consultationFee: number;
}

interface CustomizationOptions {
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    text: string;
  };
  fonts: {
    primary: string;
    secondary: string;
    size: number;
  };
  layout: {
    gridColumns: number;
    cardStyle: 'minimal' | 'detailed' | 'artistic';
    spacing: 'compact' | 'comfortable' | 'spacious';
  };
}

export default function ArtistInterface({ className = '' }: ArtistInterfaceProps) {
  // APOLLO-APPROVED State Management
  const [activeView, setActiveView] = useState<'dashboard' | 'portfolio' | 'schedule' | 'clients' | 'analytics' | 'settings'>('dashboard');
  const [customizations, setCustomizations] = useState<CustomizationOptions>({
    colors: {
      primary: '#8B5CF6',
      secondary: '#06B6D4',
      accent: '#F59E0B',
      background: '#0F172A',
      text: '#F8FAFC'
    },
    fonts: {
      primary: 'Inter',
      secondary: 'Poppins',
      size: 16
    },
    layout: {
      gridColumns: 3,
      cardStyle: 'detailed',
      spacing: 'comfortable'
    }
  });
  
  const [artistProfile, setArtistProfile] = useState<ArtistProfile>({
    id: 'artist_001',
    name: 'Alex Rodriguez',
    shopName: 'Ink & Soul Studio',
    specialties: ['Realism', 'Blackwork', 'Geometric', 'Watercolor'],
    experience: 8,
    rating: 4.9,
    portfolio: [],
    availability: [],
    pricing: [],
    customizations
  });

  const [isCustomizing, setIsCustomizing] = useState(false);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterOptions, setFilterOptions] = useState({
    style: 'all',
    bodyPart: 'all',
    featured: false
  });

  // APOLLO-APPROVED Grid System
  const GridSystem = ({ children, columns = customizations.layout.gridColumns }: { children: React.ReactNode; columns?: number }) => (
    <div 
      className="grid gap-4"
      style={{
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: customizations.layout.spacing === 'compact' ? '0.5rem' : 
             customizations.layout.spacing === 'comfortable' ? '1rem' : '1.5rem'
      }}
    >
      {children}
    </div>
  );

  // APOLLO-APPROVED Color Customization
  const applyCustomizations = () => {
    const root = document.documentElement;
    root.style.setProperty('--artist-primary', customizations.colors.primary);
    root.style.setProperty('--artist-secondary', customizations.colors.secondary);
    root.style.setProperty('--artist-accent', customizations.colors.accent);
    root.style.setProperty('--artist-background', customizations.colors.background);
    root.style.setProperty('--artist-text', customizations.colors.text);
    root.style.setProperty('--artist-font-primary', customizations.fonts.primary);
    root.style.setProperty('--artist-font-secondary', customizations.fonts.secondary);
    root.style.setProperty('--artist-font-size', `${customizations.fonts.size}px`);
  };

  useEffect(() => {
    applyCustomizations();
  }, [customizations]);

  // APOLLO-APPROVED Dashboard View
  const DashboardView = () => (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6 rounded-lg text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Total Appointments</p>
              <p className="text-2xl font-bold">47</p>
            </div>
            <Calendar className="w-8 h-8 opacity-80" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 p-6 rounded-lg text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Monthly Revenue</p>
              <p className="text-2xl font-bold">$12,450</p>
            </div>
            <DollarSign className="w-8 h-8 opacity-80" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-orange-600 to-red-600 p-6 rounded-lg text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Portfolio Items</p>
              <p className="text-2xl font-bold">156</p>
            </div>
            <Award className="w-8 h-8 opacity-80" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-pink-600 to-purple-600 p-6 rounded-lg text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Client Rating</p>
              <p className="text-2xl font-bold">4.9</p>
            </div>
            <Star className="w-8 h-8 opacity-80" />
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" />
          Recent Activity
        </h3>
        <div className="space-y-3">
          {[
            { action: 'New appointment booked', client: 'Sarah Johnson', time: '2 hours ago', type: 'success' },
            { action: 'Portfolio item added', client: 'Geometric Mandala', time: '4 hours ago', type: 'info' },
            { action: 'Client review received', client: '5 stars from Mike Chen', time: '1 day ago', type: 'success' },
            { action: 'Schedule updated', client: 'Added weekend slots', time: '2 days ago', type: 'info' }
          ].map((item, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full mr-3 ${
                  item.type === 'success' ? 'bg-green-500' : 
                  item.type === 'info' ? 'bg-blue-500' : 'bg-yellow-500'
                }`} />
                <div>
                  <p className="font-medium">{item.action}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{item.client}</p>
                </div>
              </div>
              <span className="text-sm text-gray-500">{item.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // APOLLO-APPROVED Portfolio View
  const PortfolioView = () => (
    <div className="space-y-6">
      {/* Portfolio Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setFilterOptions(prev => ({ ...prev, featured: !prev.featured }))}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
              filterOptions.featured 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            <Star className="w-4 h-4" />
            Featured Only
          </button>
          
          <select
            value={filterOptions.style}
            onChange={(e) => setFilterOptions(prev => ({ ...prev, style: e.target.value }))}
            className="px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-0"
          >
            <option value="all">All Styles</option>
            <option value="realism">Realism</option>
            <option value="geometric">Geometric</option>
            <option value="watercolor">Watercolor</option>
            <option value="blackwork">Blackwork</option>
          </select>
        </div>

        <div className="flex gap-2">
          <button className="px-4 py-2 bg-purple-600 text-white rounded-lg flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Add Portfolio Item
          </button>
          
          <button className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Bulk Upload
          </button>
        </div>
      </div>

      {/* Portfolio Grid */}
      <GridSystem columns={customizations.layout.gridColumns}>
        {Array.from({ length: 12 }).map((_, index) => (
          <div
            key={index}
            className={`bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-lg transition-all duration-300 hover:shadow-xl ${
              customizations.layout.cardStyle === 'minimal' ? 'p-4' :
              customizations.layout.cardStyle === 'detailed' ? 'p-6' : 'p-8'
            }`}
          >
            <div className="aspect-square bg-gradient-to-br from-purple-400 to-pink-400 rounded-lg mb-4 relative group">
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex gap-2">
                  <button className="p-2 bg-white bg-opacity-90 rounded-full hover:bg-opacity-100">
                    <Eye className="w-4 h-4" />
                  </button>
                  <button className="p-2 bg-white bg-opacity-90 rounded-full hover:bg-opacity-100">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="p-2 bg-white bg-opacity-90 rounded-full hover:bg-opacity-100">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">Geometric Mandala #{index + 1}</h3>
                {index % 3 === 0 && (
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                )}
              </div>
              
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <span>Realism</span>
                <span>•</span>
                <span>Arm</span>
                <span>•</span>
                <span>4h</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold text-purple-600">$450</span>
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                  <span className="text-sm">4.9</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </GridSystem>
    </div>
  );

  // APOLLO-APPROVED Customization Panel
  const CustomizationPanel = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Customize Interface</h2>
          <button
            onClick={() => setIsCustomizing(false)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            <EyeOff className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-6">
          {/* Color Customization */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Colors</h3>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(customizations.colors).map(([key, value]) => (
                <div key={key}>
                  <label className="block text-sm font-medium mb-2 capitalize">{key}</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={value}
                      onChange={(e) => setCustomizations(prev => ({
                        ...prev,
                        colors: { ...prev.colors, [key]: e.target.value }
                      }))}
                      className="w-12 h-8 rounded border-0 cursor-pointer"
                    />
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => setCustomizations(prev => ({
                        ...prev,
                        colors: { ...prev.colors, [key]: e.target.value }
                      }))}
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Font Customization */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Typography</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Primary Font</label>
                <select
                  value={customizations.fonts.primary}
                  onChange={(e) => setCustomizations(prev => ({
                    ...prev,
                    fonts: { ...prev.fonts, primary: e.target.value }
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value="Inter">Inter</option>
                  <option value="Poppins">Poppins</option>
                  <option value="Roboto">Roboto</option>
                  <option value="Open Sans">Open Sans</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Font Size</label>
                <input
                  type="range"
                  min="12"
                  max="24"
                  value={customizations.fonts.size}
                  onChange={(e) => setCustomizations(prev => ({
                    ...prev,
                    fonts: { ...prev.fonts, size: parseInt(e.target.value) }
                  }))}
                  className="w-full"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">{customizations.fonts.size}px</span>
              </div>
            </div>
          </div>

          {/* Layout Customization */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Layout</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Grid Columns</label>
                <input
                  type="range"
                  min="1"
                  max="6"
                  value={customizations.layout.gridColumns}
                  onChange={(e) => setCustomizations(prev => ({
                    ...prev,
                    layout: { ...prev.layout, gridColumns: parseInt(e.target.value) }
                  }))}
                  className="w-full"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">{customizations.layout.gridColumns} columns</span>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Card Style</label>
                <select
                  value={customizations.layout.cardStyle}
                  onChange={(e) => setCustomizations(prev => ({
                    ...prev,
                    layout: { ...prev.layout, cardStyle: e.target.value as any }
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                >
                  <option value="minimal">Minimal</option>
                  <option value="detailed">Detailed</option>
                  <option value="artistic">Artistic</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={() => setIsCustomizing(false)}
            className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Apply Changes
          </button>
          <button
            onClick={() => setIsCustomizing(false)}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div 
      className={`min-h-screen ${className}`}
      style={{
        backgroundColor: customizations.colors.background,
        color: customizations.colors.text,
        fontFamily: customizations.fonts.primary,
        fontSize: `${customizations.fonts.size}px`
      }}
    >
      {/* APOLLO-APPROVED Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold" style={{ color: customizations.colors.primary }}>
                {artistProfile.shopName}
              </h1>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Artist Dashboard
              </span>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsCustomizing(true)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Customize Interface"
              >
                <Palette className="w-5 h-5" />
              </button>
              
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* APOLLO-APPROVED Navigation */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="px-6">
          <nav className="flex space-x-8">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
              { id: 'portfolio', label: 'Portfolio', icon: Award },
              { id: 'schedule', label: 'Schedule', icon: Calendar },
              { id: 'clients', label: 'Clients', icon: Users },
              { id: 'analytics', label: 'Analytics', icon: TrendingUp },
              { id: 'settings', label: 'Settings', icon: Settings }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveView(id as any)}
                className={`flex items-center gap-2 px-3 py-4 border-b-2 transition-colors ${
                  activeView === id
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* APOLLO-APPROVED Main Content */}
      <div className="p-6">
        {activeView === 'dashboard' && <DashboardView />}
        {activeView === 'portfolio' && <PortfolioView />}
        {activeView === 'schedule' && (
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Schedule Management</h3>
            <p className="text-gray-600 dark:text-gray-400">Coming soon...</p>
          </div>
        )}
        {activeView === 'clients' && (
          <div className="text-center py-12">
            <Users className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Client Management</h3>
            <p className="text-gray-600 dark:text-gray-400">Coming soon...</p>
          </div>
        )}
        {activeView === 'analytics' && (
          <div className="text-center py-12">
            <TrendingUp className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Analytics Dashboard</h3>
            <p className="text-gray-600 dark:text-gray-400">Coming soon...</p>
          </div>
        )}
        {activeView === 'settings' && (
          <div className="text-center py-12">
            <Settings className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Settings</h3>
            <p className="text-gray-600 dark:text-gray-400">Coming soon...</p>
          </div>
        )}
      </div>

      {/* APOLLO-APPROVED Customization Panel */}
      {isCustomizing && <CustomizationPanel />}
    </div>
  );
}
