'use client'

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useApp, appActions } from '../context/AppContext';
import { apolloClient } from '../lib/apollo-client';
import { apolloAI } from '../lib/ai-system';
import { apolloAnalytics } from '../lib/analytics';
import { Message } from '../types';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, Loader2, Mic, MicOff, Volume2 } from 'lucide-react';

export default function ChatInterfaceEnhanced() {
  const { state, dispatch } = useApp();
  const { messages, isLoading } = state;
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any | null>(null);
  const synthesisRef = useRef<SpeechSynthesisUtterance | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      recognitionRef.current = new (window as any).webkitSpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        inputRef.current?.focus();
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

  // Track page view
  useEffect(() => {
    apolloAnalytics.trackPageView('/chat', 'Enhanced Chat Interface');
  }, []);

  const sanitizeInput = (input: string): string => {
    return input
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '')
      .trim()
      .substring(0, 500);
  };

  const generateTypingAnimation = () => {
    setIsTyping(true);
    setTimeout(() => setIsTyping(false), 2000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;

    const sanitizedInput = sanitizeInput(inputValue);
    if (!sanitizedInput) return;

    // Track user interaction
    apolloAnalytics.trackInteraction('chat_input', 'submit', {
      messageLength: sanitizedInput.length,
      sessionId
    });

    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: sanitizedInput,
      timestamp: new Date()
    };

    dispatch(appActions.addMessage(userMessage));
    dispatch(appActions.setLoading(true));
    setInputValue('');
    setSuggestions([]);
    generateTypingAnimation();

    try {
      // Create AI context
      const context = {
        conversationHistory: messages,
        userPreferences: {},
        sessionData: { sessionId },
        businessRules: {}
      };

      // Process with APOLLO AI
      const aiResponse = await apolloAI.processQuery(sanitizedInput, context);
      
      const aiMessage: Message = {
        id: Date.now() + 1,
        type: 'ai',
        content: aiResponse.response,
        timestamp: new Date()
      };

      dispatch(appActions.addMessage(aiMessage));
      setSuggestions(aiResponse.suggestions);

      // Auto-speak response
      speakText(aiResponse.response);

      // Track AI response
      apolloAnalytics.trackInteraction('ai_response', 'generated', {
        confidence: aiResponse.confidence,
        intent: aiResponse.intent,
        processingTime: aiResponse.metadata.processingTime,
        sessionId
      });

    } catch (error) {
      console.error('APOLLO AI Error:', error);
      
      // Track error
      apolloAnalytics.trackError(error as Error, { sessionId });
      
      // Fallback response
      const fallbackResponse = "I apologize, but I'm experiencing some technical difficulties. Please try again or contact us directly for assistance.";
      
      const aiMessage: Message = {
        id: Date.now() + 1,
        type: 'ai',
        content: fallbackResponse,
        timestamp: new Date()
      };

      dispatch(appActions.addMessage(aiMessage));
    } finally {
      dispatch(appActions.setLoading(false));
    }
  };

  const speakText = (text: string) => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      
      utterance.onstart = () => setIsPlaying(true);
      utterance.onend = () => setIsPlaying(false);
      
      synthesisRef.current = utterance;
      speechSynthesis.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      speechSynthesis.cancel();
      setIsPlaying(false);
    }
  };

  const startRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
      setIsRecording(true);
      apolloAnalytics.trackInteraction('voice_input', 'start', { sessionId });
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleSuggestionClick = useCallback((suggestion: string) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
    apolloAnalytics.trackInteraction('suggestion', 'click', { suggestion, sessionId });
  }, [sessionId]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearChat = () => {
    dispatch(appActions.setActiveTab('chat'));
    apolloAnalytics.trackInteraction('chat', 'clear', { sessionId });
  };

  return (
    <div className="chat-container">
      <motion.div 
        className="chat-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-apollo-500 apollo-glow" />
            <h2 className="text-2xl font-bold gradient-text">All Seeing Eye</h2>
          </div>
          <div className="flex items-center gap-2">
            {isPlaying && (
              <motion.button
                onClick={stopSpeaking}
                className="p-2 rounded-full bg-apollo-500/20 hover:bg-apollo-500/30 transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Volume2 className="w-4 h-4 text-apollo-500" />
              </motion.button>
            )}
            <button
              onClick={clearChat}
              className="px-3 py-1 text-sm bg-crowley-700 hover:bg-crowley-600 rounded-lg transition-colors"
            >
              Clear
            </button>
          </div>
        </div>
        <p className="text-sm text-gray-400 mt-1">Powered by APOLLO AI Consciousness</p>
      </motion.div>
      
      <div className="messages">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              className={`message ${message.type}`}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ 
                duration: 0.3, 
                delay: index * 0.1,
                type: "spring",
                stiffness: 100
              }}
            >
              <div className="message-avatar">
                {message.type === 'user' ? (
                  <User className="w-5 h-5" />
                ) : (
                  <Bot className="w-5 h-5" />
                )}
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-timestamp">
                  {message.timestamp?.toLocaleTimeString() || 'Unknown time'}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isLoading && (
          <motion.div 
            className="message ai"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="message-avatar">
              <Bot className="w-5 h-5" />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <Loader2 className="w-4 h-4 apollo-spin" />
                <span>APOLLO is thinking...</span>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {suggestions.length > 0 && (
        <motion.div 
          className="suggestions"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <p className="suggestions-label">Quick suggestions:</p>
          <div className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <motion.button
                key={index}
                className="suggestion-chip"
                onClick={() => handleSuggestionClick(suggestion)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                transition={{ type: "spring", stiffness: 400, damping: 17 }}
              >
                {suggestion}
              </motion.button>
            ))}
          </div>
        </motion.div>
      )}

      <motion.form 
        onSubmit={handleSubmit} 
        className="chat-form"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <div className="input-container">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about appointments, pricing, designs, or aftercare..."
            className="chat-input"
            maxLength={500}
            disabled={isLoading}
          />
          <div className="character-count">
            {inputValue.length}/500
          </div>
        </div>
        <div className="chat-actions">
          <motion.button
            type="button"
            onClick={isRecording ? stopRecording : startRecording}
            className={`voice-button ${isRecording ? 'recording' : ''}`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={isLoading}
          >
            {isRecording ? (
              <MicOff className="w-4 h-4" />
            ) : (
              <Mic className="w-4 h-4" />
            )}
          </motion.button>
          <motion.button 
            type="submit" 
            className="chat-button"
            disabled={!inputValue.trim() || isLoading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 apollo-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </motion.button>
        </div>
      </motion.form>
    </div>
  );
}
