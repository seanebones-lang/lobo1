// APOLLO-GUIDED Mobile Subscription Management System
import React from 'react';

interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: 'month' | 'year';
  trialDays: number;
  features: string[];
  appStoreProductId: string;
}

interface SubscriptionStatus {
  isActive: boolean;
  planId: string | null;
  trialEndDate: Date | null;
  subscriptionEndDate: Date | null;
  autoRenew: boolean;
  isTrialActive: boolean;
  isTrialExpired: boolean;
  daysRemaining: number;
}

interface SubscriptionEvent {
  type: 'purchased' | 'restored' | 'cancelled' | 'expired' | 'trial_started' | 'trial_expired';
  planId: string;
  timestamp: Date;
  transactionId?: string;
  receipt?: string;
}

class ApolloSubscriptionManager {
  private plans: Map<string, SubscriptionPlan> = new Map();
  private currentStatus: SubscriptionStatus | null = null;
  private listeners: Map<string, Function[]> = new Map();
  private isInitialized: boolean = false;

  constructor() {
    this.initializePlans();
    this.loadSubscriptionStatus();
  }

  private initializePlans(): void {
    // Basic Plan - $9.99/month
    this.plans.set('basic_monthly', {
      id: 'basic_monthly',
      name: 'Basic Plan',
      price: 9.99,
      currency: 'USD',
      interval: 'month',
      trialDays: 14,
      features: [
        'Up to 50 AI consultations/month',
        'Basic tattoo design tools',
        'Standard booking system',
        'Email support',
        'Basic templates library',
        'Mobile app access',
        'Social media integration'
      ],
      appStoreProductId: 'com.nexteleven.tattoo.basic.monthly'
    });

    // Premium Plan - $19.99/month
    this.plans.set('premium_monthly', {
      id: 'premium_monthly',
      name: 'Premium Plan',
      price: 19.99,
      currency: 'USD',
      interval: 'month',
      trialDays: 14,
      features: [
        'Unlimited AI consultations',
        'Advanced tattoo design tools',
        'Priority booking with artists',
        'Exclusive design templates',
        'Priority customer support',
        'Offline mode access',
        'Cloud sync across devices',
        'Advanced analytics',
        'Custom branding options',
        'Social media automation'
      ],
      appStoreProductId: 'com.nexteleven.tattoo.premium.monthly'
    });

    // Pro Plan - $29.99/month
    this.plans.set('pro_monthly', {
      id: 'pro_monthly',
      name: 'Pro Plan',
      price: 29.99,
      currency: 'USD',
      interval: 'month',
      trialDays: 14,
      features: [
        'Unlimited AI consultations',
        'Professional tattoo design tools',
        'VIP booking with artists',
        'Premium design templates',
        'Dedicated support manager',
        'Offline mode access',
        'Cloud sync across devices',
        'Advanced analytics & reporting',
        'Full custom branding',
        'Social media automation',
        'Multi-location support',
        'API access for integrations',
        'White-label options',
        'Advanced security features'
      ],
      appStoreProductId: 'com.nexteleven.tattoo.pro.monthly'
    });

    // Annual Plans with Discounts
    this.plans.set('basic_yearly', {
      id: 'basic_yearly',
      name: 'Basic Plan (Yearly)',
      price: 99.99,
      currency: 'USD',
      interval: 'year',
      trialDays: 14,
      features: [
        'Up to 50 AI consultations/month',
        'Basic tattoo design tools',
        'Standard booking system',
        'Email support',
        'Basic templates library',
        'Mobile app access',
        'Social media integration',
        '2 months free (save $20)'
      ],
      appStoreProductId: 'com.nexteleven.tattoo.basic.yearly'
    });

    this.plans.set('premium_yearly', {
      id: 'premium_yearly',
      name: 'Premium Plan (Yearly)',
      price: 199.99,
      currency: 'USD',
      interval: 'year',
      trialDays: 14,
      features: [
        'Unlimited AI consultations',
        'Advanced tattoo design tools',
        'Priority booking with artists',
        'Exclusive design templates',
        'Priority customer support',
        'Offline mode access',
        'Cloud sync across devices',
        'Advanced analytics',
        'Custom branding options',
        'Social media automation',
        '2 months free (save $40)'
      ],
      appStoreProductId: 'com.nexteleven.tattoo.premium.yearly'
    });

    this.plans.set('pro_yearly', {
      id: 'pro_yearly',
      name: 'Pro Plan (Yearly)',
      price: 299.99,
      currency: 'USD',
      interval: 'year',
      trialDays: 14,
      features: [
        'Unlimited AI consultations',
        'Professional tattoo design tools',
        'VIP booking with artists',
        'Premium design templates',
        'Dedicated support manager',
        'Offline mode access',
        'Cloud sync across devices',
        'Advanced analytics & reporting',
        'Full custom branding',
        'Social media automation',
        'Multi-location support',
        'API access for integrations',
        'White-label options',
        'Advanced security features',
        '2 months free (save $60)'
      ],
      appStoreProductId: 'com.nexteleven.tattoo.pro.yearly'
    });
  }

  // Initialize subscription system
  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Check if we're in a mobile environment
      if (typeof window !== 'undefined' && 'ReactNative' in window) {
        await this.initializeReactNative();
      } else if (typeof window !== 'undefined' && 'webkit' in window) {
        await this.initializeWebKit();
      } else {
        await this.initializeWebFallback();
      }

      this.isInitialized = true;
      this.emit('initialized');
    } catch (error) {
      console.error('APOLLO Subscription initialization failed:', error);
      this.emit('error', error);
    }
  }

  // React Native initialization
  private async initializeReactNative(): Promise<void> {
    // In a real React Native app, you would use react-native-iap
    console.log('🌊 APOLLO Subscription: Initializing React Native IAP...');
    
    // Mock implementation for web development
    this.currentStatus = {
      isActive: false,
      planId: null,
      trialEndDate: null,
      subscriptionEndDate: null,
      autoRenew: false,
      isTrialActive: false,
      isTrialExpired: false,
      daysRemaining: 0
    };
  }

  // WebKit (iOS Safari) initialization
  private async initializeWebKit(): Promise<void> {
    console.log('🌊 APOLLO Subscription: Initializing WebKit StoreKit...');
    
    // Check if StoreKit is available
    if ('storekit' in window) {
      // Initialize StoreKit for web
      await this.initializeStoreKitWeb();
    } else {
      // Fallback to web-based subscription
      await this.initializeWebFallback();
    }
  }

  // Web fallback initialization
  private async initializeWebFallback(): Promise<void> {
    console.log('🌊 APOLLO Subscription: Using web fallback...');
    
    // For web development, simulate subscription status
    this.currentStatus = {
      isActive: false,
      planId: null,
      trialEndDate: null,
      subscriptionEndDate: null,
      autoRenew: false,
      isTrialActive: false,
      isTrialExpired: false,
      daysRemaining: 0
    };
  }

  // StoreKit Web initialization
  private async initializeStoreKitWeb(): Promise<void> {
    try {
      // Initialize StoreKit for web
      const storekit = (window as any).storekit;
      await storekit.configure({
        appIdentifier: 'com.nexteleven.tattoo',
        environment: 'sandbox' // Use 'production' for live app
      });

      // Set up event listeners
      storekit.addEventListener('purchase', this.handlePurchase.bind(this));
      storekit.addEventListener('restore', this.handleRestore.bind(this));
      storekit.addEventListener('error', this.handleError.bind(this));

    } catch (error) {
      console.error('StoreKit Web initialization failed:', error);
      throw error;
    }
  }

  // Start free trial
  async startFreeTrial(planId: string): Promise<boolean> {
    try {
      const plan = this.plans.get(planId);
      if (!plan) throw new Error('Invalid plan ID');

      const trialEndDate = new Date();
      trialEndDate.setDate(trialEndDate.getDate() + plan.trialDays);

      this.currentStatus = {
        isActive: true,
        planId: planId,
        trialEndDate: trialEndDate,
        subscriptionEndDate: null,
        autoRenew: true,
        isTrialActive: true,
        isTrialExpired: false,
        daysRemaining: plan.trialDays
      };

      this.saveSubscriptionStatus();
      this.emit('trial_started', { planId, trialEndDate });

      // Track trial start
      this.trackSubscriptionEvent({
        type: 'trial_started',
        planId: planId,
        timestamp: new Date()
      });

      return true;
    } catch (error) {
      console.error('Failed to start free trial:', error);
      this.emit('error', error);
      return false;
    }
  }

  // Purchase subscription
  async purchaseSubscription(planId: string): Promise<boolean> {
    try {
      const plan = this.plans.get(planId);
      if (!plan) throw new Error('Invalid plan ID');

      // Check if we're in a mobile environment
      if (typeof window !== 'undefined' && 'ReactNative' in window) {
        return await this.purchaseReactNative(plan);
      } else if (typeof window !== 'undefined' && 'storekit' in window) {
        return await this.purchaseStoreKit(plan);
      } else {
        return await this.purchaseWebFallback(plan);
      }
    } catch (error) {
      console.error('Purchase failed:', error);
      this.emit('error', error);
      return false;
    }
  }

  // React Native purchase
  private async purchaseReactNative(plan: SubscriptionPlan): Promise<boolean> {
    // In a real React Native app, you would use react-native-iap
    console.log(`🌊 APOLLO Subscription: Purchasing ${plan.name} via React Native IAP...`);
    
    // Mock successful purchase
    const subscriptionEndDate = new Date();
    subscriptionEndDate.setMonth(subscriptionEndDate.getMonth() + (plan.interval === 'year' ? 12 : 1));

    this.currentStatus = {
      isActive: true,
      planId: plan.id,
      trialEndDate: null,
      subscriptionEndDate: subscriptionEndDate,
      autoRenew: true,
      isTrialActive: false,
      isTrialExpired: false,
      daysRemaining: 0
    };

    this.saveSubscriptionStatus();
    this.emit('purchased', { planId: plan.id, subscriptionEndDate });

    return true;
  }

  // StoreKit purchase
  private async purchaseStoreKit(plan: SubscriptionPlan): Promise<boolean> {
    try {
      const storekit = (window as any).storekit;
      const product = await storekit.getProduct(plan.appStoreProductId);
      
      if (!product) {
        throw new Error('Product not found');
      }

      const transaction = await storekit.purchase(product);
      
      if (transaction) {
        const subscriptionEndDate = new Date();
        subscriptionEndDate.setMonth(subscriptionEndDate.getMonth() + (plan.interval === 'year' ? 12 : 1));

        this.currentStatus = {
          isActive: true,
          planId: plan.id,
          trialEndDate: null,
          subscriptionEndDate: subscriptionEndDate,
          autoRenew: true,
          isTrialActive: false,
          isTrialExpired: false,
          daysRemaining: 0
        };

        this.saveSubscriptionStatus();
        this.emit('purchased', { planId: plan.id, subscriptionEndDate, transactionId: transaction.id });

        return true;
      }

      return false;
    } catch (error) {
      console.error('StoreKit purchase failed:', error);
      throw error;
    }
  }

  // Web fallback purchase
  private async purchaseWebFallback(plan: SubscriptionPlan): Promise<boolean> {
    console.log(`🌊 APOLLO Subscription: Simulating purchase of ${plan.name}...`);
    
    // In a real web app, you would integrate with Stripe, PayPal, or similar
    const subscriptionEndDate = new Date();
    subscriptionEndDate.setMonth(subscriptionEndDate.getMonth() + (plan.interval === 'year' ? 12 : 1));

    this.currentStatus = {
      isActive: true,
      planId: plan.id,
      trialEndDate: null,
      subscriptionEndDate: subscriptionEndDate,
      autoRenew: true,
      isTrialActive: false,
      isTrialExpired: false,
      daysRemaining: 0
    };

    this.saveSubscriptionStatus();
    this.emit('purchased', { planId: plan.id, subscriptionEndDate });

    return true;
  }

  // Cancel subscription
  async cancelSubscription(): Promise<boolean> {
    try {
      if (!this.currentStatus?.isActive) {
        throw new Error('No active subscription to cancel');
      }

      // In a real app, you would call the appropriate cancellation API
      console.log('🌊 APOLLO Subscription: Cancelling subscription...');

      this.currentStatus.autoRenew = false;
      this.saveSubscriptionStatus();
      this.emit('cancelled', { planId: this.currentStatus.planId });

      // Track cancellation
      this.trackSubscriptionEvent({
        type: 'cancelled',
        planId: this.currentStatus.planId!,
        timestamp: new Date()
      });

      return true;
    } catch (error) {
      console.error('Cancellation failed:', error);
      this.emit('error', error);
      return false;
    }
  }

  // Restore purchases
  async restorePurchases(): Promise<boolean> {
    try {
      console.log('🌊 APOLLO Subscription: Restoring purchases...');

      // In a real app, you would restore from the app store
      const restored = await this.loadSubscriptionStatus();
      
      if (restored) {
        this.emit('restored', { status: this.currentStatus });
        return true;
      }

      return false;
    } catch (error) {
      console.error('Restore failed:', error);
      this.emit('error', error);
      return false;
    }
  }

  // Check subscription status
  checkSubscriptionStatus(): SubscriptionStatus | null {
    if (!this.currentStatus) return null;

    const now = new Date();
    const status = { ...this.currentStatus };

    // Check trial status
    if (status.isTrialActive && status.trialEndDate) {
      if (now > status.trialEndDate) {
        status.isTrialActive = false;
        status.isTrialExpired = true;
        status.isActive = false;
        this.emit('trial_expired');
      } else {
        status.daysRemaining = Math.ceil((status.trialEndDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
      }
    }

    // Check subscription status
    if (status.subscriptionEndDate && now > status.subscriptionEndDate) {
      status.isActive = false;
      this.emit('expired');
    }

    this.currentStatus = status;
    return status;
  }

  // Get available plans
  getAvailablePlans(): SubscriptionPlan[] {
    return Array.from(this.plans.values());
  }

  // Get current plan
  getCurrentPlan(): SubscriptionPlan | null {
    if (!this.currentStatus?.planId) return null;
    return this.plans.get(this.currentStatus.planId) || null;
  }

  // Event handling
  private handlePurchase(event: any): void {
    console.log('Purchase event:', event);
    this.emit('purchased', event);
  }

  private handleRestore(event: any): void {
    console.log('Restore event:', event);
    this.emit('restored', event);
  }

  private handleError(event: any): void {
    console.error('Subscription error:', event);
    this.emit('error', event);
  }

  // Event system
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  off(event: string, callback: Function): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private emit(event: string, data?: any): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  // Persistence
  private saveSubscriptionStatus(): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('apollo_subscription_status', JSON.stringify(this.currentStatus));
    }
  }

  private loadSubscriptionStatus(): boolean {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('apollo_subscription_status');
      if (saved) {
        try {
          this.currentStatus = JSON.parse(saved);
          return true;
        } catch (error) {
          console.error('Failed to load subscription status:', error);
        }
      }
    }
    return false;
  }

  // Analytics
  private trackSubscriptionEvent(event: SubscriptionEvent): void {
    // In a real app, you would send this to your analytics service
    console.log('🌊 APOLLO Subscription Event:', event);
  }

  // Cleanup
  destroy(): void {
    this.listeners.clear();
    this.currentStatus = null;
  }
}

// Singleton instance
export const apolloSubscription = new ApolloSubscriptionManager();

// React hook for subscription status
export function useSubscription() {
  const [status, setStatus] = React.useState<SubscriptionStatus | null>(null);
  const [plans, setPlans] = React.useState<SubscriptionPlan[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const updateStatus = () => {
      setStatus(apolloSubscription.checkSubscriptionStatus());
      setPlans(apolloSubscription.getAvailablePlans());
      setIsLoading(false);
    };

    // Initialize subscription manager
    apolloSubscription.initialize().then(() => {
      updateStatus();
    });

    // Set up event listeners
    apolloSubscription.on('purchased', updateStatus);
    apolloSubscription.on('cancelled', updateStatus);
    apolloSubscription.on('expired', updateStatus);
    apolloSubscription.on('trial_expired', updateStatus);
    apolloSubscription.on('restored', updateStatus);

    // Update status periodically
    const interval = setInterval(updateStatus, 60000); // Every minute

    return () => {
      clearInterval(interval);
      apolloSubscription.off('purchased', updateStatus);
      apolloSubscription.off('cancelled', updateStatus);
      apolloSubscription.off('expired', updateStatus);
      apolloSubscription.off('trial_expired', updateStatus);
      apolloSubscription.off('restored', updateStatus);
    };
  }, []);

  return {
    status,
    plans,
    isLoading,
    startTrial: (planId: string) => apolloSubscription.startFreeTrial(planId),
    purchase: (planId: string) => apolloSubscription.purchaseSubscription(planId),
    cancel: () => apolloSubscription.cancelSubscription(),
    restore: () => apolloSubscription.restorePurchases(),
    getCurrentPlan: () => apolloSubscription.getCurrentPlan()
  };
}
