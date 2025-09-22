'use client'

import React, { useState } from 'react';
import { Message } from '../types';
import { useApp, appActions } from '../context/AppContext';
// Removed apollo-client import

export default function ChatInterface() {
  const { state, dispatch } = useApp();
  const { messages, isLoading } = state;
  const [inputValue, setInputValue] = useState('');

  const sanitizeInput = (input: string): string => {
    return input
      .trim()
      .slice(0, 500) // Limit to 500 characters
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // Remove script tags
      .replace(/javascript:/gi, '') // Remove javascript: protocols
      .replace(/on\w+\s*=/gi, ''); // Remove event handlers
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const sanitizedInput = sanitizeInput(inputValue);
    if (!sanitizedInput) return;

    const userMessage: Message = {
      id: messages.length + 1,
      type: 'user',
      content: sanitizedInput,
      timestamp: new Date()
    };

    const currentInput = sanitizedInput; // Capture the sanitized input value before clearing
    dispatch(appActions.addMessage(userMessage));
    setInputValue('');
    dispatch(appActions.setLoading(true));

    // Get AI response from APOLLO
    try {
      // Simple response for tattoo app
      const response = { text: `I understand you're looking for tattoo services. How can I help you today?` };
      
      const aiResponse: Message = {
        id: messages.length + 2,
        type: 'ai',
        content: response.text,
        timestamp: new Date()
      };
      
      dispatch(appActions.addMessage(aiResponse));
      dispatch(appActions.setLoading(false));
    } catch (error) {
      console.error('AI response error:', error);
      // Fallback to local response
      const aiResponse: Message = {
        id: messages.length + 2,
        type: 'ai',
        content: generateAIResponse(currentInput),
        timestamp: new Date()
      };
      dispatch(appActions.addMessage(aiResponse));
      dispatch(appActions.setLoading(false));
    }
  };

  const generateAIResponse = (input: string) => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('appointment') || lowerInput.includes('book')) {
      return 'I can help you schedule an appointment! Our artists are available Tuesday-Saturday, 10am-8pm. What type of tattoo are you interested in?';
    }
    
    if (lowerInput.includes('price') || lowerInput.includes('cost')) {
      return 'Our pricing starts at $100 for small tattoos and varies based on size, complexity, and placement. A consultation will give you an exact quote.';
    }
    
    if (lowerInput.includes('design') || lowerInput.includes('idea')) {
      return 'I\'d love to help with design ideas! What style are you thinking - traditional, realistic, geometric, or something else?';
    }
    
    if (lowerInput.includes('aftercare') || lowerInput.includes('care')) {
      return 'Proper aftercare is crucial! Keep it clean, moisturized, and protected from sun. I can send you our detailed aftercare guide.';
    }
    
    return 'Thank you for your message! I\'m here to help with appointments, pricing, design consultations, aftercare, or any other tattoo-related questions. What would you like to know more about?';
  };

  return (
    <div className="chat-container">
      <h2 className="chat-header">All Seeing Eye</h2>
      
      <div className="messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              {message.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message ai">
            <div className="message-content">
              <div className="loading">
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <form className="chat-form" onSubmit={handleSend}>
        <div className="input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask about appointments, pricing, designs, or aftercare..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            maxLength={500}
          />
          <div className="character-count">
            {inputValue.length}/500
          </div>
        </div>
        <button 
          type="submit" 
          className="chat-button"
          disabled={!inputValue.trim() || isLoading}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}