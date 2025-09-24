import { ragPipeline } from '../rag-pipeline';

describe('RAG Pipeline System', () => {
  beforeEach(() => {
    // Reset any state before each test
  });

  describe('Pipeline Selection', () => {
    it('should select tattoo pipeline for tattoo-related queries', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('What is traditional tattoo style?', context);

      expect(result.metadata.pipeline).toBe('tattoo');
      expect(result.answer).toContain('traditional');
      expect(result.confidence).toBeGreaterThan(0.5);
    });

    it('should select customer service pipeline for appointment queries', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('I want to book an appointment', context);

      expect(result.metadata.pipeline).toBe('customer_service');
      expect(result.answer).toContain('appointment');
      expect(result.confidence).toBeGreaterThan(0.5);
    });

    it('should select sales pipeline for pricing queries', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('How much does a tattoo cost?', context);

      expect(result.metadata.pipeline).toBe('sales');
      expect(result.answer).toContain('pricing');
      expect(result.confidence).toBeGreaterThan(0.5);
    });

    it('should select conversation pipeline for general queries', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('Tell me about your shop', context);

      expect(result.metadata.pipeline).toBe('conversation');
      expect(result.answer).toBeDefined();
      expect(result.confidence).toBeGreaterThan(0.5);
    });
  });

  describe('Tattoo Knowledge Pipeline', () => {
    it('should provide detailed style information', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('What is realistic tattoo style?', context);

      expect(result.answer).toContain('realistic');
      expect(result.answer).toContain('characterized by');
      expect(result.answer).toContain('pricing');
      expect(result.sources).toContain('tattoo.styles.realistic');
    });

    it('should provide body part information', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('What about arm tattoos?', context);

      expect(result.answer).toContain('arm');
      expect(result.answer).toContain('Pain level');
      expect(result.answer).toContain('healing');
      expect(result.sources).toContain('tattoo.body_parts.arm');
    });

    it('should provide comprehensive aftercare information', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('What is the aftercare for tattoos?', context);

      expect(result.answer).toContain('aftercare');
      expect(result.answer).toContain('24 hours');
      expect(result.answer).toContain('healing');
      expect(result.sources).toContain('tattoo.aftercare');
    });
  });

  describe('Customer Service Pipeline', () => {
    it('should handle appointment booking queries', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('I want to book an appointment', context);

      expect(result.answer).toContain('appointment');
      expect(result.answer).toContain('process');
      expect(result.sources).toContain('customer_service.appointment_management.booking_process');
    });

    it('should handle consultation requests', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('I need a consultation', context);

      expect(result.answer).toContain('consultation');
      expect(result.answer).toContain('free');
      expect(result.sources).toContain('customer_service.appointment_management.consultation_guidelines');
    });

    it('should handle problem resolution', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('I have a problem with my appointment', context);

      expect(result.answer).toContain('issue');
      expect(result.answer).toContain('resolution');
      expect(result.sources).toContain('customer_service.problem_resolution');
    });
  });

  describe('Sales Pipeline', () => {
    it('should handle pricing inquiries', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('How much does a tattoo cost?', context);

      expect(result.answer).toContain('pricing');
      expect(result.answer).toContain('questions');
      expect(result.answer).toContain('quote');
      expect(result.sources).toContain('sales.consultation_sales');
    });

    it('should handle price objections', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('That seems too expensive', context);

      expect(result.answer).toContain('budget');
      expect(result.answer).toContain('value');
      expect(result.answer).toContain('payment plans');
      expect(result.sources).toContain('sales.consultation_sales.objection_handling');
    });

    it('should handle upselling opportunities', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('Do you offer touch-ups?', context);

      expect(result.answer).toContain('touch-up');
      expect(result.answer).toContain('services');
      expect(result.sources).toContain('sales.upselling');
    });
  });

  describe('Conversation Pipeline', () => {
    it('should handle first-time customer conversations', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('This is my first tattoo', context);

      expect(result.answer).toContain('first');
      expect(result.answer).toContain('exciting');
      expect(result.answer).toContain('decision');
    });

    it('should handle story-based conversations', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('Tell me about your experience with tattoos', context);

      expect(result.answer).toContain('question');
      expect(result.answer).toContain('tattoo');
      expect(result.answer).toContain('help');
    });
  });

  describe('Pipeline Statistics', () => {
    it('should return pipeline statistics', () => {
      const stats = ragPipeline.getPipelineStats();

      expect(stats.totalPipelines).toBe(4);
      expect(stats.pipelines).toContain('tattoo');
      expect(stats.pipelines).toContain('customer_service');
      expect(stats.pipelines).toContain('sales');
      expect(stats.pipelines).toContain('conversation');
      expect(stats.knowledgeBaseSize).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    it('should handle empty queries gracefully', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('', context);

      expect(result.answer).toBeDefined();
      expect(result.confidence).toBeGreaterThan(0);
    });

    it('should handle malformed queries', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await ragPipeline.processQuery('asdfghjkl', context);

      expect(result.answer).toBeDefined();
      expect(result.confidence).toBeGreaterThan(0);
    });
  });
});
