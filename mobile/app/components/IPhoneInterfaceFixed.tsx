'use client';

import React, { useState } from 'react';

interface IPhoneInterfaceProps {
  onScreenClick?: () => void;
}

export default function IPhoneInterfaceFixed({ onScreenClick }: IPhoneInterfaceProps) {
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [chatMessages, setChatMessages] = useState<Array<{id: number, text: string, sender: 'user' | 'ai'}>>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleScreenClick = () => {
    if (!isUnlocked) {
      setIsUnlocked(true);
      onScreenClick?.();
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user' as const
    };

    setChatMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        text: "I'm APOLLO 1.0.0, your advanced Tattoo AI assistant. I can help you with design consultations, appointment booking, pricing estimates, and aftercare guidance. What can I help you with today?",
        sender: 'ai' as const
      };
      setChatMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  // APOLLO Analysis: Use inline styles to avoid CSS conflicts
  const styles = {
    container: {
      minHeight: '100vh',
      backgroundColor: '#000000',
      position: 'relative' as const,
      overflow: 'hidden',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    background: {
      position: 'absolute' as const,
      inset: 0,
      background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #000000 100%)'
    },
    glow1: {
      position: 'absolute' as const,
      top: '25%',
      left: '25%',
      width: '384px',
      height: '384px',
      backgroundColor: 'rgba(59, 130, 246, 0.2)',
      borderRadius: '50%',
      filter: 'blur(48px)',
      animation: 'apolloPulse 3s ease-in-out infinite'
    },
    glow2: {
      position: 'absolute' as const,
      bottom: '25%',
      right: '25%',
      width: '320px',
      height: '320px',
      backgroundColor: 'rgba(96, 165, 250, 0.15)',
      borderRadius: '50%',
      filter: 'blur(48px)',
      animation: 'apolloPulse 3s ease-in-out infinite 1s'
    },
    glow3: {
      position: 'absolute' as const,
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      width: '256px',
      height: '256px',
      backgroundColor: 'rgba(37, 99, 235, 0.1)',
      borderRadius: '50%',
      filter: 'blur(32px)',
      animation: 'apolloPulse 3s ease-in-out infinite 0.5s'
    },
    leftBranding: {
      position: 'absolute' as const,
      left: '32px',
      top: '50%',
      transform: 'translateY(-50%)',
      opacity: 1,
      animation: 'fadeInLeft 1s ease-out 0.5s both'
    },
    rightBranding: {
      position: 'absolute' as const,
      right: '32px',
      top: '50%',
      transform: 'translateY(-50%)',
      textAlign: 'right' as const,
      opacity: 1,
      animation: 'fadeInRight 1s ease-out 0.7s both'
    },
    phoneContainer: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '32px'
    },
    phoneFrame: {
      position: 'relative' as const,
      width: '320px',
      height: '640px',
      backgroundColor: '#000000',
      borderRadius: '48px',
      padding: '8px',
      boxShadow: '0 0 60px rgba(59, 130, 246, 0.3), 0 0 120px rgba(59, 130, 246, 0.2)',
      animation: 'phoneGlow 2s ease-in-out infinite alternate'
    },
    phoneScreen: {
      position: 'relative' as const,
      width: '100%',
      height: '100%',
      backgroundColor: '#000000',
      borderRadius: '40px',
      overflow: 'hidden'
    },
    lockScreen: {
      width: '100%',
      height: '100%',
      background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #000000 100%)',
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      justifyContent: 'center',
      cursor: 'pointer',
      transition: 'transform 0.3s ease',
      position: 'relative' as const
    },
    dynamicIsland: {
      position: 'absolute' as const,
      top: '16px',
      left: '50%',
      transform: 'translateX(-50%)',
      width: '128px',
      height: '32px',
      backgroundColor: '#000000',
      borderRadius: '50%',
      border: '1px solid #374151'
    },
    brandTitle: {
      textAlign: 'center' as const,
      marginBottom: '32px',
      animation: 'fadeInUp 1s ease-out 1.5s both'
    },
    brandText: {
      fontSize: '48px',
      fontWeight: 'bold',
      background: 'linear-gradient(90deg, #ffffff 0%, #60a5fa 50%, #3b82f6 100%)',
      backgroundSize: '200% 100%',
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      animation: 'textShimmer 4s ease-in-out infinite',
      marginBottom: '8px'
    },
    apolloTitle: {
      textAlign: 'center' as const,
      animation: 'fadeInUp 1s ease-out 2s both'
    },
    apolloText: {
      fontSize: '20px',
      fontWeight: '600',
      color: '#60a5fa',
      textShadow: '0 0 10px #3b82f6, 0 0 25px #3b82f6, 0 0 35px #3b82f6',
      animation: 'apolloGlow 2s ease-in-out infinite'
    },
    tapHint: {
      fontSize: '14px',
      color: '#9ca3af',
      marginTop: '8px',
      animation: 'pulse 2s ease-in-out infinite'
    },
    glassEffect: {
      position: 'absolute' as const,
      inset: 0,
      background: 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, transparent 50%, rgba(59,130,246,0.05) 100%)',
      borderRadius: '40px'
    }
  };

  return (
    <>
      {/* APOLLO Analysis: Add CSS animations to head */}
      <style jsx global>{`
        @keyframes apolloPulse {
          0%, 100% { opacity: 0.8; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.05); }
        }
        @keyframes fadeInLeft {
          from { opacity: 0; transform: translateY(-50%) translateX(-50px); }
          to { opacity: 1; transform: translateY(-50%) translateX(0); }
        }
        @keyframes fadeInRight {
          from { opacity: 0; transform: translateY(-50%) translateX(50px); }
          to { opacity: 1; transform: translateY(-50%) translateX(0); }
        }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes textShimmer {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        @keyframes apolloGlow {
          0%, 100% { text-shadow: 0 0 10px #3b82f6; }
          50% { text-shadow: 0 0 25px #3b82f6, 0 0 35px #3b82f6; }
        }
        @keyframes phoneGlow {
          0% { box-shadow: 0 0 60px rgba(59, 130, 246, 0.3), 0 0 120px rgba(59, 130, 246, 0.2); }
          100% { box-shadow: 0 0 80px rgba(59, 130, 246, 0.4), 0 0 140px rgba(59, 130, 246, 0.3); }
        }
      `}</style>

      <div style={styles.container}>
        {/* Background with Electric Blue Glow */}
        <div style={styles.background}>
          <div style={styles.glow1}></div>
          <div style={styles.glow2}></div>
          <div style={styles.glow3}></div>
        </div>

        {/* Company Branding - Left Side */}
        <div style={styles.leftBranding}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: 'bold',
            background: 'linear-gradient(90deg, #ffffff 0%, #60a5fa 50%, #3b82f6 100%)',
            backgroundSize: '200% 100%',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            animation: 'textShimmer 3s ease-in-out infinite'
          }}>
            NextElevenStudios
          </h1>
        </div>

        {/* Right Side Branding */}
        <div style={styles.rightBranding}>
          <div style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: '#60a5fa',
            marginBottom: '8px',
            textShadow: '0 0 5px #3b82f6, 0 0 20px #3b82f6, 0 0 5px #3b82f6',
            animation: 'apolloGlow 2s ease-in-out infinite'
          }}>
            APOLLO 1.0.0
          </div>
          <div style={{
            fontSize: '18px',
            color: '#93c5fd',
            animation: 'pulse 2s ease-in-out infinite 1s'
          }}>
            BizBot.store
          </div>
        </div>

        {/* iPhone 17 Pro Max Container */}
        <div style={styles.phoneContainer}>
          <div style={styles.phoneFrame}>
            {/* Screen */}
            <div style={styles.phoneScreen}>
              {!isUnlocked ? (
                /* Lock Screen - Jet Black Glass Panel */
                <div 
                  style={styles.lockScreen}
                  onClick={handleScreenClick}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                >
                  {/* Dynamic Island */}
                  <div style={styles.dynamicIsland}></div>
                  
                  {/* NextEleven Brand */}
                  <div style={styles.brandTitle}>
                    <h1 style={styles.brandText}>
                      NextEleven
                    </h1>
                  </div>

                  {/* APOLLO 1.0.0 with Pulsing Blue */}
                  <div style={styles.apolloTitle}>
                    <div style={styles.apolloText}>
                      APOLLO 1.0.0
                    </div>
                    <div style={styles.tapHint}>
                      Tap to unlock
                    </div>
                  </div>

                  {/* Glass Morphism Effect */}
                  <div style={styles.glassEffect}></div>
                </div>
              ) : (
                /* Chat Interface - APOLLO Analysis: Simplified iPhone-style chat */
                <div style={{
                  width: '100%',
                  height: '100%',
                  background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #000000 100%)',
                  display: 'flex',
                  flexDirection: 'column'
                }}>
                  {/* Status Bar */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '16px',
                    color: 'white',
                    fontSize: '14px'
                  }}>
                    <div>9:41</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <div style={{ width: '16px', height: '8px', backgroundColor: 'white', borderRadius: '4px' }}></div>
                      <div style={{ width: '24px', height: '12px', border: '1px solid white', borderRadius: '4px' }}></div>
                    </div>
                  </div>

                  {/* Chat Header */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '16px',
                    borderBottom: '1px solid #374151'
                  }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      backgroundColor: '#3b82f6',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontWeight: 'bold'
                    }}>
                      A
                    </div>
                    <div style={{ marginLeft: '12px' }}>
                      <div style={{ color: 'white', fontWeight: '600' }}>Tattoo AI</div>
                      <div style={{ color: '#60a5fa', fontSize: '14px' }}>APOLLO 1.0.0</div>
                    </div>
                  </div>

                  {/* Chat Messages */}
                  <div style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '16px'
                  }}>
                    {chatMessages.map((message) => (
                      <div
                        key={message.id}
                        style={{
                          display: 'flex',
                          justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start'
                        }}
                      >
                        <div style={{
                          maxWidth: '80%',
                          padding: '12px',
                          borderRadius: '16px',
                          backgroundColor: message.sender === 'user' ? '#3b82f6' : '#374151',
                          color: message.sender === 'user' ? '#000000' : '#ffffff',
                          fontSize: '14px',
                          lineHeight: '1.4'
                        }}>
                          {message.text}
                        </div>
                      </div>
                    ))}
                    
                    {isTyping && (
                      <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                        <div style={{
                          backgroundColor: '#374151',
                          padding: '12px',
                          borderRadius: '16px'
                        }}>
                          <div style={{ display: 'flex', gap: '4px' }}>
                            <div style={{
                              width: '8px',
                              height: '8px',
                              backgroundColor: '#60a5fa',
                              borderRadius: '50%',
                              animation: 'bounce 1.4s infinite ease-in-out both'
                            }}></div>
                            <div style={{
                              width: '8px',
                              height: '8px',
                              backgroundColor: '#60a5fa',
                              borderRadius: '50%',
                              animation: 'bounce 1.4s infinite ease-in-out both 0.16s'
                            }}></div>
                            <div style={{
                              width: '8px',
                              height: '8px',
                              backgroundColor: '#60a5fa',
                              borderRadius: '50%',
                              animation: 'bounce 1.4s infinite ease-in-out both 0.32s'
                            }}></div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Input Area */}
                  <div style={{
                    padding: '16px',
                    borderTop: '1px solid #374151'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Ask about tattoos..."
                        style={{
                          flex: 1,
                          backgroundColor: '#374151',
                          color: 'white',
                          padding: '12px',
                          borderRadius: '16px',
                          border: '1px solid #4b5563',
                          outline: 'none',
                          fontSize: '14px'
                        }}
                      />
                      <button
                        onClick={sendMessage}
                        style={{
                          backgroundColor: '#3b82f6',
                          color: 'white',
                          padding: '12px',
                          borderRadius: '50%',
                          border: 'none',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          transition: 'transform 0.2s ease'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                        onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                      >
                        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
