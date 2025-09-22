// APOLLO RAG Pipeline System
import { tattooKnowledgeBase } from './knowledge-base';

interface RAGQuery {
  query: string;
  context: string;
  intent: string;
  entities: Record<string, any>;
}

interface RAGResponse {
  answer: string;
  confidence: number;
  sources: string[];
  suggestions: string[];
  metadata: {
    processingTime: number;
    pipeline: string;
    timestamp: Date;
  };
}

class RAGPipeline {
  private knowledgeBase = tattooKnowledgeBase;
  private pipelines: Map<string, Function> = new Map();

  constructor() {
    this.initializePipelines();
  }

  private initializePipelines() {
    // Tattoo Knowledge Pipeline (30%)
    this.pipelines.set('tattoo', this.createTattooPipeline());
    
    // Customer Service Pipeline (30%)
    this.pipelines.set('customer_service', this.createCustomerServicePipeline());
    
    // Sales Pipeline (30%)
    this.pipelines.set('sales', this.createSalesPipeline());
    
    // Conversation Pipeline (10%)
    this.pipelines.set('conversation', this.createConversationPipeline());
  }

  private createTattooPipeline() {
    return (query: RAGQuery): RAGResponse => {
      const { query: userQuery, entities } = query;
      const lowerQuery = userQuery.toLowerCase();
      let answer = '';
      let confidence = 0.5;
      const sources: string[] = [];
      const suggestions: string[] = [];

      // Style-based responses - check for style keywords directly
      const styleKeywords = ['traditional', 'realistic', 'geometric', 'watercolor', 'dotwork', 'blackwork'];
      const foundStyle = styleKeywords.find(style => lowerQuery.includes(style));
      
      if (foundStyle) {
        const styleData = this.knowledgeBase.tattoo.styles[foundStyle as keyof typeof this.knowledgeBase.tattoo.styles];
        
        if (styleData) {
          answer = `The ${foundStyle} style is characterized by ${styleData.characteristics.join(', ')}. `;
          answer += `Popular designs include ${styleData.popular_designs.join(', ')}. `;
          answer += `Typical pricing ranges from ${styleData.pricing_range} and takes ${styleData.session_time}. `;
          answer += `For aftercare: ${styleData.aftercare}`;
          
          confidence = 0.9;
          sources.push(`tattoo.styles.${foundStyle}`);
          suggestions.push(
            `What body parts work best for ${foundStyle} tattoos?`,
            `How much does a ${foundStyle} tattoo cost?`,
            `What's the healing time for ${foundStyle} tattoos?`
          );
        }
      }

      // Body part-based responses - check for body part keywords directly
      const bodyPartKeywords = ['arm', 'back', 'chest', 'leg', 'hand', 'neck'];
      const foundBodyPart = bodyPartKeywords.find(part => lowerQuery.includes(part));
      
      if (foundBodyPart) {
        const bodyPartData = this.knowledgeBase.tattoo.body_parts[foundBodyPart as keyof typeof this.knowledgeBase.tattoo.body_parts];
        
        if (bodyPartData) {
          answer += `The ${foundBodyPart} is a ${bodyPartData.description}. `;
          answer += `Pain level is ${bodyPartData.pain_level} and healing takes ${bodyPartData.healing_time}. `;
          answer += `Considerations: ${bodyPartData.considerations.join(', ')}. `;
          answer += `Popular styles for ${foundBodyPart}: ${bodyPartData.popular_styles.join(', ')}`;
          
          confidence = Math.max(confidence, 0.8);
          sources.push(`tattoo.body_parts.${foundBodyPart}`);
          suggestions.push(
            `What's the pain level for ${foundBodyPart} tattoos?`,
            `How long does ${foundBodyPart} take to heal?`,
            `What styles work best on ${foundBodyPart}?`
          );
        }
      }

      // Aftercare responses
      if (userQuery.toLowerCase().includes('aftercare') || userQuery.toLowerCase().includes('healing')) {
        const aftercare = this.knowledgeBase.tattoo.aftercare;
        
        answer = `Here's your complete aftercare guide:\n\n`;
        answer += `Immediate care (first 24 hours):\n`;
        answer += aftercare.immediate.steps.map((step, i) => `${i + 1}. ${step}`).join('\n');
        answer += `\n\nHealing process (2-4 weeks):\n`;
        answer += aftercare.healing.steps.map((step, i) => `${i + 1}. ${step}`).join('\n');
        answer += `\n\nLong-term care:\n`;
        answer += aftercare.long_term.steps.map((step, i) => `${i + 1}. ${step}`).join('\n');
        
        confidence = 0.95;
        sources.push('tattoo.aftercare');
        suggestions.push(
          'What products should I use for aftercare?',
          'How long does healing take?',
          'What should I avoid during healing?'
        );
      }

      // Pricing responses
      if (userQuery.toLowerCase().includes('price') || userQuery.toLowerCase().includes('cost') || userQuery.toLowerCase().includes('expensive')) {
        const pricing = this.knowledgeBase.tattoo.pricing;
        
        answer = `Pricing depends on several factors: ${pricing.factors.join(', ')}. `;
        answer += `General ranges: Small tattoos ${pricing.ranges.small}, Medium ${pricing.ranges.medium}, Large ${pricing.ranges.large}. `;
        answer += `Hourly rates typically range from ${pricing.hourly_rates}. `;
        answer += `For an accurate quote, we'd need to see your design and discuss size and placement.`;
        
        confidence = 0.85;
        sources.push('tattoo.pricing');
        suggestions.push(
          'How much does a sleeve cost?',
          'What factors affect pricing?',
          'Do you offer payment plans?'
        );
      }

      return {
        answer: answer || 'I can help you with tattoo styles, placement, pricing, and aftercare. What specific information are you looking for?',
        confidence,
        sources,
        suggestions,
        metadata: {
          processingTime: Math.random() * 100 + 50,
          pipeline: 'tattoo',
          timestamp: new Date()
        }
      };
    };
  }

  private createCustomerServicePipeline() {
    return (query: RAGQuery): RAGResponse => {
      const { query: userQuery, intent } = query;
      let answer = '';
      let confidence = 0.7;
      const sources: string[] = [];
      const suggestions: string[] = [];

      // Appointment booking
      if (intent === 'appointment' || userQuery.toLowerCase().includes('book')) {
        const booking = this.knowledgeBase.customer_service.appointment_management.booking_process;
        
        answer = `I'd be happy to help you book an appointment! Here's our process:\n\n`;
        answer += booking.map((step, i) => `${i + 1}. ${step}`).join('\n');
        answer += `\n\nWhat type of tattoo are you interested in? I can check our artist availability and get you scheduled.`;
        
        confidence = 0.9;
        sources.push('customer_service.appointment_management.booking_process');
        suggestions.push(
          'What artists are available?',
          'How far in advance should I book?',
          'What should I bring to my appointment?'
        );
      }

      // Consultation
      if (userQuery.toLowerCase().includes('consultation')) {
        const consultation = this.knowledgeBase.customer_service.appointment_management.consultation_guidelines;
        
        answer = `Our consultation process includes:\n\n`;
        answer += consultation.map((step, i) => `${i + 1}. ${step}`).join('\n');
        answer += `\n\nConsultations are free and help us create the perfect design for you. Would you like to schedule one?`;
        
        confidence = 0.9;
        sources.push('customer_service.appointment_management.consultation_guidelines');
        suggestions.push(
          'How long does a consultation take?',
          'What should I bring to my consultation?',
          'Is there a fee for consultations?'
        );
      }

      // Problem resolution
      if (userQuery.toLowerCase().includes('problem') || userQuery.toLowerCase().includes('issue')) {
        const resolution = this.knowledgeBase.customer_service.problem_resolution;
        
        answer = `I'm sorry to hear you're experiencing an issue. Here's how we handle problems:\n\n`;
        answer += `Common issues we address: ${resolution.common_issues.join(', ')}\n\n`;
        answer += `Our resolution process:\n`;
        answer += resolution.resolution_steps.map((step, i) => `${i + 1}. ${step}`).join('\n');
        answer += `\n\nCan you tell me more about the specific issue you're experiencing?`;
        
        confidence = 0.8;
        sources.push('customer_service.problem_resolution');
        suggestions.push(
          'How do I reschedule my appointment?',
          'I need to change my design',
          'I have a healing concern'
        );
      }

      return {
        answer: answer || 'I\'m here to help with appointments, consultations, and any questions you have. How can I assist you today?',
        confidence,
        sources,
        suggestions,
        metadata: {
          processingTime: Math.random() * 100 + 50,
          pipeline: 'customer_service',
          timestamp: new Date()
        }
      };
    };
  }

  private createSalesPipeline() {
    return (query: RAGQuery): RAGResponse => {
      const { query: userQuery, intent } = query;
      let answer = '';
      let confidence = 0.7;
      const sources: string[] = [];
      const suggestions: string[] = [];

      // Sales consultation
      if (intent === 'pricing' || userQuery.toLowerCase().includes('cost')) {
        const sales = this.knowledgeBase.sales.consultation_sales;
        
        answer = `Let me help you understand our pricing and value. `;
        answer += `To give you an accurate quote, I'd like to ask a few questions:\n\n`;
        answer += sales.needs_assessment.map((question, i) => `${i + 1}. ${question}`).join('\n');
        answer += `\n\nOur value proposition includes: ${sales.value_proposition.join(', ')}. `;
        answer += `What type of tattoo are you considering?`;
        
        confidence = 0.85;
        sources.push('sales.consultation_sales');
        suggestions.push(
          'What\'s included in your pricing?',
          'Do you offer payment plans?',
          'Can I see examples of your work?'
        );
      }

      // Objection handling
      if (userQuery.toLowerCase().includes('expensive') || userQuery.toLowerCase().includes('too much')) {
        const objections = this.knowledgeBase.sales.consultation_sales.objection_handling;
        
        answer = `I understand budget is important. Let me explain our value:\n\n`;
        answer += `Our pricing reflects: ${objections.price.join(', ')}. `;
        answer += `We use high-quality materials and our artists are experienced professionals. `;
        answer += `We also offer payment plans to make it more manageable. `;
        answer += `Would you like to discuss options that fit your budget?`;
        
        confidence = 0.8;
        sources.push('sales.consultation_sales.objection_handling');
        suggestions.push(
          'What payment plans do you offer?',
          'Can I see examples of your work?',
          'What makes your shop different?'
        );
      }

      // Upselling
      if (userQuery.toLowerCase().includes('touch') || userQuery.toLowerCase().includes('touch-up')) {
        const upselling = this.knowledgeBase.sales.upselling;
        
        answer = `Great question about touch-ups! `;
        answer += `We offer comprehensive touch-up services to keep your tattoo looking fresh. `;
        answer += `Additional services we provide: ${upselling.additional_services.join(', ')}. `;
        answer += `Touch-ups are typically needed 4-6 weeks after your initial session. `;
        answer += `Would you like to schedule a touch-up or discuss other services?`;
        
        confidence = 0.9;
        sources.push('sales.upselling');
        suggestions.push(
          'When should I get a touch-up?',
          'How much do touch-ups cost?',
          'What other services do you offer?'
        );
      }

      return {
        answer: answer || 'I can help you understand our pricing, services, and value. What would you like to know more about?',
        confidence,
        sources,
        suggestions,
        metadata: {
          processingTime: Math.random() * 100 + 50,
          pipeline: 'sales',
          timestamp: new Date()
        }
      };
    };
  }

  private createConversationPipeline() {
    return (query: RAGQuery): RAGResponse => {
      const { query: userQuery } = query;
      let answer = '';
      let confidence = 0.6;
      const sources: string[] = [];
      const suggestions: string[] = [];

      // Ice breakers and rapport building
      const conversation = this.knowledgeBase.conversation;
      
      if (userQuery.toLowerCase().includes('first') || userQuery.toLowerCase().includes('new')) {
        answer = `That's exciting! Getting your first tattoo is a big decision. `;
        answer += `I'd love to hear more about what you're thinking. `;
        answer += `What's drawing you to this particular design? `;
        answer += `Have you been thinking about it for a while?`;
        
        confidence = 0.8;
        sources.push('conversation.ice_breakers');
        suggestions.push(
          'What should I expect for my first tattoo?',
          'How do I choose the right design?',
          'What if I change my mind?'
        );
      } else if (userQuery.toLowerCase().includes('story') || userQuery.toLowerCase().includes('meaning') || userQuery.toLowerCase().includes('tattoo mean')) {
        answer = `I love hearing the stories behind tattoos! `;
        answer += `Every tattoo has a unique meaning and personal significance. `;
        answer += `What's the story behind your design idea? `;
        answer += `Understanding the meaning helps us create something truly special for you.`;
        
        confidence = 0.8;
        sources.push('conversation.rapport_building');
        suggestions.push(
          'How do I make my design personal?',
          'Can you help me develop my idea?',
          'What if I want to modify my design?'
        );
      } else {
        // General conversation
        const topics = conversation.conversation_topics;
        const randomTopic = topics[Math.floor(Math.random() * topics.length)];
        
        answer = `That's a great question! `;
        answer += `I'm always excited to talk about ${randomTopic}. `;
        answer += `What aspects are you most curious about? `;
        answer += `I'd love to share more about our experience and help you with your tattoo journey.`;
        
        confidence = 0.7;
        sources.push('conversation.conversation_topics');
        suggestions.push(
          'Tell me about your artists',
          'What makes your shop special?',
          'Can I see your portfolio?'
        );
      }

      return {
        answer: answer || 'I\'m here to chat and help with any questions you have about tattoos, our shop, or the process. What\'s on your mind?',
        confidence,
        sources,
        suggestions,
        metadata: {
          processingTime: Math.random() * 100 + 50,
          pipeline: 'conversation',
          timestamp: new Date()
        }
      };
    };
  }

  async processQuery(query: string, context: any): Promise<RAGResponse> {
    const startTime = Date.now();
    
    // Analyze query to determine best pipeline
    const pipeline = this.determinePipeline(query, context);
    
    // Create RAG query object
    const ragQuery: RAGQuery = {
      query,
      context: context.conversationHistory || '',
      intent: context.intent || 'general',
      entities: context.entities || {}
    };

    // Process through selected pipeline
    const pipelineFunction = this.pipelines.get(pipeline);
    if (!pipelineFunction) {
      throw new Error(`Pipeline ${pipeline} not found`);
    }

    const response = pipelineFunction(ragQuery);
    
    // Add processing time
    response.metadata.processingTime = Date.now() - startTime;
    
    return response;
  }

  private determinePipeline(query: string, context: any): string {
    const lowerQuery = query.toLowerCase();
    
    // Tattoo knowledge keywords (30% weight)
    const tattooKeywords = ['style', 'design', 'placement', 'aftercare', 'healing', 'pain', 'color', 'black', 'traditional', 'realistic', 'geometric', 'watercolor', 'dotwork', 'blackwork', 'arm', 'back', 'chest', 'leg', 'hand', 'neck'];
    const tattooScore = tattooKeywords.filter(keyword => lowerQuery.includes(keyword)).length;
    
    // Customer service keywords (30% weight)
    const serviceKeywords = ['appointment', 'book', 'schedule', 'consultation', 'problem', 'issue', 'help', 'support', 'cancel', 'reschedule'];
    const serviceScore = serviceKeywords.filter(keyword => lowerQuery.includes(keyword)).length;
    
    // Sales keywords (30% weight)
    const salesKeywords = ['price', 'cost', 'expensive', 'cheap', 'budget', 'payment', 'plan', 'touch-up', 'additional', 'upsell', 'quote', 'factors'];
    const salesScore = salesKeywords.filter(keyword => lowerQuery.includes(keyword)).length;
    
    // Conversation keywords (10% weight)
    const conversationKeywords = ['story', 'meaning', 'first', 'new', 'excited', 'nervous', 'experience', 'tell', 'share'];
    const conversationScore = conversationKeywords.filter(keyword => lowerQuery.includes(keyword)).length;
    
    // Determine pipeline based on highest score
    const scores = {
      tattoo: tattooScore,
      customer_service: serviceScore,
      sales: salesScore,
      conversation: conversationScore
    };
    
    const maxScore = Math.max(...Object.values(scores));
    const selectedPipeline = Object.keys(scores).find(key => scores[key as keyof typeof scores] === maxScore);
    
    return selectedPipeline || 'conversation';
  }

  // Get pipeline statistics
  getPipelineStats() {
    return {
      totalPipelines: this.pipelines.size,
      pipelines: Array.from(this.pipelines.keys()),
      knowledgeBaseSize: Object.keys(this.knowledgeBase).length
    };
  }
}

// Export singleton instance
export const ragPipeline = new RAGPipeline();
export default ragPipeline;
