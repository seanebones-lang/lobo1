'use client'

import React, { useState, useEffect } from 'react';
import { useArtistProfile } from '../lib/artist-profile-manager';
import { 
  Play, 
  Pause, 
  SkipForward, 
  SkipBack, 
  CheckCircle, 
  Lightbulb, 
  Share2, 
  Code,
  MessageSquare,
  Settings,
  Palette,
  Users,
  BarChart3
} from 'lucide-react';

interface TourStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  action?: string;
  target?: string;
}

interface BotTourProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function BotTour({ isOpen, onClose }: BotTourProps) {
  const { profile, generateChatbotConfig } = useArtistProfile();
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());

  const tourSteps: TourStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to Your AI Tattoo Assistant',
      description: 'Your personalized chatbot is ready to help customers learn about your services, book appointments, and get pricing information.',
      icon: <MessageSquare className="w-8 h-8 text-blue-500" />
    },
    {
      id: 'customization',
      title: 'Customize Your Bot',
      description: 'Set your shop name, specialties, pricing, and personality to make the bot uniquely yours.',
      icon: <Settings className="w-8 h-8 text-purple-500" />,
      action: 'Customize Bot'
    },
    {
      id: 'branding',
      title: 'Brand Your Experience',
      description: 'Choose colors, add your logo, and set a welcome message that reflects your style.',
      icon: <Palette className="w-8 h-8 text-pink-500" />,
      action: 'Brand Settings'
    },
    {
      id: 'social',
      title: 'Social Media Integration',
      description: 'Connect your Instagram, Facebook, and other social accounts for seamless sharing.',
      icon: <Share2 className="w-8 h-8 text-green-500" />,
      action: 'Connect Social'
    },
    {
      id: 'analytics',
      title: 'Track Performance',
      description: 'Monitor conversations, popular questions, and customer engagement with detailed analytics.',
      icon: <BarChart3 className="w-8 h-8 text-orange-500" />,
      action: 'View Analytics'
    },
    {
      id: 'embed',
      title: 'Embed Everywhere',
      description: 'Add your bot to your website, social media, or share the direct link with customers.',
      icon: <Code className="w-8 h-8 text-cyan-500" />,
      action: 'Get Embed Code'
    }
  ];

  const tips = [
    {
      title: 'Keep Your Bio Updated',
      description: 'Regularly update your bio and specialties to ensure customers get accurate information.',
      category: 'Profile'
    },
    {
      title: 'Use Clear Pricing',
      description: 'Set clear hourly rates and minimum charges to avoid confusion during consultations.',
      category: 'Pricing'
    },
    {
      title: 'Test Your Bot',
      description: 'Try different questions to see how your bot responds and adjust the personality if needed.',
      category: 'Testing'
    },
    {
      title: 'Monitor Analytics',
      description: 'Check which questions are asked most often and add them to your custom Q&A section.',
      category: 'Analytics'
    },
    {
      title: 'Share on Social Media',
      description: 'Post about your AI assistant on social media to let customers know they can chat with you 24/7.',
      category: 'Marketing'
    },
    {
      title: 'Update Availability',
      description: 'Keep your availability updated so customers can book appointments at the right times.',
      category: 'Scheduling'
    }
  ];

  useEffect(() => {
    if (isOpen) {
      setCurrentStep(0);
      setIsPlaying(false);
    }
  }, [isOpen]);

  const handleNext = () => {
    if (currentStep < tourSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onClose();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    onClose();
  };

  const handleStepAction = (action: string) => {
    // Mark step as completed
    setCompletedSteps(prev => new Set([...Array.from(prev), tourSteps[currentStep].id]));
    
    // Handle specific actions
    switch (action) {
      case 'Customize Bot':
        // Navigate to profile setup
        break;
      case 'Brand Settings':
        // Navigate to branding settings
        break;
      case 'Connect Social':
        // Navigate to social media settings
        break;
      case 'View Analytics':
        // Navigate to analytics
        break;
      case 'Get Embed Code':
        // Show embed code modal
        break;
    }
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const generateEmbedCode = () => {
    const config = generateChatbotConfig();
    if (!config) return '';

    return `
<!-- NextEleven Tattoo AI Chatbot -->
<div id="nexteleven-chatbot" 
     data-shop-name="${config.shopName}"
     data-personality="${config.personality}"
     data-color-scheme="${config.colorScheme}"
     data-welcome-message="${config.welcomeMessage}">
</div>
<script src="https://nexteleven.ai/chatbot.js"></script>
    `.trim();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <Play className="w-6 h-6 text-blue-500" />
            <h2 className="text-xl font-bold text-white">Bot Tour & Tips</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ×
          </button>
        </div>

        {/* Tour Steps */}
        <div className="p-6">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Tour Steps</h3>
              <div className="flex items-center gap-2">
                <button
                  onClick={handlePlayPause}
                  className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
                <span className="text-sm text-gray-400">
                  {currentStep + 1} of {tourSteps.length}
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-700 rounded-full h-2 mb-6">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / tourSteps.length) * 100}%` }}
              ></div>
            </div>

            {/* Current Step */}
            <div className="bg-gray-800 rounded-lg p-6 mb-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  {tourSteps[currentStep].icon}
                </div>
                <div className="flex-1">
                  <h4 className="text-lg font-semibold text-white mb-2">
                    {tourSteps[currentStep].title}
                  </h4>
                  <p className="text-gray-300 mb-4">
                    {tourSteps[currentStep].description}
                  </p>
                  {tourSteps[currentStep].action && (
                    <button
                      onClick={() => handleStepAction(tourSteps[currentStep].action!)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      {tourSteps[currentStep].action}
                    </button>
                  )}
                </div>
                {completedSteps.has(tourSteps[currentStep].id) && (
                  <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                )}
              </div>
            </div>

            {/* Navigation */}
            <div className="flex justify-between">
              <button
                onClick={handlePrevious}
                disabled={currentStep === 0}
                className="px-4 py-2 text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>

              <div className="flex gap-2">
                <button
                  onClick={handleSkip}
                  className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                >
                  Skip Tour
                </button>
                <button
                  onClick={handleNext}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {currentStep === tourSteps.length - 1 ? 'Finish' : 'Next'}
                </button>
              </div>
            </div>
          </div>

          {/* Tips Section */}
          <div className="border-t border-gray-700 pt-6">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="w-5 h-5 text-yellow-500" />
              <h3 className="text-lg font-semibold text-white">Tips & Tricks</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {tips.map((tip, index) => (
                <div key={index} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-white">{tip.title}</h4>
                        <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">
                          {tip.category}
                        </span>
                      </div>
                      <p className="text-sm text-gray-300">{tip.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Embed Code Section */}
          <div className="border-t border-gray-700 pt-6 mt-6">
            <div className="flex items-center gap-2 mb-4">
              <Code className="w-5 h-5 text-cyan-500" />
              <h3 className="text-lg font-semibold text-white">Embed Your Bot</h3>
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <p className="text-sm text-gray-300 mb-3">
                Copy this code to embed your chatbot on your website:
              </p>
              <pre className="bg-gray-900 rounded p-3 text-xs text-gray-300 overflow-x-auto">
                <code>{generateEmbedCode()}</code>
              </pre>
              <button
                onClick={() => navigator.clipboard.writeText(generateEmbedCode())}
                className="mt-3 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors text-sm"
              >
                Copy Embed Code
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
