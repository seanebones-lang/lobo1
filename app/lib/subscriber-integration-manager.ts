// APOLLO-GUIDED Subscriber Integration Manager
// Handles payment methods, calendar integration, and feature access management

import React from 'react';

export interface PaymentMethod {
  id: string;
  type: 'credit_card' | 'debit_card' | 'paypal' | 'apple_pay' | 'google_pay' | 'crypto' | 'bank_transfer';
  provider: 'stripe' | 'paypal' | 'square' | 'apple' | 'google' | 'coinbase' | 'bank';
  last4?: string;
  brand?: string;
  expiryMonth?: number;
  expiryYear?: number;
  isDefault: boolean;
  isVerified: boolean;
  createdAt: number;
  updatedAt: number;
}

export interface CalendarIntegration {
  id: string;
  provider: 'google' | 'outlook' | 'apple' | 'calendly' | 'acuity' | 'square';
  calendarId: string;
  calendarName: string;
  accessToken: string;
  refreshToken?: string;
  isActive: boolean;
  syncEnabled: boolean;
  lastSyncAt?: number;
  createdAt: number;
}

export interface FeatureAccess {
  featureId: string;
  featureName: string;
  isEnabled: boolean;
  tier: 'basic' | 'premium' | 'pro';
  limits?: {
    maxAppointments?: number;
    maxStorage?: number; // in MB
    maxIntegrations?: number;
    maxTeamMembers?: number;
    maxDeposits?: number;
    maxScheduling?: number;
    maxClients?: number;
    maxPortfolio?: number;
  };
  usage?: {
    currentAppointments?: number;
    currentStorage?: number;
    currentIntegrations?: number;
    currentTeamMembers?: number;
    currentDeposits?: number;
    currentScheduling?: number;
    currentClients?: number;
    currentPortfolio?: number;
  };
}

export interface SubscriberPreferences {
  userId: string;
  subscriptionTier: 'basic' | 'premium' | 'pro';
  paymentMethods: PaymentMethod[];
  calendarIntegrations: CalendarIntegration[];
  featureAccess: FeatureAccess[];
  notifications: {
    email: boolean;
    sms: boolean;
    push: boolean;
    appointmentReminders: boolean;
    paymentAlerts: boolean;
    systemUpdates: boolean;
  };
  privacy: {
    dataSharing: boolean;
    analytics: boolean;
    marketing: boolean;
  };
  createdAt: number;
  updatedAt: number;
}

class ApolloSubscriberIntegrationManager {
  private subscribers: Map<string, SubscriberPreferences> = new Map();
  private readonly STORAGE_KEY = 'apollo_subscriber_preferences';

  constructor() {
    this.loadSubscriberData();
    console.log('🌊 Tattoo App Subscriber Integration Manager: Initialized');
  }

  // Load subscriber data from localStorage
  private loadSubscriberData(): void {
    if (typeof window === 'undefined') return;
    
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const data = JSON.parse(stored);
        this.subscribers = new Map(Object.entries(data));
        console.log(`🌊 APOLLO Subscriber Manager: Loaded ${this.subscribers.size} subscriber profiles`);
      }
    } catch (error) {
      console.error('❌ APOLLO Subscriber Manager: Failed to load subscriber data', error);
    }
  }

  // Save subscriber data to localStorage
  private saveSubscriberData(): void {
    if (typeof window === 'undefined') return;
    
    try {
      const data = Object.fromEntries(this.subscribers);
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('❌ APOLLO Subscriber Manager: Failed to save subscriber data', error);
    }
  }

  // Get or create subscriber preferences
  getSubscriberPreferences(userId: string): SubscriberPreferences {
    if (!this.subscribers.has(userId)) {
      this.subscribers.set(userId, this.createDefaultPreferences(userId));
    }
    return this.subscribers.get(userId)!;
  }

  // Create default preferences for new subscriber
  private createDefaultPreferences(userId: string): SubscriberPreferences {
    return {
      userId,
      subscriptionTier: 'basic',
      paymentMethods: [],
      calendarIntegrations: [],
      featureAccess: this.getDefaultFeatureAccess('basic'),
      notifications: {
        email: true,
        sms: false,
        push: true,
        appointmentReminders: true,
        paymentAlerts: true,
        systemUpdates: true,
      },
      privacy: {
        dataSharing: false,
        analytics: true,
        marketing: false,
      },
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
  }

  // Get default feature access based on tier
  private getDefaultFeatureAccess(tier: 'basic' | 'premium' | 'pro'): FeatureAccess[] {
    const baseFeatures = [
      { featureId: 'ai_chat', featureName: 'AI Chat Assistant', isEnabled: true, tier: 'basic' as const },
      { featureId: 'basic_analytics', featureName: 'Basic Analytics', isEnabled: true, tier: 'basic' as const },
      { featureId: 'contact_form', featureName: 'Contact Form', isEnabled: true, tier: 'basic' as const },
    ];

    // Premium and Pro get ALL features enabled
    const premiumFeatures = [
      { featureId: 'appointment_booking', featureName: 'Appointment Booking', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'deposit_collection', featureName: 'Deposit Collection', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'advanced_scheduling', featureName: 'Advanced Scheduling', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'advanced_analytics', featureName: 'Advanced Analytics', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'calendar_sync', featureName: 'Calendar Synchronization', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'payment_processing', featureName: 'Payment Processing', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'custom_branding', featureName: 'Custom Branding', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'client_management', featureName: 'Client Management', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'portfolio_showcase', featureName: 'Portfolio Showcase', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'aftercare_guides', featureName: 'Aftercare Guides', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'pricing_calculator', featureName: 'Pricing Calculator', isEnabled: tier !== 'basic', tier: 'premium' as const },
      { featureId: 'artist_profiles', featureName: 'Artist Profiles', isEnabled: tier !== 'basic', tier: 'premium' as const },
    ];

    // Pro gets everything plus additional features
    const proFeatures = [
      { featureId: 'api_access', featureName: 'API Access', isEnabled: tier === 'pro', tier: 'pro' as const },
      { featureId: 'white_label', featureName: 'White Label Solution', isEnabled: tier === 'pro', tier: 'pro' as const },
      { featureId: 'priority_support', featureName: 'Priority Support', isEnabled: tier === 'pro', tier: 'pro' as const },
      { featureId: 'unlimited_integrations', featureName: 'Unlimited Integrations', isEnabled: tier === 'pro', tier: 'pro' as const },
      { featureId: 'multi_location', featureName: 'Multi-Location Support', isEnabled: tier === 'pro', tier: 'pro' as const },
      { featureId: 'advanced_reporting', featureName: 'Advanced Reporting', isEnabled: tier === 'pro', tier: 'pro' as const },
      { featureId: 'team_management', featureName: 'Team Management', isEnabled: tier === 'pro', tier: 'pro' as const },
    ];

    return [...baseFeatures, ...premiumFeatures, ...proFeatures].map(feature => ({
      ...feature,
      limits: this.getFeatureLimits(feature.tier),
      usage: this.getDefaultUsage(),
    }));
  }

  // Get feature limits based on tier
  private getFeatureLimits(tier: 'basic' | 'premium' | 'pro') {
    const limits = {
      basic: { 
        maxAppointments: 0, // No appointments for basic
        maxStorage: 100, // Very limited storage
        maxIntegrations: 0, // No integrations for basic
        maxTeamMembers: 1,
        maxDeposits: 0, // No deposit collection
        maxScheduling: 0, // No advanced scheduling
        maxClients: 10, // Limited client management
        maxPortfolio: 5, // Limited portfolio items
      },
      premium: { 
        maxAppointments: 200, 
        maxStorage: 5000, 
        maxIntegrations: 5, 
        maxTeamMembers: 3,
        maxDeposits: -1, // Unlimited deposits
        maxScheduling: -1, // Unlimited scheduling
        maxClients: 500, // More clients
        maxPortfolio: 100, // More portfolio items
      },
      pro: { 
        maxAppointments: -1, 
        maxStorage: -1, 
        maxIntegrations: -1, 
        maxTeamMembers: -1,
        maxDeposits: -1, // Unlimited everything
        maxScheduling: -1,
        maxClients: -1,
        maxPortfolio: -1,
      }, // -1 = unlimited
    };
    return limits[tier];
  }

  // Get default usage
  private getDefaultUsage() {
    return {
      currentAppointments: 0,
      currentStorage: 0,
      currentIntegrations: 0,
      currentTeamMembers: 1,
      currentDeposits: 0,
      currentScheduling: 0,
      currentClients: 0,
      currentPortfolio: 0,
    };
  }

  // Add payment method
  async addPaymentMethod(userId: string, paymentData: Partial<PaymentMethod>): Promise<PaymentMethod> {
    const preferences = this.getSubscriberPreferences(userId);
    
    const paymentMethod: PaymentMethod = {
      id: `pm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: paymentData.type || 'credit_card',
      provider: paymentData.provider || 'stripe',
      last4: paymentData.last4,
      brand: paymentData.brand,
      expiryMonth: paymentData.expiryMonth,
      expiryYear: paymentData.expiryYear,
      isDefault: preferences.paymentMethods.length === 0,
      isVerified: false,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    // Verify payment method with provider
    const verificationResult = await this.verifyPaymentMethod(paymentMethod);
    paymentMethod.isVerified = verificationResult.success;

    preferences.paymentMethods.push(paymentMethod);
    preferences.updatedAt = Date.now();
    this.subscribers.set(userId, preferences);
    this.saveSubscriberData();

    console.log(`🌊 APOLLO Subscriber Manager: Added payment method for user ${userId}`);
    return paymentMethod;
  }

  // Verify payment method with provider
  private async verifyPaymentMethod(paymentMethod: PaymentMethod): Promise<{ success: boolean; error?: string }> {
    try {
      // Simulate API call to payment provider
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock verification logic
      const isValid = Math.random() > 0.1; // 90% success rate for demo
      return { success: isValid };
    } catch (error) {
      return { success: false, error: 'Verification failed' };
    }
  }

  // Add calendar integration
  async addCalendarIntegration(userId: string, integrationData: Partial<CalendarIntegration>): Promise<CalendarIntegration> {
    const preferences = this.getSubscriberPreferences(userId);
    
    const integration: CalendarIntegration = {
      id: `cal_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      provider: integrationData.provider || 'google',
      calendarId: integrationData.calendarId || '',
      calendarName: integrationData.calendarName || 'Default Calendar',
      accessToken: integrationData.accessToken || '',
      refreshToken: integrationData.refreshToken,
      isActive: true,
      syncEnabled: true,
      createdAt: Date.now(),
    };

    // Test calendar connection
    const connectionResult = await this.testCalendarConnection(integration);
    integration.isActive = connectionResult.success;

    preferences.calendarIntegrations.push(integration);
    preferences.updatedAt = Date.now();
    this.subscribers.set(userId, preferences);
    this.saveSubscriberData();

    console.log(`🌊 APOLLO Subscriber Manager: Added calendar integration for user ${userId}`);
    return integration;
  }

  // Test calendar connection
  private async testCalendarConnection(integration: CalendarIntegration): Promise<{ success: boolean; error?: string }> {
    try {
      // Simulate API call to calendar provider
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock connection test
      const isConnected = Math.random() > 0.05; // 95% success rate for demo
      return { success: isConnected };
    } catch (error) {
      return { success: false, error: 'Connection test failed' };
    }
  }

  // Update subscription tier
  async updateSubscriptionTier(userId: string, newTier: 'basic' | 'premium' | 'pro'): Promise<SubscriberPreferences> {
    const preferences = this.getSubscriberPreferences(userId);
    preferences.subscriptionTier = newTier;
    preferences.featureAccess = this.getDefaultFeatureAccess(newTier);
    preferences.updatedAt = Date.now();
    
    this.subscribers.set(userId, preferences);
    this.saveSubscriberData();

    console.log(`🌊 APOLLO Subscriber Manager: Updated subscription tier to ${newTier} for user ${userId}`);
    return preferences;
  }

  // Check feature access
  hasFeatureAccess(userId: string, featureId: string): boolean {
    const preferences = this.getSubscriberPreferences(userId);
    const feature = preferences.featureAccess.find(f => f.featureId === featureId);
    return feature ? feature.isEnabled : false;
  }

  // Check usage limits
  checkUsageLimit(userId: string, featureId: string): { allowed: boolean; remaining?: number } {
    const preferences = this.getSubscriberPreferences(userId);
    const feature = preferences.featureAccess.find(f => f.featureId === featureId);
    
    // First check if the feature is enabled for this tier
    if (!feature || !feature.isEnabled) {
      return { allowed: false, remaining: 0 };
    }

    if (!feature.limits) {
      return { allowed: true };
    }

    const limits = feature.limits;
    const usage = feature.usage || this.getDefaultUsage();

    // Check specific limits based on feature
    if (featureId.includes('appointment') && limits.maxAppointments !== undefined) {
      const remaining = limits.maxAppointments === -1 ? -1 : limits.maxAppointments - (usage.currentAppointments || 0);
      return { allowed: remaining === -1 || remaining > 0, remaining };
    }

    if (featureId.includes('deposit') && limits.maxDeposits !== undefined) {
      const remaining = limits.maxDeposits === -1 ? -1 : limits.maxDeposits - (usage.currentDeposits || 0);
      return { allowed: remaining === -1 || remaining > 0, remaining };
    }

    if (featureId.includes('scheduling') && limits.maxScheduling !== undefined) {
      const remaining = limits.maxScheduling === -1 ? -1 : limits.maxScheduling - (usage.currentScheduling || 0);
      return { allowed: remaining === -1 || remaining > 0, remaining };
    }

    if (featureId.includes('client') && limits.maxClients !== undefined) {
      const remaining = limits.maxClients === -1 ? -1 : limits.maxClients - (usage.currentClients || 0);
      return { allowed: remaining === -1 || remaining > 0, remaining };
    }

    if (featureId.includes('portfolio') && limits.maxPortfolio !== undefined) {
      const remaining = limits.maxPortfolio === -1 ? -1 : limits.maxPortfolio - (usage.currentPortfolio || 0);
      return { allowed: remaining === -1 || remaining > 0, remaining };
    }

    if (featureId.includes('storage') && limits.maxStorage !== undefined) {
      const remaining = limits.maxStorage === -1 ? -1 : limits.maxStorage - (usage.currentStorage || 0);
      return { allowed: remaining === -1 || remaining > 0, remaining };
    }

    if (featureId.includes('integration') && limits.maxIntegrations !== undefined) {
      const remaining = limits.maxIntegrations === -1 ? -1 : limits.maxIntegrations - (usage.currentIntegrations || 0);
      return { allowed: remaining === -1 || remaining > 0, remaining };
    }

    return { allowed: true };
  }

  // Update usage
  updateUsage(userId: string, featureId: string, increment: number = 1): void {
    const preferences = this.getSubscriberPreferences(userId);
    const feature = preferences.featureAccess.find(f => f.featureId === featureId);
    
    if (feature && feature.usage) {
      if (featureId.includes('appointment')) {
        feature.usage.currentAppointments = (feature.usage.currentAppointments || 0) + increment;
      } else if (featureId.includes('deposit')) {
        feature.usage.currentDeposits = (feature.usage.currentDeposits || 0) + increment;
      } else if (featureId.includes('scheduling')) {
        feature.usage.currentScheduling = (feature.usage.currentScheduling || 0) + increment;
      } else if (featureId.includes('client')) {
        feature.usage.currentClients = (feature.usage.currentClients || 0) + increment;
      } else if (featureId.includes('portfolio')) {
        feature.usage.currentPortfolio = (feature.usage.currentPortfolio || 0) + increment;
      } else if (featureId.includes('storage')) {
        feature.usage.currentStorage = (feature.usage.currentStorage || 0) + increment;
      } else if (featureId.includes('integration')) {
        feature.usage.currentIntegrations = (feature.usage.currentIntegrations || 0) + increment;
      }
      
      preferences.updatedAt = Date.now();
      this.subscribers.set(userId, preferences);
      this.saveSubscriberData();
    }
  }

  // Get integration status
  getIntegrationStatus(userId: string): {
    paymentMethods: { count: number; verified: number; default?: PaymentMethod };
    calendarIntegrations: { count: number; active: number; providers: string[] };
    featureAccess: { total: number; enabled: number; tier: string };
  } {
    const preferences = this.getSubscriberPreferences(userId);
    
    return {
      paymentMethods: {
        count: preferences.paymentMethods.length,
        verified: preferences.paymentMethods.filter(pm => pm.isVerified).length,
        default: preferences.paymentMethods.find(pm => pm.isDefault),
      },
      calendarIntegrations: {
        count: preferences.calendarIntegrations.length,
        active: preferences.calendarIntegrations.filter(cal => cal.isActive).length,
        providers: Array.from(new Set(preferences.calendarIntegrations.map(cal => cal.provider))),
      },
      featureAccess: {
        total: preferences.featureAccess.length,
        enabled: preferences.featureAccess.filter(f => f.isEnabled).length,
        tier: preferences.subscriptionTier,
      },
    };
  }

  // React Hook for subscriber preferences
  useSubscriberPreferences(userId: string) {
    const [preferences, setPreferences] = React.useState<SubscriberPreferences | null>(null);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
      const loadPreferences = async () => {
        setLoading(true);
        try {
          const prefs = this.getSubscriberPreferences(userId);
          setPreferences(prefs);
        } catch (error) {
          console.error('Failed to load subscriber preferences:', error);
        } finally {
          setLoading(false);
        }
      };

      loadPreferences();
    }, [userId]);

    return { preferences, loading, refetch: () => this.getSubscriberPreferences(userId) };
  }
}

export const apolloSubscriberIntegrationManager = new ApolloSubscriberIntegrationManager();
