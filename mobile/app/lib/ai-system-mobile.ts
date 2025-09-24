// APOLLO MOBILE - Optimized AI System for Mobile Devices
import { Message } from '../types';
import { ragPipelineMobile } from './rag-pipeline-mobile';

interface MobileAIResponse {
  response: string;
  confidence: number;
  intent: string;
  entities: Record<string, any>;
  suggestions: string[];
  sources: string[];
  pipeline: string;
  metadata: {
    processingTime: number;
    model: string;
    timestamp: Date;
    mobileOptimized: boolean;
    memoryUsage: number;
  };
}

interface MobileAIContext {
  conversationHistory: Message[];
  userPreferences: Record<string, any>;
  sessionData: Record<string, any>;
  businessRules: Record<string, any>;
  deviceCapabilities: {
    hasLocalAI: boolean;
    maxMemoryMB: number;
    isOnline: boolean;
    batteryLevel?: number;
  };
}

class ApolloMobileAISystem {
  private knowledgeBase: Map<string, any> = new Map();
  private conversationMemory: Map<string, Message[]> = new Map();
  private userProfiles: Map<string, any> = new Map();
  private localModelCache: Map<string, any> = new Map();
  private isLocalModelLoaded: boolean = false;

  constructor() {
    this.initializeMobileKnowledgeBase();
  }

  private initializeMobileKnowledgeBase() {
    // Mobile-optimized knowledge base (reduced size)
    this.knowledgeBase.set('tattoo_styles', [
      'Traditional', 'Realistic', 'Geometric', 'Watercolor', 'Blackwork', 
      'Minimalist', 'Japanese', 'Neo-traditional'
    ]);
    
    this.knowledgeBase.set('body_parts', [
      'Arm', 'Leg', 'Back', 'Chest', 'Shoulder', 'Wrist', 'Ankle', 
      'Neck', 'Ribcage', 'Hand', 'Foot'
    ]);
    
    this.knowledgeBase.set('pricing_factors', [
      'Size', 'Complexity', 'Color', 'Body placement', 'Artist experience', 
      'Time required'
    ]);
    
    this.knowledgeBase.set('aftercare_steps', [
      'Keep bandage on for 2-4 hours',
      'Wash hands before touching tattoo',
      'Gently wash with antibacterial soap',
      'Pat dry with clean towel',
      'Apply thin layer of healing ointment',
      'Avoid direct sunlight',
      'Don\'t pick at scabs',
      'Moisturize regularly'
    ]);

    // Mobile-specific optimizations
    this.knowledgeBase.set('mobile_features', [
      'Quick booking', 'Photo upload', 'Voice input', 'Offline mode',
      'Push notifications', 'Location services', 'Contact sync'
    ]);
  }

  async processQuery(input: string, context: MobileAIContext): Promise<MobileAIResponse> {
    const startTime = Date.now();
    const memoryStart = this.getMemoryUsage();
    
    // Preprocess input for mobile
    const processedInput = this.preprocessMobileInput(input);
    
    // Analyze intent with mobile optimizations
    const intent = this.analyzeMobileIntent(processedInput);
    
    // Extract entities with mobile constraints
    const entities = this.extractMobileEntities(processedInput);
    
    // Choose processing method based on device capabilities
    let response: MobileAIResponse;
    
    if (context.deviceCapabilities.hasLocalAI && this.isLocalModelLoaded) {
      // Use local model (llama3.2:1b)
      response = await this.processWithLocalModel(processedInput, intent, entities, context);
    } else if (context.deviceCapabilities.isOnline) {
      // Use cloud API with mobile optimizations
      response = await this.processWithCloudAPI(processedInput, intent, entities, context);
    } else {
      // Use offline fallback
      response = await this.processOffline(processedInput, intent, entities, context);
    }

    // Add mobile-specific metadata
    response.metadata.mobileOptimized = true;
    response.metadata.memoryUsage = this.getMemoryUsage() - memoryStart;
    response.metadata.processingTime = Date.now() - startTime;

    return response;
  }

  private preprocessMobileInput(input: string): string {
    // Mobile-optimized preprocessing
    return input
      .toLowerCase()
      .trim()
      .replace(/[^\w\s]/g, '')
      .replace(/\s+/g, ' ')
      .substring(0, 500); // Limit input length for mobile
  }

  private analyzeMobileIntent(input: string): string {
    // Mobile-optimized intent detection
    const intents = {
      quick_book: ['book', 'schedule', 'appointment', 'quick', 'fast'],
      pricing: ['price', 'cost', 'how much', 'budget'],
      design: ['design', 'idea', 'style', 'show', 'photo'],
      aftercare: ['care', 'heal', 'healing', 'after'],
      artist: ['artist', 'who', 'portfolio'],
      hours: ['open', 'hours', 'when'],
      location: ['where', 'address', 'location'],
      mobile: ['app', 'mobile', 'phone', 'offline'],
      general: ['hello', 'hi', 'help', 'what', 'how']
    };

    for (const [intent, keywords] of Object.entries(intents)) {
      if (keywords.some(keyword => input.includes(keyword))) {
        return intent;
      }
    }

    return 'general';
  }

  private extractMobileEntities(input: string): Record<string, any> {
    const entities: Record<string, any> = {};
    
    // Extract tattoo styles (mobile-optimized)
    const styles = this.knowledgeBase.get('tattoo_styles') || [];
    const foundStyles = styles.filter((style: string) =>
      input.includes(style.toLowerCase())
    );
    if (foundStyles.length > 0) {
      entities.tattoo_styles = foundStyles;
    }
    
    // Extract body parts (mobile-optimized)
    const bodyParts = this.knowledgeBase.get('body_parts') || [];
    const foundBodyParts = bodyParts.filter((part: string) =>
      input.includes(part.toLowerCase())
    );
    if (foundBodyParts.length > 0) {
      entities.body_parts = foundBodyParts;
    }
    
    // Extract size indicators (simplified for mobile)
    const sizePatterns = [
      /(small|medium|large|tiny)/i,
      /(\d+)\s*(inch|cm)/i
    ];
    
    for (const pattern of sizePatterns) {
      const match = input.match(pattern);
      if (match) {
        entities.size = match[0];
        break;
      }
    }
    
    return entities;
  }

  private async processWithLocalModel(
    input: string, 
    intent: string, 
    entities: Record<string, any>, 
    context: MobileAIContext
  ): Promise<MobileAIResponse> {
    // Use local llama3.2:1b model
    try {
      const ragResponse = await ragPipelineMobile.processQuery(input, {
        ...context,
        intent,
        entities,
        useLocalModel: true
      });
      
      return {
        response: ragResponse.answer,
        confidence: ragResponse.confidence,
        intent,
        entities,
        suggestions: ragResponse.suggestions,
        sources: ragResponse.sources,
        pipeline: 'mobile_local',
        metadata: {
          processingTime: 0, // Will be set by caller
          model: 'llama3.2:1b-mobile',
          timestamp: new Date(),
          mobileOptimized: true,
          memoryUsage: 0 // Will be set by caller
        }
      };
    } catch (error) {
      console.error('Local model error, falling back to offline:', error);
      return this.processOffline(input, intent, entities, context);
    }
  }

  private async processWithCloudAPI(
    input: string, 
    intent: string, 
    entities: Record<string, any>, 
    context: MobileAIContext
  ): Promise<MobileAIResponse> {
    // Use cloud API with mobile optimizations
    try {
      const ragResponse = await ragPipelineMobile.processQuery(input, {
        ...context,
        intent,
        entities,
        useLocalModel: false
      });
      
      return {
        response: ragResponse.answer,
        confidence: ragResponse.confidence,
        intent,
        entities,
        suggestions: ragResponse.suggestions,
        sources: ragResponse.sources,
        pipeline: 'mobile_cloud',
        metadata: {
          processingTime: 0, // Will be set by caller
          model: 'APOLLO-Mobile-Cloud',
          timestamp: new Date(),
          mobileOptimized: true,
          memoryUsage: 0 // Will be set by caller
        }
      };
    } catch (error) {
      console.error('Cloud API error, falling back to offline:', error);
      return this.processOffline(input, intent, entities, context);
    }
  }

  private async processOffline(
    input: string, 
    intent: string, 
    entities: Record<string, any>, 
    context: MobileAIContext
  ): Promise<MobileAIResponse> {
    // Offline fallback with cached responses
    const response = this.generateMobileResponse(input, intent, entities, context);
    const suggestions = this.generateMobileSuggestions(intent, entities);
    const confidence = this.calculateMobileConfidence(intent, entities, response);
    
    return {
      response,
      confidence,
      intent,
      entities,
      suggestions,
      sources: ['mobile_offline'],
      pipeline: 'mobile_offline',
      metadata: {
        processingTime: 0, // Will be set by caller
        model: 'APOLLO-Mobile-Offline',
        timestamp: new Date(),
        mobileOptimized: true,
        memoryUsage: 0 // Will be set by caller
      }
    };
  }

  private generateMobileResponse(
    input: string, 
    intent: string, 
    entities: Record<string, any>, 
    context: MobileAIContext
  ): string {
    const responses = {
      quick_book: this.generateQuickBookResponse(entities),
      pricing: this.generatePricingResponse(entities),
      design: this.generateDesignResponse(entities),
      aftercare: this.generateAftercareResponse(entities),
      artist: this.generateArtistResponse(entities),
      hours: this.generateHoursResponse(),
      location: this.generateLocationResponse(),
      mobile: this.generateMobileFeatureResponse(entities),
      general: this.generateGeneralResponse(input, entities)
    };

    return responses[intent as keyof typeof responses] || responses.general;
  }

  private generateQuickBookResponse(entities: Record<string, any>): string {
    let response = "I can help you book quickly! ";
    
    if (entities.tattoo_styles) {
      response += `${entities.tattoo_styles.join(', ')} style - great choice! `;
    }
    
    response += "Tap 'Book Now' for instant scheduling. Available slots: Today 2pm, Tomorrow 10am, Friday 3pm.";
    
    return response;
  }

  private generatePricingResponse(entities: Record<string, any>): string {
    let response = "Quick pricing: ";
    
    if (entities.size === 'small') {
      response += "Small tattoos: $100-200";
    } else if (entities.size === 'medium') {
      response += "Medium tattoos: $200-400";
    } else if (entities.size === 'large') {
      response += "Large tattoos: $400+";
    } else {
      response += "Small: $100-200, Medium: $200-400, Large: $400+";
    }
    
    response += ". Tap for detailed quote!";
    
    return response;
  }

  private generateDesignResponse(entities: Record<string, any>): string {
    let response = "Design help! ";
    
    if (entities.tattoo_styles) {
      response += `${entities.tattoo_styles.join(', ')} styles available. `;
    }
    
    response += "Upload a photo or browse our gallery. Tap 'Design Studio' to start!";
    
    return response;
  }

  private generateAftercareResponse(entities: Record<string, any>): string {
    const steps = this.knowledgeBase.get('aftercare_steps') || [];
    let response = "Aftercare essentials:\n\n";
    
    // Show only first 4 steps for mobile
    steps.slice(0, 4).forEach((step: string, index: number) => {
      response += `${index + 1}. ${step}\n`;
    });
    
    response += "\nTap 'Full Guide' for complete instructions.";
    
    return response;
  }

  private generateArtistResponse(entities: Record<string, any>): string {
    let response = "Our artists: ";
    
    if (entities.tattoo_styles) {
      response += `Specialists in ${entities.tattoo_styles.join(', ')}. `;
    }
    
    response += "Tap 'View Artists' to see portfolios and book directly!";
    
    return response;
  }

  private generateHoursResponse(): string {
    return "Hours: Tue-Sat 10am-8pm. Closed Sun-Mon. Tap 'Book Now' to see available times!";
  }

  private generateLocationResponse(): string {
    return "We're at [Your Address]. Tap 'Directions' for GPS navigation!";
  }

  private generateMobileFeatureResponse(entities: Record<string, any>): string {
    return "Mobile features: Quick booking, photo upload, voice input, offline mode, push notifications. What would you like to try?";
  }

  private generateGeneralResponse(input: string, entities: Record<string, any>): string {
    if (input.includes('apollo') || input.includes('ai')) {
      return "I'm APOLLO Mobile - your AI assistant optimized for mobile! I can help with quick booking, pricing, designs, and more. What do you need?";
    }
    
    return "Hi! I'm here to help with your tattoo needs. Try: 'Book appointment', 'Get pricing', 'See designs', or 'Learn about aftercare'.";
  }

  private generateMobileSuggestions(intent: string, entities: Record<string, any>): string[] {
    const suggestions: Record<string, string[]> = {
      quick_book: [
        "Book for today",
        "Check tomorrow's slots",
        "See all availability"
      ],
      pricing: [
        "Get custom quote",
        "See price examples",
        "Calculate by size"
      ],
      design: [
        "Upload photo",
        "Browse gallery",
        "Start design studio"
      ],
      aftercare: [
        "View full guide",
        "Set reminders",
        "Ask questions"
      ],
      artist: [
        "View portfolios",
        "Book consultation",
        "See specialties"
      ],
      mobile: [
        "Enable notifications",
        "Try voice input",
        "Go offline"
      ]
    };

    return suggestions[intent] || [
      "Book appointment",
      "Get pricing",
      "See designs",
      "View artists"
    ];
  }

  private calculateMobileConfidence(intent: string, entities: Record<string, any>, response: string): number {
    let confidence = 0.6; // Higher base confidence for mobile
    
    // Increase confidence based on entity extraction
    const entityCount = Object.keys(entities).length;
    confidence += entityCount * 0.15;
    
    // Increase confidence for specific intents
    if (intent !== 'general') {
      confidence += 0.25;
    }
    
    // Mobile-optimized confidence calculation
    if (response.length > 50 && response.length < 200) {
      confidence += 0.1; // Sweet spot for mobile responses
    }
    
    return Math.min(confidence, 1.0);
  }

  private getMemoryUsage(): number {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      return process.memoryUsage().heapUsed / 1024 / 1024; // MB
    }
    return 0;
  }

  // Mobile-specific methods
  async loadLocalModel(): Promise<boolean> {
    try {
      // Simulate loading llama3.2:1b model
      console.log('Loading llama3.2:1b model for mobile...');
      this.isLocalModelLoaded = true;
      return true;
    } catch (error) {
      console.error('Failed to load local model:', error);
      return false;
    }
  }

  async unloadLocalModel(): Promise<void> {
    this.isLocalModelLoaded = false;
    this.localModelCache.clear();
  }

  // Memory management for mobile
  storeConversation(sessionId: string, messages: Message[]) {
    // Limit conversation history for mobile
    const limitedMessages = messages.slice(-10); // Keep only last 10 messages
    this.conversationMemory.set(sessionId, limitedMessages);
  }

  getConversationHistory(sessionId: string): Message[] {
    return this.conversationMemory.get(sessionId) || [];
  }

  // Mobile-optimized user profile management
  updateUserProfile(userId: string, preferences: Record<string, any>) {
    // Store only essential preferences for mobile
    const mobilePreferences = {
      favoriteStyles: preferences.favoriteStyles?.slice(0, 3), // Limit to 3
      preferredArtist: preferences.preferredArtist,
      notificationSettings: preferences.notificationSettings,
      offlineMode: preferences.offlineMode || false
    };
    this.userProfiles.set(userId, mobilePreferences);
  }

  getUserProfile(userId: string): Record<string, any> {
    return this.userProfiles.get(userId) || {};
  }

  // Mobile performance monitoring
  getPerformanceMetrics(): {
    memoryUsage: number;
    isLocalModelLoaded: boolean;
    cacheSize: number;
    conversationCount: number;
  } {
    return {
      memoryUsage: this.getMemoryUsage(),
      isLocalModelLoaded: this.isLocalModelLoaded,
      cacheSize: this.localModelCache.size,
      conversationCount: this.conversationMemory.size
    };
  }
}

// Export singleton instance
export const apolloMobileAI = new ApolloMobileAISystem();
export default apolloMobileAI;
