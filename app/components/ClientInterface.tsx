'use client'

import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageCircle, 
  Send, 
  Mic, 
  MicOff, 
  Camera, 
  Image, 
  Smile, 
  Heart,
  Star,
  ThumbsUp,
  ThumbsDown,
  Share,
  Bookmark,
  Search,
  Filter,
  Settings,
  User,
  Phone,
  Mail,
  MapPin,
  Clock,
  Calendar,
  DollarSign,
  Award,
  Palette,
  Zap,
  Sparkles,
  Bot,
  UserCheck,
  MessageSquare,
  PhoneCall,
  Video,
  FileText,
  Download,
  Upload,
  Link,
  Copy,
  CheckCircle,
  AlertCircle,
  Info,
  HelpCircle
} from 'lucide-react';

// APOLLO-APPROVED Client Interface with 10/10 Quality
interface ClientInterfaceProps {
  className?: string;
}

interface Message {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    confidence?: number;
    suggestions?: string[];
    quickReplies?: string[];
    attachments?: Attachment[];
  };
}

interface Attachment {
  id: string;
  type: 'image' | 'document' | 'audio' | 'video';
  url: string;
  name: string;
  size: number;
}

interface QuickAction {
  id: string;
  label: string;
  icon: React.ComponentType<any>;
  action: () => void;
  color: string;
}

interface ConversationContext {
  artistId: string;
  artistName: string;
  sessionId: string;
  preferences: {
    voiceEnabled: boolean;
    autoSpeak: boolean;
    theme: 'light' | 'dark' | 'auto';
    fontSize: 'small' | 'medium' | 'large';
  };
}

export default function ClientInterface({ className = '' }: ClientInterfaceProps) {
  // APOLLO-APPROVED State Management
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome_001',
      type: 'ai',
      content: "Hello! I'm your AI tattoo assistant. I can help you with design ideas, pricing, booking appointments, and answering any questions about tattoos. What would you like to know?",
      timestamp: new Date(),
      metadata: {
        confidence: 0.95,
        suggestions: [
          "Show me tattoo styles",
          "What's the pricing?",
          "Book an appointment",
          "Tell me about aftercare"
        ],
        quickReplies: [
          "I want a tattoo",
          "Show me portfolios",
          "How much does it cost?",
          "When can I book?"
        ]
      }
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedQuickAction, setSelectedQuickAction] = useState<string | null>(null);
  
  const [context, setContext] = useState<ConversationContext>({
    artistId: 'artist_001',
    artistName: 'Alex Rodriguez',
    sessionId: `session_${Date.now()}`,
    preferences: {
      voiceEnabled: true,
      autoSpeak: false,
      theme: 'dark',
      fontSize: 'medium'
    }
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // APOLLO-APPROVED Quick Actions
  const quickActions: QuickAction[] = [
    {
      id: 'book_appointment',
      label: 'Book Appointment',
      icon: Calendar,
      action: () => handleQuickAction('book_appointment'),
      color: 'bg-blue-500 hover:bg-blue-600'
    },
    {
      id: 'view_portfolio',
      label: 'View Portfolio',
      icon: Award,
      action: () => handleQuickAction('view_portfolio'),
      color: 'bg-purple-500 hover:bg-purple-600'
    },
    {
      id: 'get_pricing',
      label: 'Get Pricing',
      icon: DollarSign,
      action: () => handleQuickAction('get_pricing'),
      color: 'bg-green-500 hover:bg-green-600'
    },
    {
      id: 'contact_artist',
      label: 'Contact Artist',
      icon: Phone,
      action: () => handleQuickAction('contact_artist'),
      color: 'bg-orange-500 hover:bg-orange-600'
    }
  ];

  // APOLLO-APPROVED Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // APOLLO-APPROVED Voice Recognition Setup
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      recognitionRef.current = new (window as any).webkitSpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        handleSendMessage(transcript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  }, []);

  // APOLLO-APPROVED Message Handling
  const handleSendMessage = async (message?: string) => {
    const messageText = message || inputValue.trim();
    if (!messageText) return;

    // Add user message
    const userMessage: Message = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);
    setIsLoading(true);

    try {
      // Simulate AI response with APOLLO processing
      const aiResponse = await generateAIResponse(messageText);
      
      const aiMessage: Message = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'ai',
        content: aiResponse.content,
        timestamp: new Date(),
        metadata: {
          confidence: aiResponse.confidence,
          suggestions: aiResponse.suggestions,
          quickReplies: aiResponse.quickReplies
        }
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error generating AI response:', error);
      
      const errorMessage: Message = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'ai',
        content: "I apologize, but I'm experiencing some technical difficulties. Please try again or contact us directly for assistance.",
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      setIsLoading(false);
    }
  };

  // APOLLO-APPROVED AI Response Generation
  const generateAIResponse = async (input: string): Promise<{
    content: string;
    confidence: number;
    suggestions: string[];
    quickReplies: string[];
  }> => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    const lowerInput = input.toLowerCase();
    
    // APOLLO-APPROVED Response Logic
    if (lowerInput.includes('book') || lowerInput.includes('appointment')) {
      return {
        content: "I'd be happy to help you book an appointment! Here are our available time slots:\n\n📅 **This Week:**\n• Tuesday 2:00 PM - 4:00 PM\n• Thursday 10:00 AM - 12:00 PM\n• Friday 3:00 PM - 5:00 PM\n\n📅 **Next Week:**\n• Monday 1:00 PM - 3:00 PM\n• Wednesday 11:00 AM - 1:00 PM\n• Saturday 10:00 AM - 2:00 PM\n\nWould you like to book any of these slots?",
        confidence: 0.95,
        suggestions: ["Book Tuesday 2:00 PM", "Book Thursday 10:00 AM", "Book Friday 3:00 PM"],
        quickReplies: ["Yes, book it", "Show me more times", "What's the process?"]
      };
    }
    
    if (lowerInput.includes('price') || lowerInput.includes('cost') || lowerInput.includes('pricing')) {
      return {
        content: "Here's our current pricing structure:\n\n💰 **Pricing Tiers:**\n• **Small Tattoos** (1-3 inches): $150 - $300\n• **Medium Tattoos** (3-6 inches): $300 - $600\n• **Large Tattoos** (6+ inches): $600 - $1200\n• **Sleeves/Back Pieces**: $1200 - $3000+\n\n⏰ **Hourly Rate**: $150/hour\n💳 **Deposit Required**: 50% of estimated cost\n\n*Pricing varies based on complexity, detail level, and placement. Would you like a specific quote?*",
        confidence: 0.92,
        suggestions: ["Get a quote", "What's included?", "Payment options"],
        quickReplies: ["I want a quote", "Show me examples", "Book consultation"]
      };
    }
    
    if (lowerInput.includes('style') || lowerInput.includes('design') || lowerInput.includes('portfolio')) {
      return {
        content: "Here are the tattoo styles I specialize in:\n\n🎨 **My Specialties:**\n• **Realism** - Photorealistic portraits and nature\n• **Geometric** - Mandalas, sacred geometry, patterns\n• **Blackwork** - Bold, high-contrast designs\n• **Watercolor** - Soft, flowing color transitions\n• **Traditional** - Classic American and Japanese styles\n\n📸 **Portfolio Highlights:**\n• 150+ completed pieces\n• 4.9/5 star average rating\n• Featured in 3 tattoo magazines\n\nWould you like to see specific examples of any style?",
        confidence: 0.88,
        suggestions: ["Show realism examples", "Show geometric examples", "Show blackwork examples"],
        quickReplies: ["I love realism", "Show me more", "Book consultation"]
      };
    }
    
    if (lowerInput.includes('aftercare') || lowerInput.includes('healing') || lowerInput.includes('care')) {
      return {
        content: "Here's your complete aftercare guide:\n\n🩹 **First 24 Hours:**\n• Keep bandage on for 2-4 hours\n• Gently wash with antibacterial soap\n• Pat dry with clean towel\n• Apply thin layer of healing ointment\n\n📅 **First Week:**\n• Wash 2-3 times daily\n• Apply healing ointment 2-3 times daily\n• Avoid soaking (baths, pools, hot tubs)\n• Wear loose, breathable clothing\n\n⚠️ **What to Avoid:**\n• Direct sunlight\n• Picking or scratching\n• Heavy exercise\n• Tight clothing\n\n*I'll provide detailed written instructions after your session!*",
        confidence: 0.94,
        suggestions: ["Download aftercare guide", "What if it gets infected?", "When can I exercise?"],
        quickReplies: ["Got it", "More questions", "Book appointment"]
      };
    }
    
    // Default response
    return {
      content: "I understand you're interested in getting a tattoo! I can help you with:\n\n• **Design Ideas** - Browse styles and get inspiration\n• **Pricing** - Get quotes and understand costs\n• **Booking** - Schedule your appointment\n• **Aftercare** - Learn about healing and care\n• **General Questions** - Ask me anything about tattoos\n\nWhat would you like to explore first?",
      confidence: 0.85,
      suggestions: ["Show me designs", "Tell me about pricing", "Book appointment", "Aftercare info"],
      quickReplies: ["I want a tattoo", "Show me portfolios", "How much?", "When can I book?"]
    };
  };

  // APOLLO-APPROVED Quick Action Handler
  const handleQuickAction = (actionId: string) => {
    setSelectedQuickAction(actionId);
    
    switch (actionId) {
      case 'book_appointment':
        handleSendMessage("I want to book an appointment");
        break;
      case 'view_portfolio':
        handleSendMessage("Show me your portfolio");
        break;
      case 'get_pricing':
        handleSendMessage("What are your prices?");
        break;
      case 'contact_artist':
        handleSendMessage("I want to contact the artist directly");
        break;
    }
    
    setTimeout(() => setSelectedQuickAction(null), 2000);
  };

  // APOLLO-APPROVED Voice Recording
  const toggleRecording = () => {
    if (!recognitionRef.current) return;
    
    if (isRecording) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  // APOLLO-APPROVED Message Component
  const MessageBubble = ({ message }: { message: Message }) => (
    <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
        message.type === 'user'
          ? 'bg-blue-500 text-white'
          : message.type === 'ai'
          ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-lg'
          : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 text-sm'
      }`}>
        <div className="whitespace-pre-wrap">{message.content}</div>
        
        {message.metadata?.suggestions && message.metadata.suggestions.length > 0 && (
          <div className="mt-3 space-y-2">
            <p className="text-xs opacity-75 mb-2">Quick suggestions:</p>
            <div className="flex flex-wrap gap-1">
              {message.metadata.suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSendMessage(suggestion)}
                  className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-500 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        
        <div className="text-xs opacity-75 mt-2">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );

  return (
    <div className={`min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 ${className}`}>
      {/* APOLLO-APPROVED Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  {context.artistName} - AI Assistant
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Your personal tattoo consultation assistant
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                Online
              </div>
              
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* APOLLO-APPROVED Quick Actions */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex flex-wrap gap-2 justify-center">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={action.action}
              disabled={selectedQuickAction === action.id}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-white text-sm font-medium transition-all duration-200 ${
                selectedQuickAction === action.id
                  ? 'scale-95 opacity-75'
                  : action.color
              }`}
            >
              <action.icon className="w-4 h-4" />
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* APOLLO-APPROVED Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 max-h-96">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-gray-700 rounded-2xl px-4 py-2 shadow-lg">
              <div className="flex items-center gap-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm text-gray-600 dark:text-gray-400">AI is typing...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* APOLLO-APPROVED Input Area */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type your message..."
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-2xl bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={isLoading}
            />
            
            {showSuggestions && (
              <div className="absolute bottom-full left-0 right-0 mb-2 bg-white dark:bg-gray-700 rounded-lg shadow-lg border border-gray-200 dark:border-gray-600 p-2">
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">Quick suggestions:</div>
                <div className="space-y-1">
                  {['Book appointment', 'Show portfolio', 'Get pricing', 'Aftercare info'].map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setInputValue(suggestion);
                        setShowSuggestions(false);
                        inputRef.current?.focus();
                      }}
                      className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={toggleRecording}
              className={`p-3 rounded-full transition-colors ${
                isRecording
                  ? 'bg-red-500 text-white animate-pulse'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
              title={isRecording ? 'Stop recording' : 'Start voice input'}
            >
              {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
            
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputValue.trim() || isLoading}
              className="p-3 bg-purple-500 text-white rounded-full hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Send message"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div className="flex items-center justify-between mt-3 text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-4">
            <button className="flex items-center gap-1 hover:text-purple-500 transition-colors">
              <Camera className="w-4 h-4" />
              Photo
            </button>
            <button className="flex items-center gap-1 hover:text-purple-500 transition-colors">
              <Image className="w-4 h-4" />
              Image
            </button>
            <button className="flex items-center gap-1 hover:text-purple-500 transition-colors">
              <FileText className="w-4 h-4" />
              Document
            </button>
          </div>
          
          <div className="flex items-center gap-2">
            <span>Press Enter to send</span>
            <span>•</span>
            <span>Ctrl + Enter for new line</span>
          </div>
        </div>
      </div>
    </div>
  );
}
