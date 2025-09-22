// APOLLO MOBILE RAG Pipeline - Optimized for Mobile Devices
import { apolloIOSOptimizer } from './ios-optimizations';

interface MobileRAGResponse {
  answer: string;
  confidence: number;
  suggestions: string[];
  sources: string[];
  metadata: {
    pipeline: string;
    processingTime: number;
    memoryUsage: number;
    mobileOptimized: boolean;
    deviceCapabilities: string[];
  };
}

interface MobileRAGContext {
  conversationHistory: any[];
  intent: string;
  entities: Record<string, any>;
  useLocalModel: boolean;
  deviceCapabilities: {
    hasLocalAI: boolean;
    maxMemoryMB: number;
    isOnline: boolean;
    batteryLevel?: number;
  };
}

class MobileRAGPipeline {
  private knowledgeBase: Map<string, any> = new Map();
  private cache: Map<string, MobileRAGResponse> = new Map();
  private iosOptimizer = apolloIOSOptimizer;

  constructor() {
    this.initializeMobileKnowledgeBase();
  }

  private initializeMobileKnowledgeBase() {
    // Mobile-optimized knowledge base (reduced size for performance)
    this.knowledgeBase.set('tattoo', {
      styles: {
        traditional: {
          description: 'Classic American tattoo style with bold lines and bright colors',
          characteristics: ['Bold outlines', 'Bright colors', 'Classic designs'],
          pricing: 'Medium to high',
          time: '2-4 hours'
        },
        realistic: {
          description: 'Photorealistic tattoos that look like photographs',
          characteristics: ['Detailed shading', 'Realistic proportions', 'High detail'],
          pricing: 'High',
          time: '4-8 hours'
        },
        geometric: {
          description: 'Mathematical patterns and shapes',
          characteristics: ['Clean lines', 'Symmetrical patterns', 'Minimalist'],
          pricing: 'Medium',
          time: '2-6 hours'
        },
        watercolor: {
          description: 'Painterly style with flowing colors',
          characteristics: ['Soft edges', 'Color blending', 'Artistic'],
          pricing: 'Medium to high',
          time: '3-6 hours'
        },
        minimalist: {
          description: 'Simple, clean designs with minimal detail',
          characteristics: ['Simple lines', 'Minimal detail', 'Clean'],
          pricing: 'Low to medium',
          time: '1-3 hours'
        }
      },
      bodyParts: {
        arm: {
          description: 'Upper or lower arm placement',
          pain: 'Low to medium',
          healing: '2-3 weeks',
          visibility: 'High'
        },
        leg: {
          description: 'Thigh or calf placement',
          pain: 'Medium',
          healing: '2-4 weeks',
          visibility: 'Medium'
        },
        back: {
          description: 'Upper or lower back placement',
          pain: 'Low to medium',
          healing: '3-4 weeks',
          visibility: 'Low'
        },
        chest: {
          description: 'Chest area placement',
          pain: 'Medium to high',
          healing: '3-4 weeks',
          visibility: 'Medium'
        },
        shoulder: {
          description: 'Shoulder blade or deltoid area',
          pain: 'Low to medium',
          healing: '2-3 weeks',
          visibility: 'High'
        }
      },
      aftercare: {
        immediate: [
          'Keep bandage on for 2-4 hours',
          'Wash hands before touching tattoo',
          'Gently wash with antibacterial soap',
          'Pat dry with clean towel'
        ],
        firstWeek: [
          'Apply thin layer of healing ointment',
          'Avoid direct sunlight',
          'Don\'t pick at scabs',
          'Wear loose clothing'
        ],
        ongoing: [
          'Moisturize regularly',
          'Use sunscreen when healed',
          'Avoid swimming for 2 weeks',
          'Follow artist instructions'
        ]
      },
      pricing: {
        small: { min: 100, max: 200, description: '1-3 inches' },
        medium: { min: 200, max: 400, description: '3-6 inches' },
        large: { min: 400, max: 800, description: '6+ inches' },
        factors: ['Size', 'Complexity', 'Color', 'Body placement', 'Artist experience']
      }
    });

    this.knowledgeBase.set('customer_service', {
      booking: {
        process: 'Easy online booking with real-time availability',
        cancellation: '24-hour cancellation policy',
        rescheduling: 'Free rescheduling up to 24 hours before',
        consultation: 'Free design consultation included'
      },
      support: {
        hours: 'Monday-Friday 9am-6pm',
        contact: 'Phone, email, or in-app chat',
        response: 'Within 2 hours during business hours'
      }
    });

    this.knowledgeBase.set('sales', {
      packages: {
        basic: 'Single session tattoo',
        premium: 'Multi-session piece with consultation',
        vip: 'Full sleeve or large piece with priority booking'
      },
      promotions: {
        firstTime: '10% off first tattoo',
        referral: '20% off for referrals',
        seasonal: 'Holiday specials available'
      }
    });

    this.knowledgeBase.set('conversation', {
      greetings: [
        'Hello! How can I help with your tattoo needs?',
        'Hi there! Ready to book your next tattoo?',
        'Welcome! What brings you in today?'
      ],
      fallbacks: [
        'I\'m here to help with appointments, pricing, and design advice.',
        'Feel free to ask about our services or book an appointment.',
        'How can I assist you today?'
      ]
    });
  }

  async processQuery(userQuery: string, context: MobileRAGContext): Promise<MobileRAGResponse> {
    const startTime = Date.now();
    const memoryStart = this.getMemoryUsage();
    
    // Check cache first for mobile performance
    const cacheKey = this.generateCacheKey(userQuery, context);
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey)!;
      cached.metadata.processingTime = Date.now() - startTime;
      cached.metadata.memoryUsage = this.getMemoryUsage() - memoryStart;
      return cached;
    }

    // Determine pipeline based on query and device capabilities
    const pipeline = this.determineMobilePipeline(userQuery, context);
    
    let response: MobileRAGResponse;
    
    switch (pipeline) {
      case 'tattoo':
        response = await this.createTattooPipeline(userQuery, context);
        break;
      case 'customer_service':
        response = await this.createCustomerServicePipeline(userQuery, context);
        break;
      case 'sales':
        response = await this.createSalesPipeline(userQuery, context);
        break;
      case 'conversation':
        response = await this.createConversationPipeline(userQuery, context);
        break;
      default:
        response = await this.createGeneralPipeline(userQuery, context);
    }

    // Add mobile-specific metadata
    response.metadata.processingTime = Date.now() - startTime;
    response.metadata.memoryUsage = this.getMemoryUsage() - memoryStart;
    response.metadata.mobileOptimized = true;
    response.metadata.deviceCapabilities = this.getDeviceCapabilities();

    // Cache response for mobile performance
    this.cacheResponse(cacheKey, response);

    return response;
  }

  private determineMobilePipeline(userQuery: string, context: MobileRAGContext): string {
    const lowerQuery = userQuery.toLowerCase();
    
    // Mobile-optimized pipeline detection
    const scores = {
      tattoo: 0,
      customer_service: 0,
      sales: 0,
      conversation: 0
    };

    // Tattoo keywords
    const tattooKeywords = ['tattoo', 'design', 'style', 'ink', 'artist', 'placement', 'size', 'color', 'aftercare'];
    tattooKeywords.forEach(keyword => {
      if (lowerQuery.includes(keyword)) scores.tattoo += 1;
    });

    // Customer service keywords
    const serviceKeywords = ['book', 'appointment', 'schedule', 'cancel', 'reschedule', 'hours', 'contact', 'help'];
    serviceKeywords.forEach(keyword => {
      if (lowerQuery.includes(keyword)) scores.customer_service += 1;
    });

    // Sales keywords
    const salesKeywords = ['price', 'cost', 'budget', 'package', 'deal', 'discount', 'promotion'];
    salesKeywords.forEach(keyword => {
      if (lowerQuery.includes(keyword)) scores.sales += 1;
    });

    // Conversation keywords
    const conversationKeywords = ['hello', 'hi', 'thanks', 'bye', 'good', 'bad', 'story', 'tell'];
    conversationKeywords.forEach(keyword => {
      if (lowerQuery.includes(keyword)) scores.conversation += 1;
    });

    // Return pipeline with highest score
    const maxScore = Math.max(...Object.values(scores));
    if (maxScore === 0) return 'conversation';
    
    return Object.keys(scores).find(key => scores[key as keyof typeof scores] === maxScore) || 'conversation';
  }

  private async createTattooPipeline(userQuery: string, context: MobileRAGContext): Promise<MobileRAGResponse> {
    const lowerQuery = userQuery.toLowerCase();
    const tattooData = this.knowledgeBase.get('tattoo');
    
    let answer = '';
    let confidence = 0.8;
    const suggestions: string[] = [];
    const sources: string[] = ['tattoo_knowledge_base'];

    // Style detection
    const styleKeywords = Object.keys(tattooData.styles);
    const foundStyles = styleKeywords.filter(style => lowerQuery.includes(style));
    
    if (foundStyles.length > 0) {
      const style = foundStyles[0];
      const styleData = tattooData.styles[style];
      answer += `${styleData.description}. `;
      answer += `Characteristics: ${styleData.characteristics.join(', ')}. `;
      answer += `Pricing: ${styleData.pricing}, Time: ${styleData.time}. `;
      confidence += 0.1;
      suggestions.push(`Learn more about ${style} tattoos`);
    }

    // Body part detection
    const bodyPartKeywords = Object.keys(tattooData.bodyParts);
    const foundBodyParts = bodyPartKeywords.filter(part => lowerQuery.includes(part));
    
    if (foundBodyParts.length > 0) {
      const part = foundBodyParts[0];
      const partData = tattooData.bodyParts[part];
      answer += `For ${part} placement: ${partData.description}. `;
      answer += `Pain level: ${partData.pain}, Healing: ${partData.healing}. `;
      confidence += 0.1;
      suggestions.push(`See ${part} tattoo examples`);
    }

    // Pricing queries
    if (lowerQuery.includes('price') || lowerQuery.includes('cost')) {
      answer += `Pricing: Small (1-3"): $${tattooData.pricing.small.min}-${tattooData.pricing.small.max}, `;
      answer += `Medium (3-6"): $${tattooData.pricing.medium.min}-${tattooData.pricing.medium.max}, `;
      answer += `Large (6+"): $${tattooData.pricing.large.min}-${tattooData.pricing.large.max}. `;
      suggestions.push('Get custom quote', 'See pricing examples');
    }

    // Aftercare queries
    if (lowerQuery.includes('care') || lowerQuery.includes('heal')) {
      answer += `Aftercare: ${tattooData.aftercare.immediate.join(', ')}. `;
      answer += `First week: ${tattooData.aftercare.firstWeek.join(', ')}. `;
      suggestions.push('Download aftercare guide', 'Set healing reminders');
    }

    // Default response
    if (!answer) {
      answer = 'I can help with tattoo styles, pricing, placement, and aftercare. What would you like to know?';
      suggestions.push('Browse tattoo styles', 'Get pricing info', 'Learn about aftercare');
    }

    return {
      answer: answer.trim(),
      confidence: Math.min(confidence, 1.0),
      suggestions: suggestions.slice(0, 3), // Limit suggestions for mobile
      sources,
      metadata: {
        pipeline: 'tattoo',
        processingTime: 0, // Will be set by caller
        memoryUsage: 0, // Will be set by caller
        mobileOptimized: true,
        deviceCapabilities: []
      }
    };
  }

  private async createCustomerServicePipeline(userQuery: string, context: MobileRAGContext): Promise<MobileRAGResponse> {
    const lowerQuery = userQuery.toLowerCase();
    const serviceData = this.knowledgeBase.get('customer_service');
    
    let answer = '';
    let confidence = 0.9;
    const suggestions: string[] = [];
    const sources: string[] = ['customer_service_knowledge_base'];

    if (lowerQuery.includes('book') || lowerQuery.includes('appointment')) {
      answer = `Booking is easy! ${serviceData.booking.process}. `;
      answer += `Free consultation included. `;
      suggestions.push('Book now', 'Check availability', 'Schedule consultation');
    } else if (lowerQuery.includes('cancel') || lowerQuery.includes('reschedule')) {
      answer = `${serviceData.booking.cancellation}. ${serviceData.booking.rescheduling}. `;
      suggestions.push('Cancel appointment', 'Reschedule', 'Contact support');
    } else if (lowerQuery.includes('contact') || lowerQuery.includes('help')) {
      answer = `Support: ${serviceData.support.hours}. ${serviceData.support.contact}. `;
      answer += `Response time: ${serviceData.support.response}. `;
      suggestions.push('Call support', 'Send message', 'Live chat');
    } else {
      answer = 'I can help with booking, cancellations, and support. What do you need?';
      suggestions.push('Book appointment', 'Contact support', 'View hours');
    }

    return {
      answer: answer.trim(),
      confidence,
      suggestions: suggestions.slice(0, 3),
      sources,
      metadata: {
        pipeline: 'customer_service',
        processingTime: 0,
        memoryUsage: 0,
        mobileOptimized: true,
        deviceCapabilities: []
      }
    };
  }

  private async createSalesPipeline(userQuery: string, context: MobileRAGContext): Promise<MobileRAGResponse> {
    const lowerQuery = userQuery.toLowerCase();
    const salesData = this.knowledgeBase.get('sales');
    
    let answer = '';
    let confidence = 0.9;
    const suggestions: string[] = [];
    const sources: string[] = ['sales_knowledge_base'];

    if (lowerQuery.includes('package') || lowerQuery.includes('deal')) {
      answer = `Packages: Basic (single session), Premium (multi-session with consultation), VIP (large pieces with priority booking). `;
      suggestions.push('View packages', 'Get custom quote', 'Book consultation');
    } else if (lowerQuery.includes('promotion') || lowerQuery.includes('discount')) {
      answer = `Current promotions: ${salesData.promotions.firstTime}, ${salesData.promotions.referral}, ${salesData.promotions.seasonal}. `;
      suggestions.push('Apply discount', 'Refer a friend', 'View all offers');
    } else {
      answer = 'I can help with packages, promotions, and pricing. What interests you?';
      suggestions.push('View packages', 'See promotions', 'Get quote');
    }

    return {
      answer: answer.trim(),
      confidence,
      suggestions: suggestions.slice(0, 3),
      sources,
      metadata: {
        pipeline: 'sales',
        processingTime: 0,
        memoryUsage: 0,
        mobileOptimized: true,
        deviceCapabilities: []
      }
    };
  }

  private async createConversationPipeline(userQuery: string, context: MobileRAGContext): Promise<MobileRAGResponse> {
    const conversationData = this.knowledgeBase.get('conversation');
    
    let answer = '';
    let confidence = 0.7;
    const suggestions: string[] = [];
    const sources: string[] = ['conversation_knowledge_base'];

    if (userQuery.toLowerCase().includes('hello') || userQuery.toLowerCase().includes('hi')) {
      answer = conversationData.greetings[Math.floor(Math.random() * conversationData.greetings.length)];
      suggestions.push('Book appointment', 'Get pricing', 'See designs');
    } else if (userQuery.toLowerCase().includes('thanks') || userQuery.toLowerCase().includes('thank you')) {
      answer = 'You\'re welcome! Happy to help with your tattoo needs.';
      suggestions.push('Book appointment', 'Ask more questions');
    } else {
      answer = conversationData.fallbacks[Math.floor(Math.random() * conversationData.fallbacks.length)];
      suggestions.push('Book appointment', 'Get pricing', 'Learn about aftercare');
    }

    return {
      answer: answer.trim(),
      confidence,
      suggestions: suggestions.slice(0, 3),
      sources,
      metadata: {
        pipeline: 'conversation',
        processingTime: 0,
        memoryUsage: 0,
        mobileOptimized: true,
        deviceCapabilities: []
      }
    };
  }

  private async createGeneralPipeline(userQuery: string, context: MobileRAGContext): Promise<MobileRAGResponse> {
    return {
      answer: 'I\'m here to help with your tattoo needs! Try asking about styles, pricing, booking, or aftercare.',
      confidence: 0.6,
      suggestions: ['Book appointment', 'Get pricing', 'See designs', 'Learn about aftercare'],
      sources: ['general_knowledge_base'],
      metadata: {
        pipeline: 'general',
        processingTime: 0,
        memoryUsage: 0,
        mobileOptimized: true,
        deviceCapabilities: []
      }
    };
  }

  private generateCacheKey(userQuery: string, context: MobileRAGContext): string {
    return `${userQuery.toLowerCase().substring(0, 50)}_${context.intent}_${context.useLocalModel}`;
  }

  private cacheResponse(key: string, response: MobileRAGResponse): void {
    // Limit cache size for mobile
    if (this.cache.size >= 50) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey) {
        this.cache.delete(firstKey);
      }
    }
    this.cache.set(key, response);
  }

  private getMemoryUsage(): number {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      return process.memoryUsage().heapUsed / 1024 / 1024; // MB
    }
    return 0;
  }

  private getDeviceCapabilities(): string[] {
    const capabilities: string[] = [];
    const report = this.iosOptimizer.getOptimizationReport();
    
    if (report.deviceCapabilities.hasANE) capabilities.push('ANE');
    if (report.deviceCapabilities.hasMetal) capabilities.push('Metal');
    if (report.deviceCapabilities.hasARKit) capabilities.push('ARKit');
    if (report.deviceCapabilities.hasHapticEngine) capabilities.push('Haptic');
    
    return capabilities;
  }

  // Mobile-specific methods
  clearCache(): void {
    this.cache.clear();
  }

  getCacheSize(): number {
    return this.cache.size;
  }

  getPerformanceMetrics(): {
    cacheSize: number;
    memoryUsage: number;
    knowledgeBaseSize: number;
  } {
    return {
      cacheSize: this.cache.size,
      memoryUsage: this.getMemoryUsage(),
      knowledgeBaseSize: this.knowledgeBase.size
    };
  }
}

// Export singleton instance
export const ragPipelineMobile = new MobileRAGPipeline();
export default ragPipelineMobile;
