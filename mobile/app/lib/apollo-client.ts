import { Message } from '../types';

interface ApolloResponse {
  response: string;
  confidence: number;
  suggestions?: string[];
  intent?: string;
  entities?: any[];
}

interface ApolloConfig {
  baseUrl: string;
  apiKey: string;
  model: string;
}

class ApolloClient {
  private config: ApolloConfig;
  private conversationHistory: Message[] = [];

  constructor() {
    this.config = {
      baseUrl: process.env.APOLLO_BASE_URL || 'http://localhost:8000',
      apiKey: process.env.APOLLO_API_KEY || 'nexteleven-crowley-edition-2024',
      model: process.env.APOLLO_MODEL || 'llama3.2:3b'
    };
  }

  async query(input: string, conversationHistory: Message[] = []): Promise<ApolloResponse> {
    try {
      // Store conversation history
      this.conversationHistory = conversationHistory;

      // Try to connect to APOLLO server first
      const apolloResponse = await this.queryApolloServer(input);
      if (apolloResponse) {
        return apolloResponse;
      }

      // Fallback to local processing
      return this.processLocally(input);
    } catch (error) {
      console.error('APOLLO query error:', error);
      return this.processLocally(input);
    }
  }

  private async queryApolloServer(input: string): Promise<ApolloResponse | null> {
    try {
      const response = await fetch(`${this.config.baseUrl}/apollo/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify({
          query: input,
          conversation_history: this.conversationHistory,
          model: this.config.model,
          context: 'tattoo_professional_assistant'
        })
      });

      if (!response.ok) {
        throw new Error(`APOLLO server error: ${response.status}`);
      }

      const data = await response.json();
      return {
        response: data.response || data.message || 'I understand your request.',
        confidence: data.confidence || 0.9,
        suggestions: data.suggestions || [],
        intent: data.intent || 'general',
        entities: data.entities || []
      };
    } catch (error) {
      console.log('APOLLO server not available, using local processing');
      return null;
    }
  }

  private processLocally(input: string): ApolloResponse {
    const lowerInput = input.toLowerCase();
    
    // Enhanced local processing with APOLLO-style responses
    let response = 'Thank you for your message! I\'m APOLLO, your advanced AI assistant for NextEleven Tattoo Pro. ';
    let confidence = 0.8;
    let intent = 'general';
    let suggestions: string[] = [];
    let entities: any[] = [];

    // Intent detection and response generation
    if (lowerInput.includes('apollo') || lowerInput.includes('ai') || lowerInput.includes('assistant')) {
      response = 'I am APOLLO, a hybrid LLM/RAG system designed for advanced AI interactions. I can help you with appointments, design consultations, aftercare guidance, pricing estimates, and any tattoo-related questions. How can I assist you today?';
      confidence = 0.95;
      intent = 'system_info';
      suggestions = ['Book an appointment', 'Get pricing information', 'Learn about aftercare', 'View artist portfolios'];
    } else if (lowerInput.includes('appointment') || lowerInput.includes('book') || lowerInput.includes('schedule')) {
      response = 'I can help you schedule an appointment! Our artists are available Tuesday-Saturday, 10am-8pm. What type of tattoo are you interested in? I can also help you choose an artist based on your preferred style.';
      confidence = 0.9;
      intent = 'appointment_booking';
      suggestions = ['View available artists', 'Check availability', 'Get price estimate', 'Choose tattoo style'];
      entities = [{ type: 'intent', value: 'appointment_booking' }];
    } else if (lowerInput.includes('price') || lowerInput.includes('cost') || lowerInput.includes('how much')) {
      response = 'Our pricing varies based on size, complexity, and placement. Small tattoos start at $100, medium pieces range $200-500, and large work can be $500+. A consultation will give you an exact quote. Would you like to schedule a consultation?';
      confidence = 0.9;
      intent = 'pricing_inquiry';
      suggestions = ['Schedule consultation', 'View pricing guide', 'Get custom quote', 'See portfolio examples'];
    } else if (lowerInput.includes('design') || lowerInput.includes('idea') || lowerInput.includes('style')) {
      response = 'I\'d love to help with design ideas! We specialize in traditional, realistic, geometric, watercolor, and custom designs. What style interests you? I can also connect you with our artists who specialize in specific styles.';
      confidence = 0.9;
      intent = 'design_consultation';
      suggestions = ['View artist portfolios', 'Browse style gallery', 'Schedule design consultation', 'Get custom design quote'];
    } else if (lowerInput.includes('aftercare') || lowerInput.includes('care') || lowerInput.includes('healing')) {
      response = 'Proper aftercare is crucial for beautiful healing! Keep your tattoo clean and moisturized, avoid sun exposure, and follow our detailed aftercare instructions. I can send you our comprehensive guide and schedule check-in reminders.';
      confidence = 0.95;
      intent = 'aftercare_guidance';
      suggestions = ['Download aftercare guide', 'Schedule check-in', 'Ask specific questions', 'View healing timeline'];
    } else if (lowerInput.includes('artist') || lowerInput.includes('portfolio') || lowerInput.includes('work')) {
      response = 'Our artists are highly skilled professionals with diverse specialties. I can show you portfolios, help you find an artist who matches your style, and provide information about their availability and rates.';
      confidence = 0.9;
      intent = 'artist_inquiry';
      suggestions = ['View all artists', 'Filter by specialty', 'Check availability', 'See recent work'];
    } else if (lowerInput.includes('pain') || lowerInput.includes('hurt') || lowerInput.includes('uncomfortable')) {
      response = 'Tattoo pain varies by location and individual tolerance. I can explain what to expect, suggest less sensitive areas for first tattoos, and provide tips for managing discomfort during your session.';
      confidence = 0.9;
      intent = 'pain_inquiry';
      suggestions = ['Learn about pain levels', 'Find less sensitive areas', 'Get pain management tips', 'Schedule consultation'];
    } else if (lowerInput.includes('time') || lowerInput.includes('long') || lowerInput.includes('duration')) {
      response = 'Session duration depends on size and complexity. Small tattoos take 1-2 hours, medium pieces 2-4 hours, and large work can be 4+ hours or multiple sessions. I can give you a more specific estimate based on your design.';
      confidence = 0.9;
      intent = 'duration_inquiry';
      suggestions = ['Get time estimate', 'Plan multiple sessions', 'Check artist availability', 'Schedule consultation'];
    } else if (lowerInput.includes('cancel') || lowerInput.includes('reschedule') || lowerInput.includes('change')) {
      response = 'I can help you cancel or reschedule your appointment. Please provide your appointment details, and I\'ll assist you with the process. We have a 24-hour cancellation policy.';
      confidence = 0.9;
      intent = 'appointment_management';
      suggestions = ['View my appointments', 'Reschedule appointment', 'Cancel appointment', 'Contact support'];
    } else {
      // General response with APOLLO personality
      response = 'I\'m here to help with all your tattoo needs! Whether you\'re looking to book an appointment, get design advice, learn about aftercare, or have any questions about our services, I\'m ready to assist. What would you like to know?';
      confidence = 0.8;
      intent = 'general_inquiry';
      suggestions = ['Book appointment', 'View artists', 'Get pricing', 'Learn about aftercare', 'Ask questions'];
    }

    return {
      response,
      confidence,
      suggestions,
      intent,
      entities
    };
  }

  // Method to get conversation context
  getConversationContext(): string {
    if (this.conversationHistory.length === 0) {
      return 'No previous conversation context.';
    }

    const recentMessages = this.conversationHistory.slice(-5); // Last 5 messages
    return recentMessages.map(msg => 
      `${msg.type}: ${msg.content}`
    ).join('\n');
  }

  // Method to clear conversation history
  clearHistory(): void {
    this.conversationHistory = [];
  }

  // Method to get system status
  async getSystemStatus(): Promise<{ status: string; capabilities: string[] }> {
    return {
      status: 'operational',
      capabilities: [
        'appointment_booking',
        'pricing_estimation',
        'design_consultation',
        'aftercare_guidance',
        'artist_recommendation',
        'pain_management_advice',
        'general_inquiry_handling'
      ]
    };
  }
}

// Export singleton instance
export const apolloClient = new ApolloClient();

// Export class for testing
export { ApolloClient };