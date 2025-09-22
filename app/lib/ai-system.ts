// APOLLO-GUIDED Advanced AI System
import { Message } from '../types';
import { ragPipeline } from './rag-pipeline';

interface AIResponse {
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
  };
}

interface AIContext {
  conversationHistory: Message[];
  userPreferences: Record<string, any>;
  sessionData: Record<string, any>;
  businessRules: Record<string, any>;
}

class ApolloAISystem {
  private knowledgeBase: Map<string, any> = new Map();
  private conversationMemory: Map<string, Message[]> = new Map();
  private userProfiles: Map<string, any> = new Map();

  constructor() {
    this.initializeKnowledgeBase();
  }

  private initializeKnowledgeBase() {
    // Tattoo-specific knowledge
    this.knowledgeBase.set('tattoo_styles', [
      'Traditional', 'Realistic', 'Geometric', 'Watercolor', 'Blackwork', 
      'Dotwork', 'Minimalist', 'Japanese', 'Tribal', 'Neo-traditional'
    ]);
    
    this.knowledgeBase.set('body_parts', [
      'Arm', 'Leg', 'Back', 'Chest', 'Shoulder', 'Wrist', 'Ankle', 
      'Neck', 'Ribcage', 'Hand', 'Foot', 'Thigh', 'Calf'
    ]);
    
    this.knowledgeBase.set('pricing_factors', [
      'Size', 'Complexity', 'Color', 'Body placement', 'Artist experience', 
      'Time required', 'Design uniqueness', 'Touch-ups needed'
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
  }

  async processQuery(input: string, context: AIContext): Promise<AIResponse> {
    const startTime = Date.now();
    
    // Preprocess input
    const processedInput = this.preprocessInput(input);
    
    // Analyze intent
    const intent = this.analyzeIntent(processedInput);
    
    // Extract entities
    const entities = this.extractEntities(processedInput);
    
    // Use RAG pipeline for enhanced responses
    try {
      const ragResponse = await ragPipeline.processQuery(processedInput, {
        ...context,
        intent,
        entities
      });
      
      return {
        response: ragResponse.answer,
        confidence: ragResponse.confidence,
        intent,
        entities,
        suggestions: ragResponse.suggestions,
        sources: ragResponse.sources,
        pipeline: ragResponse.metadata.pipeline,
        metadata: {
          processingTime: Date.now() - startTime,
          model: 'APOLLO-1.0.0-RAG',
          timestamp: new Date()
        }
      };
    } catch (error) {
      console.error('RAG pipeline error, falling back to local AI:', error);
      
      // Fallback to local AI if RAG fails
      const response = await this.generateResponse(processedInput, intent, entities, context);
      const suggestions = this.generateSuggestions(intent, entities);
      const confidence = this.calculateConfidence(intent, entities, response);
      
      return {
        response,
        confidence,
        intent,
        entities,
        suggestions,
        sources: ['local_ai'],
        pipeline: 'local_fallback',
        metadata: {
          processingTime: Date.now() - startTime,
          model: 'APOLLO-1.0.0-Local',
          timestamp: new Date()
        }
      };
    }
  }

  private preprocessInput(input: string): string {
    return input
      .toLowerCase()
      .trim()
      .replace(/[^\w\s]/g, '')
      .replace(/\s+/g, ' ');
  }

  private analyzeIntent(input: string): string {
    const intents = {
      appointment: ['book', 'schedule', 'appointment', 'reserve', 'time', 'date'],
      pricing: ['price', 'cost', 'how much', 'expensive', 'cheap', 'budget'],
      design: ['design', 'idea', 'style', 'look', 'show', 'example'],
      aftercare: ['care', 'heal', 'healing', 'after', 'maintenance', 'clean'],
      artist: ['artist', 'tattooist', 'who', 'portfolio', 'work'],
      hours: ['open', 'hours', 'time', 'when', 'available'],
      location: ['where', 'address', 'location', 'find', 'directions'],
      general: ['hello', 'hi', 'help', 'what', 'how', 'can']
    };

    for (const [intent, keywords] of Object.entries(intents)) {
      if (keywords.some(keyword => input.includes(keyword))) {
        return intent;
      }
    }

    return 'general';
  }

  private extractEntities(input: string): Record<string, any> {
    const entities: Record<string, any> = {};
    
    // Extract tattoo styles
    const styles = this.knowledgeBase.get('tattoo_styles') || [];
    const foundStyles = styles.filter((style: string) =>
      input.includes(style.toLowerCase())
    );
    if (foundStyles.length > 0) {
      entities.tattoo_styles = foundStyles;
    }
    
    // Extract body parts
    const bodyParts = this.knowledgeBase.get('body_parts') || [];
    const foundBodyParts = bodyParts.filter((part: string) =>
      input.includes(part.toLowerCase())
    );
    if (foundBodyParts.length > 0) {
      entities.body_parts = foundBodyParts;
    }
    
    // Extract size indicators
    const sizePatterns = [
      /(\d+)\s*(inch|cm|centimeter)/i,
      /(small|medium|large|tiny|huge|massive)/i,
      /(quarter|half|full)\s*(sleeve|back|chest)/i
    ];
    
    for (const pattern of sizePatterns) {
      const match = input.match(pattern);
      if (match) {
        entities.size = match[0];
        break;
      }
    }
    
    // Extract color preferences
    const colorPatterns = [
      /(black|white|color|colored|monochrome|grayscale)/i,
      /(red|blue|green|yellow|purple|orange|pink)/i
    ];
    
    for (const pattern of colorPatterns) {
      const match = input.match(pattern);
      if (match) {
        entities.color_preference = match[0];
        break;
      }
    }
    
    return entities;
  }

  private async generateResponse(
    input: string, 
    intent: string, 
    entities: Record<string, any>, 
    context: AIContext
  ): Promise<string> {
    const responses = {
      appointment: this.generateAppointmentResponse(entities),
      pricing: this.generatePricingResponse(entities),
      design: this.generateDesignResponse(entities),
      aftercare: this.generateAftercareResponse(entities),
      artist: this.generateArtistResponse(entities),
      hours: this.generateHoursResponse(),
      location: this.generateLocationResponse(),
      general: this.generateGeneralResponse(input, entities)
    };

    return responses[intent as keyof typeof responses] || responses.general;
  }

  private generateAppointmentResponse(entities: Record<string, any>): string {
    let response = "I'd be happy to help you book an appointment! ";
    
    if (entities.tattoo_styles) {
      response += `I see you're interested in ${entities.tattoo_styles.join(', ')} style tattoos. `;
    }
    
    if (entities.body_parts) {
      response += `For ${entities.body_parts.join(', ')} placement, `;
    }
    
    response += "our artists are available Tuesday-Saturday, 10am-8pm. ";
    response += "What's your preferred date and time? I can check availability and get you scheduled.";
    
    return response;
  }

  private generatePricingResponse(entities: Record<string, any>): string {
    let response = "Our pricing varies based on several factors: ";
    
    const factors = this.knowledgeBase.get('pricing_factors') || [];
    response += factors.join(', ') + ". ";
    
    if (entities.size) {
      response += `For ${entities.size} tattoos, `;
    }
    
    response += "prices typically range from $100 for small pieces to $500+ for larger, complex designs. ";
    response += "I'd recommend scheduling a consultation for an accurate quote based on your specific design and placement.";
    
    return response;
  }

  private generateDesignResponse(entities: Record<string, any>): string {
    let response = "I'd love to help with design ideas! ";
    
    if (entities.tattoo_styles) {
      response += `${entities.tattoo_styles.join(', ')} styles are fantastic choices. `;
    }
    
    if (entities.body_parts) {
      response += `For ${entities.body_parts.join(', ')} placement, `;
    }
    
    response += "our artists can work with you to create a custom design that perfectly fits your vision. ";
    response += "Would you like to see some examples from our portfolio or schedule a design consultation?";
    
    return response;
  }

  private generateAftercareResponse(entities: Record<string, any>): string {
    const steps = this.knowledgeBase.get('aftercare_steps') || [];
    let response = "Proper aftercare is crucial for healing! Here are the key steps:\n\n";
    
    steps.forEach((step: string, index: number) => {
      response += `${index + 1}. ${step}\n`;
    });
    
    response += "\nI can also send you our detailed aftercare guide via email. ";
    response += "Do you have any specific questions about the healing process?";
    
    return response;
  }

  private generateArtistResponse(entities: Record<string, any>): string {
    let response = "Our talented artists each have their own specialties and styles. ";
    
    if (entities.tattoo_styles) {
      response += `For ${entities.tattoo_styles.join(', ')} work, `;
    }
    
    response += "I can recommend the best artist for your project. ";
    response += "Would you like to see their portfolios or schedule a consultation to discuss your design?";
    
    return response;
  }

  private generateHoursResponse(): string {
    return "We're open Tuesday-Saturday, 10am-8pm. We're closed Sundays and Mondays. ";
  }

  private generateLocationResponse(): string {
    return "We're located at [Your Address]. We're easily accessible by public transport and have parking available. ";
  }

  private generateGeneralResponse(input: string, entities: Record<string, any>): string {
    if (input.includes('apollo') || input.includes('ai')) {
      return "I'm APOLLO, your AI assistant for NextEleven Tattoo Pro. I'm here to help with appointments, pricing, design consultations, aftercare, and any other questions you might have!";
    }
    
    return "I'm here to help with all your tattoo needs! Whether you want to book an appointment, get pricing information, discuss design ideas, or learn about aftercare, just let me know what you're looking for.";
  }

  private generateSuggestions(intent: string, entities: Record<string, any>): string[] {
    const suggestions: Record<string, string[]> = {
      appointment: [
        "What's your preferred date?",
        "Do you have a specific artist in mind?",
        "What type of tattoo are you planning?"
      ],
      pricing: [
        "What size are you thinking?",
        "Do you want color or black and white?",
        "Where on your body is the tattoo going?"
      ],
      design: [
        "Show me some examples",
        "I want a custom design",
        "What styles do you offer?"
      ],
      aftercare: [
        "Send me the aftercare guide",
        "How long does healing take?",
        "What products should I use?"
      ],
      artist: [
        "Show me portfolios",
        "Who specializes in [style]?",
        "Schedule a consultation"
      ]
    };

    return suggestions[intent] || [
      "Book an appointment",
      "Get pricing info",
      "See design examples",
      "Learn about aftercare"
    ];
  }

  private calculateConfidence(intent: string, entities: Record<string, any>, response: string): number {
    let confidence = 0.5; // Base confidence
    
    // Increase confidence based on entity extraction
    const entityCount = Object.keys(entities).length;
    confidence += entityCount * 0.1;
    
    // Increase confidence for specific intents
    if (intent !== 'general') {
      confidence += 0.2;
    }
    
    // Increase confidence for longer, more detailed responses
    if (response.length > 100) {
      confidence += 0.1;
    }
    
    return Math.min(confidence, 1.0);
  }

  // Memory management
  storeConversation(sessionId: string, messages: Message[]) {
    this.conversationMemory.set(sessionId, messages);
  }

  getConversationHistory(sessionId: string): Message[] {
    return this.conversationMemory.get(sessionId) || [];
  }

  // User profile management
  updateUserProfile(userId: string, preferences: Record<string, any>) {
    this.userProfiles.set(userId, preferences);
  }

  getUserProfile(userId: string): Record<string, any> {
    return this.userProfiles.get(userId) || {};
  }
}

// Export singleton instance
export const aiSystem = new ApolloAISystem();
export default aiSystem;
