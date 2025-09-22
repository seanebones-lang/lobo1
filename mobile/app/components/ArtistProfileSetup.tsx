'use client'

import React, { useState, useEffect } from 'react';
import { useArtistProfile } from '../lib/artist-profile-manager';
import { 
  User, 
  Store, 
  Palette, 
  Phone, 
  Mail, 
  Instagram, 
  Facebook, 
  Twitter,
  Camera,
  Video,
  Clock,
  DollarSign,
  MessageCircle,
  Settings,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface ArtistProfileSetupProps {
  isOpen?: boolean;
  onClose?: () => void;
  onComplete?: () => void;
  onSkip?: () => void;
}

export default function ArtistProfileSetup({ isOpen = true, onClose, onComplete, onSkip }: ArtistProfileSetupProps) {
  const { profile, completion, updateProfile, addPortfolioItem, updateAvailability, updatePricing, updateCustomizations } = useArtistProfile();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    shopName: '',
    bio: '',
    process: [] as string[],
    specialties: [] as string[],
    experience: 0,
    contact: {
      email: '',
      phone: '',
      website: '',
      address: ''
    },
    socialMedia: {
      instagram: '',
      facebook: '',
      twitter: '',
      tiktok: '',
      youtube: ''
    },
    pricing: {
      hourlyRate: 0,
      minimumCharge: 0,
      consultationFee: 0
    },
    customizations: {
      chatbotPersonality: 'professional' as 'professional' | 'friendly' | 'artistic' | 'casual',
      welcomeMessage: 'Welcome to my tattoo studio! How can I help you today?',
      colorScheme: 'default',
      customQuestions: [] as string[]
    }
  });

  const steps = [
    { id: 1, title: 'Basic Info', icon: <User className="w-5 h-5" /> },
    { id: 2, title: 'Shop Details', icon: <Store className="w-5 h-5" /> },
    { id: 3, title: 'Contact & Social', icon: <Phone className="w-5 h-5" /> },
    { id: 4, title: 'Pricing', icon: <DollarSign className="w-5 h-5" /> },
    { id: 5, title: 'Chatbot Setup', icon: <MessageCircle className="w-5 h-5" /> }
  ];

  const processOptions = [
    'Traditional Tattooing',
    'Realistic Tattooing',
    'Blackwork',
    'Watercolor',
    'Geometric',
    'Minimalist',
    'Portrait',
    'Japanese',
    'Tribal',
    'Dotwork'
  ];

  const specialtyOptions = [
    'Small Tattoos',
    'Large Pieces',
    'Cover-ups',
    'Touch-ups',
    'Color Work',
    'Black & Grey',
    'Line Work',
    'Shading',
    'Lettering',
    'Custom Designs'
  ];

  const personalityOptions = [
    { value: 'professional', label: 'Professional', description: 'Formal and business-focused' },
    { value: 'friendly', label: 'Friendly', description: 'Warm and approachable' },
    { value: 'artistic', label: 'Artistic', description: 'Creative and expressive' },
    { value: 'casual', label: 'Casual', description: 'Relaxed and informal' }
  ];

  useEffect(() => {
    if (profile) {
      setFormData({
        shopName: profile.shopName || '',
        bio: profile.bio || '',
        process: profile.process || [],
        specialties: profile.specialties || [],
        experience: profile.experience || 0,
        contact: {
          email: profile.contact.email || '',
          phone: profile.contact.phone || '',
          website: profile.contact.website || '',
          address: profile.contact.address || ''
        },
        socialMedia: {
          instagram: profile.socialMedia.instagram || '',
          facebook: profile.socialMedia.facebook || '',
          twitter: profile.socialMedia.twitter || '',
          tiktok: profile.socialMedia.tiktok || '',
          youtube: profile.socialMedia.youtube || ''
        },
        pricing: {
          hourlyRate: profile.pricing.hourlyRate || 0,
          minimumCharge: profile.pricing.minimumCharge || 0,
          consultationFee: profile.pricing.consultationFee || 0
        },
        customizations: {
          chatbotPersonality: profile.customizations.chatbotPersonality || 'professional',
          welcomeMessage: profile.customizations.welcomeMessage || '',
          colorScheme: profile.customizations.colorScheme || 'default',
          customQuestions: profile.customizations.customQuestions || []
        }
      });
    }
  }, [profile]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNestedInputChange = (field: string, subField: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: {
        ...(prev[field as keyof typeof prev] as any),
        [subField]: value
      }
    }));
  };

  const handleArrayToggle = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field as keyof typeof prev] as string[]).includes(value)
        ? (prev[field as keyof typeof prev] as string[]).filter(item => item !== value)
        : [...(prev[field as keyof typeof prev] as string[]), value]
    }));
  };

  const handleNext = async () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    } else {
      await handleSave();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateProfile(formData);
      onComplete?.();
    } catch (error) {
      console.error('Failed to save profile:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Shop Name *
              </label>
              <input
                type="text"
                value={formData.shopName}
                onChange={(e) => handleInputChange('shopName', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your shop name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Bio *
              </label>
              <textarea
                value={formData.bio}
                onChange={(e) => handleInputChange('bio', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={4}
                placeholder="Tell us about yourself and your tattooing style..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Years of Experience
              </label>
              <input
                type="number"
                value={formData.experience}
                onChange={(e) => handleInputChange('experience', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0"
                min="0"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Tattooing Processes *
              </label>
              <div className="grid grid-cols-2 gap-2">
                {processOptions.map((process) => (
                  <label key={process} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.process.includes(process)}
                      onChange={() => handleArrayToggle('process', process)}
                      className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-300">{process}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Specialties *
              </label>
              <div className="grid grid-cols-2 gap-2">
                {specialtyOptions.map((specialty) => (
                  <label key={specialty} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.specialties.includes(specialty)}
                      onChange={() => handleArrayToggle('specialties', specialty)}
                      className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-300">{specialty}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  value={formData.contact.email}
                  onChange={(e) => handleNestedInputChange('contact', 'email', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="your@email.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Phone *
                </label>
                <input
                  type="tel"
                  value={formData.contact.phone}
                  onChange={(e) => handleNestedInputChange('contact', 'phone', e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="(555) 123-4567"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Website
              </label>
              <input
                type="url"
                value={formData.contact.website}
                onChange={(e) => handleNestedInputChange('contact', 'website', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://yourwebsite.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Address
              </label>
              <textarea
                value={formData.contact.address}
                onChange={(e) => handleNestedInputChange('contact', 'address', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={2}
                placeholder="123 Main St, City, State 12345"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Social Media Links
              </label>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Instagram className="w-5 h-5 text-pink-500" />
                  <input
                    type="url"
                    value={formData.socialMedia.instagram}
                    onChange={(e) => handleNestedInputChange('socialMedia', 'instagram', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="https://instagram.com/yourhandle"
                  />
                </div>

                <div className="flex items-center space-x-3">
                  <Facebook className="w-5 h-5 text-blue-500" />
                  <input
                    type="url"
                    value={formData.socialMedia.facebook}
                    onChange={(e) => handleNestedInputChange('socialMedia', 'facebook', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="https://facebook.com/yourpage"
                  />
                </div>

                <div className="flex items-center space-x-3">
                  <Twitter className="w-5 h-5 text-blue-400" />
                  <input
                    type="url"
                    value={formData.socialMedia.twitter}
                    onChange={(e) => handleNestedInputChange('socialMedia', 'twitter', e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="https://twitter.com/yourhandle"
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Hourly Rate ($)
                </label>
                <input
                  type="number"
                  value={formData.pricing.hourlyRate}
                  onChange={(e) => handleNestedInputChange('pricing', 'hourlyRate', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="150"
                  min="0"
                  step="0.01"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Minimum Charge ($)
                </label>
                <input
                  type="number"
                  value={formData.pricing.minimumCharge}
                  onChange={(e) => handleNestedInputChange('pricing', 'minimumCharge', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="80"
                  min="0"
                  step="0.01"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Consultation Fee ($)
                </label>
                <input
                  type="number"
                  value={formData.pricing.consultationFee}
                  onChange={(e) => handleNestedInputChange('pricing', 'consultationFee', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="25"
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Chatbot Personality
              </label>
              <div className="space-y-3">
                {personalityOptions.map((option) => (
                  <label key={option.value} className="flex items-start space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      name="personality"
                      value={option.value}
                      checked={formData.customizations.chatbotPersonality === option.value}
                      onChange={(e) => handleNestedInputChange('customizations', 'chatbotPersonality', e.target.value)}
                      className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500 mt-1"
                    />
                    <div>
                      <div className="text-sm font-medium text-white">{option.label}</div>
                      <div className="text-xs text-gray-400">{option.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Welcome Message
              </label>
              <textarea
                value={formData.customizations.welcomeMessage}
                onChange={(e) => handleNestedInputChange('customizations', 'welcomeMessage', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="Welcome to my tattoo studio! How can I help you today?"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Custom Questions (Optional)
              </label>
              <textarea
                value={formData.customizations.customQuestions.join('\n')}
                onChange={(e) => handleNestedInputChange('customizations', 'customQuestions', e.target.value.split('\n').filter(q => q.trim()))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="What's your favorite tattoo style?\nDo you have any allergies?\nWhat's your budget range?"
              />
              <p className="text-xs text-gray-400 mt-1">Enter one question per line</p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="artist-profile-setup">
      <div className="bg-gray-900 rounded-2xl p-6 max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-white mb-2">Set Up Your Artist Profile</h2>
          <p className="text-gray-400">Complete your profile to customize your chatbot</p>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-400 mb-2">
              <span>Step {currentStep} of {steps.length}</span>
              <span>{completion}% Complete</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / steps.length) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Step Navigation */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-4">
            {steps.map((step) => (
              <div
                key={step.id}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${
                  currentStep === step.id
                    ? 'bg-blue-600 text-white'
                    : currentStep > step.id
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-700 text-gray-400'
                }`}
              >
                {currentStep > step.id ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  step.icon
                )}
                <span className="text-sm font-medium">{step.title}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="mb-8">
          {renderStepContent()}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="px-4 py-2 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>

          <div className="flex space-x-3">
            {onSkip && (
              <button
                onClick={onSkip}
                className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
              >
                Skip for Now
              </button>
            )}

            <button
              onClick={handleNext}
              disabled={isSaving}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSaving ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </div>
              ) : currentStep === steps.length ? (
                'Complete Setup'
              ) : (
                'Next'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
