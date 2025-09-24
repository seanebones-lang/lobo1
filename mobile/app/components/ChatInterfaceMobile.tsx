'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Camera, Image, Phone, MapPin, Calendar, Heart } from 'lucide-react';
import { apolloMobileAI } from '../lib/ai-system-mobile';
import { apolloIOSOptimizer } from '../lib/ios-optimizations';

interface Message {
  id: string;
  content: string;
  type: 'user' | 'assistant';
  timestamp: Date;
  suggestions?: string[];
  metadata?: {
    confidence: number;
    pipeline: string;
    mobileOptimized: boolean;
  };
}

interface ChatInterfaceMobileProps {
  className?: string;
}

export default function ChatInterfaceMobile({ className = '' }: ChatInterfaceMobileProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [deviceCapabilities, setDeviceCapabilities] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Initialize mobile optimizations
    const optimizationReport = apolloIOSOptimizer.getOptimizationReport();
    setDeviceCapabilities(optimizationReport.deviceCapabilities);
    
    // Add welcome message
    setMessages([{
      id: '1',
      content: 'Hi! I\'m APOLLO Mobile - your AI assistant optimized for mobile! I can help with quick booking, pricing, designs, and more. What do you need?',
      type: 'assistant',
      timestamp: new Date(),
      suggestions: ['Book appointment', 'Get pricing', 'See designs', 'Learn about aftercare'],
      metadata: {
        confidence: 0.9,
        pipeline: 'mobile_welcome',
        mobileOptimized: true
      }
    }]);

    // Monitor online status
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      type: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await apolloMobileAI.processQuery(input, {
        conversationHistory: messages,
        userPreferences: {},
        sessionData: {},
        businessRules: {},
        deviceCapabilities: {
          hasLocalAI: deviceCapabilities?.hasANE || false,
          maxMemoryMB: deviceCapabilities?.availableMemory || 2048,
          isOnline,
          batteryLevel: deviceCapabilities?.batteryLevel || 0.5
        }
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        type: 'assistant',
        timestamp: new Date(),
        suggestions: response.suggestions,
        metadata: {
          confidence: response.confidence,
          pipeline: response.pipeline,
          mobileOptimized: response.metadata.mobileOptimized
        }
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error processing query:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        type: 'assistant',
        timestamp: new Date(),
        suggestions: ['Try again', 'Contact support']
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Voice input not supported on this device');
      return;
    }

    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsRecording(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      setIsRecording(false);
    };

    recognition.onerror = () => {
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognition.start();
  };

  const handleQuickAction = (action: string) => {
    const quickActions = {
      'Book appointment': 'I want to book an appointment',
      'Get pricing': 'What are your prices?',
      'See designs': 'Show me some tattoo designs',
      'Learn about aftercare': 'Tell me about tattoo aftercare',
      'Find location': 'Where are you located?',
      'View hours': 'What are your hours?'
    };

    const query = quickActions[action as keyof typeof quickActions] || action;
    setInput(query);
    inputRef.current?.focus();
  };

  return (
    <div className={`flex flex-col h-full bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 ${className}`}>
      {/* Header */}
      <div className="bg-black/20 backdrop-blur-sm border-b border-purple-500/20 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">APOLLO Mobile</h2>
            <p className="text-sm text-purple-300">
              {isOnline ? '🟢 Online' : '🔴 Offline'} • 
              {deviceCapabilities?.hasANE ? ' 🧠 ANE' : ' 💻 CPU'} • 
              {deviceCapabilities?.hasHapticEngine ? ' 📳 Haptic' : ''}
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => handleQuickAction('Book appointment')}
              className="p-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
              title="Book appointment"
              aria-label="Book appointment"
            >
              <Calendar className="w-5 h-5 text-white" />
            </button>
            <button
              onClick={() => handleQuickAction('Find location')}
              className="p-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
              title="Find location"
              aria-label="Find location"
            >
              <MapPin className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-100 border border-purple-500/20'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              {message.metadata && (
                <div className="mt-2 text-xs opacity-70">
                  Confidence: {Math.round(message.metadata.confidence * 100)}% • 
                  Pipeline: {message.metadata.pipeline}
                </div>
              )}
              {message.suggestions && message.suggestions.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {message.suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="text-xs bg-purple-500/20 hover:bg-purple-500/30 px-2 py-1 rounded transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 text-gray-100 border border-purple-500/20 px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-500"></div>
                <span className="text-sm">APOLLO is thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="p-4 border-t border-purple-500/20">
        <div className="grid grid-cols-3 gap-2 mb-4">
          {['Book appointment', 'Get pricing', 'See designs', 'Learn about aftercare', 'Find location', 'View hours'].map((action) => (
            <button
              key={action}
              onClick={() => handleQuickAction(action)}
              className="p-2 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/20 rounded-lg text-sm text-white transition-colors"
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-purple-500/20">
        <form onSubmit={handleSubmit} className="flex items-center space-x-2">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask APOLLO anything about tattoos..."
              className="w-full px-4 py-3 bg-gray-800 border border-purple-500/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
              disabled={isLoading}
            />
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
              <button
                type="button"
                onClick={handleVoiceInput}
                className={`p-1 rounded ${
                  isRecording ? 'bg-red-500' : 'bg-purple-600 hover:bg-purple-700'
                } transition-colors`}
                disabled={isLoading}
                title={isRecording ? 'Stop recording' : 'Start voice input'}
                aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
              >
                {isRecording ? <MicOff className="w-4 h-4 text-white" /> : <Mic className="w-4 h-4 text-white" />}
              </button>
              <button
                type="button"
                className="p-1 bg-purple-600 hover:bg-purple-700 rounded transition-colors"
                disabled={isLoading}
                title="Take photo"
                aria-label="Take photo"
              >
                <Camera className="w-4 h-4 text-white" />
              </button>
            </div>
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded-lg transition-colors"
          >
            <Send className="w-5 h-5 text-white" />
          </button>
        </form>
      </div>
    </div>
  );
}
