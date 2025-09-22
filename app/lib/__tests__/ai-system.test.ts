import { apolloAI } from '../ai-system';
import { Message } from '../../types';

describe('APOLLO AI System', () => {
  beforeEach(() => {
    // Reset any state before each test
  });

  describe('processQuery', () => {
    it('should process appointment queries correctly', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await apolloAI.processQuery('I want to book an appointment', context);

      expect(result.intent).toBe('appointment');
      expect(result.response).toContain('appointment');
      expect(result.confidence).toBeGreaterThanOrEqual(0.5);
      expect(result.suggestions).toBeDefined();
      expect(result.suggestions.length).toBeGreaterThan(0);
    });

    it('should process pricing queries correctly', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await apolloAI.processQuery('How much does a tattoo cost?', context);

      expect(result.intent).toBe('pricing');
      expect(result.response).toContain('pricing');
      expect(result.confidence).toBeGreaterThanOrEqual(0.5);
    });

    it('should process design queries correctly', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await apolloAI.processQuery('I need help with a design idea', context);

      expect(result.intent).toBe('design');
      expect(result.response).toContain('styles');
      expect(result.confidence).toBeGreaterThanOrEqual(0.5);
    });

    it('should extract entities correctly', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await apolloAI.processQuery('I want a traditional tattoo on my arm', context);

      expect(result.entities.tattoo_styles).toContain('Traditional');
      expect(result.entities.body_parts).toContain('Arm');
    });

    it('should handle general queries', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await apolloAI.processQuery('Hello, how are you?', context);

      expect(result.intent).toBe('general');
      expect(result.response).toBeDefined();
      expect(result.response.length).toBeGreaterThan(0);
    });

    it('should include metadata in response', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await apolloAI.processQuery('Test query', context);

      expect(result.metadata).toBeDefined();
      expect(result.metadata.model).toBe('APOLLO-1.0.0-RAG');
      expect(result.metadata.timestamp).toBeInstanceOf(Date);
      expect(result.metadata.processingTime).toBeGreaterThanOrEqual(0);
    });
  });

  describe('memory management', () => {
    it('should store and retrieve conversation history', () => {
      const sessionId = 'test-session-123';
      const messages: Message[] = [
        {
          id: 1,
          type: 'user',
          content: 'Hello',
          timestamp: new Date()
        },
        {
          id: 2,
          type: 'ai',
          content: 'Hi there!',
          timestamp: new Date()
        }
      ];

      apolloAI.storeConversation(sessionId, messages);
      const retrieved = apolloAI.getConversationHistory(sessionId);

      expect(retrieved).toEqual(messages);
    });

    it('should return empty array for non-existent session', () => {
      const retrieved = apolloAI.getConversationHistory('non-existent');
      expect(retrieved).toEqual([]);
    });

    it('should store and retrieve user profiles', () => {
      const userId = 'user-123';
      const preferences = {
        preferredStyle: 'Traditional',
        budget: 500,
        experience: 'First time'
      };

      apolloAI.updateUserProfile(userId, preferences);
      const retrieved = apolloAI.getUserProfile(userId);

      expect(retrieved).toEqual(preferences);
    });

    it('should return empty object for non-existent user', () => {
      const retrieved = apolloAI.getUserProfile('non-existent');
      expect(retrieved).toEqual({});
    });
  });

  describe('error handling', () => {
    it('should handle empty input gracefully', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const result = await apolloAI.processQuery('', context);

      expect(result.response).toBeDefined();
      expect(result.confidence).toBeGreaterThan(0);
    });

    it('should handle very long input', async () => {
      const context = {
        conversationHistory: [],
        userPreferences: {},
        sessionData: { sessionId: 'test-session' },
        businessRules: {}
      };

      const longInput = 'a'.repeat(1000);
      const result = await apolloAI.processQuery(longInput, context);

      expect(result.response).toBeDefined();
      expect(result.confidence).toBeGreaterThan(0);
    });
  });
});
