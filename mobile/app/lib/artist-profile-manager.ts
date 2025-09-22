// APOLLO-GUIDED Artist Profile Management System
import React from 'react';

interface ArtistProfile {
  id: string;
  shopName: string;
  process: string[];
  bio: string;
  socialMedia: {
    instagram?: string;
    facebook?: string;
    twitter?: string;
    tiktok?: string;
    youtube?: string;
  };
  contact: {
    email: string;
    phone: string;
    website?: string;
    address?: string;
  };
  specialties: string[];
  experience: number;
  portfolio: {
    images: string[];
    videos: string[];
    descriptions: string[];
  };
  availability: {
    [key: string]: string[];
  };
  pricing: {
    hourlyRate: number;
    minimumCharge: number;
    consultationFee: number;
  };
  customizations: {
    chatbotPersonality: 'professional' | 'friendly' | 'artistic' | 'casual';
    welcomeMessage: string;
    colorScheme: string;
    logo?: string;
    customQuestions: string[];
  };
  createdAt: Date;
  updatedAt: Date;
}

interface ArtistProfileFormData {
  shopName: string;
  process: string[];
  bio: string;
  socialMedia: Partial<ArtistProfile['socialMedia']>;
  contact: Partial<ArtistProfile['contact']>;
  specialties: string[];
  experience: number;
  pricing: Partial<ArtistProfile['pricing']>;
  customizations: Partial<ArtistProfile['customizations']>;
}

class ApolloArtistProfileManager {
  private currentProfile: ArtistProfile | null = null;
  private listeners: Map<string, Function[]> = new Map();
  private isInitialized: boolean = false;

  constructor() {
    this.loadProfile();
  }

  // Initialize profile manager
  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Load existing profile or create default
      if (!this.currentProfile) {
        this.currentProfile = this.createDefaultProfile();
      }

      this.isInitialized = true;
      this.emit('initialized');
    } catch (error) {
      console.error('APOLLO Artist Profile initialization failed:', error);
      this.emit('error', error);
    }
  }

  // Create default profile
  private createDefaultProfile(): ArtistProfile {
    return {
      id: `artist_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      shopName: '',
      process: [],
      bio: '',
      socialMedia: {},
      contact: {
        email: '',
        phone: ''
      },
      specialties: [],
      experience: 0,
      portfolio: {
        images: [],
        videos: [],
        descriptions: []
      },
      availability: {},
      pricing: {
        hourlyRate: 0,
        minimumCharge: 0,
        consultationFee: 0
      },
      customizations: {
        chatbotPersonality: 'professional',
        welcomeMessage: 'Welcome to my tattoo studio! How can I help you today?',
        colorScheme: 'default',
        customQuestions: []
      },
      createdAt: new Date(),
      updatedAt: new Date()
    };
  }

  // Get current profile
  getCurrentProfile(): ArtistProfile | null {
    return this.currentProfile;
  }

  // Update profile
  async updateProfile(updates: Partial<ArtistProfileFormData>): Promise<boolean> {
    try {
      if (!this.currentProfile) {
        throw new Error('No profile to update');
      }

      // Update profile data
      Object.keys(updates).forEach(key => {
        if (key in this.currentProfile!) {
          (this.currentProfile as any)[key] = updates[key as keyof ArtistProfileFormData];
        }
      });

      this.currentProfile.updatedAt = new Date();
      this.saveProfile();
      this.emit('profileUpdated', this.currentProfile);

      return true;
    } catch (error) {
      console.error('Failed to update profile:', error);
      this.emit('error', error);
      return false;
    }
  }

  // Add portfolio item
  async addPortfolioItem(type: 'image' | 'video', url: string, description?: string): Promise<boolean> {
    try {
      if (!this.currentProfile) {
        throw new Error('No profile to update');
      }

      if (type === 'image') {
        this.currentProfile.portfolio.images.push(url);
      } else {
        this.currentProfile.portfolio.videos.push(url);
      }

      if (description) {
        this.currentProfile.portfolio.descriptions.push(description);
      }

      this.currentProfile.updatedAt = new Date();
      this.saveProfile();
      this.emit('portfolioUpdated', this.currentProfile.portfolio);

      return true;
    } catch (error) {
      console.error('Failed to add portfolio item:', error);
      this.emit('error', error);
      return false;
    }
  }

  // Update availability
  async updateAvailability(day: string, times: string[]): Promise<boolean> {
    try {
      if (!this.currentProfile) {
        throw new Error('No profile to update');
      }

      this.currentProfile.availability[day] = times;
      this.currentProfile.updatedAt = new Date();
      this.saveProfile();
      this.emit('availabilityUpdated', this.currentProfile.availability);

      return true;
    } catch (error) {
      console.error('Failed to update availability:', error);
      this.emit('error', error);
      return false;
    }
  }

  // Update pricing
  async updatePricing(pricing: Partial<ArtistProfile['pricing']>): Promise<boolean> {
    try {
      if (!this.currentProfile) {
        throw new Error('No profile to update');
      }

      this.currentProfile.pricing = { ...this.currentProfile.pricing, ...pricing };
      this.currentProfile.updatedAt = new Date();
      this.saveProfile();
      this.emit('pricingUpdated', this.currentProfile.pricing);

      return true;
    } catch (error) {
      console.error('Failed to update pricing:', error);
      this.emit('error', error);
      return false;
    }
  }

  // Update chatbot customizations
  async updateChatbotCustomizations(customizations: Partial<ArtistProfile['customizations']>): Promise<boolean> {
    try {
      if (!this.currentProfile) {
        throw new Error('No profile to update');
      }

      this.currentProfile.customizations = { ...this.currentProfile.customizations, ...customizations };
      this.currentProfile.updatedAt = new Date();
      this.saveProfile();
      this.emit('customizationsUpdated', this.currentProfile.customizations);

      return true;
    } catch (error) {
      console.error('Failed to update customizations:', error);
      this.emit('error', error);
      return false;
    }
  }

  // Generate chatbot configuration
  generateChatbotConfig(): any {
    if (!this.currentProfile) return null;

    return {
      personality: this.currentProfile.customizations.chatbotPersonality,
      welcomeMessage: this.currentProfile.customizations.welcomeMessage,
      shopName: this.currentProfile.shopName,
      specialties: this.currentProfile.specialties,
      process: this.currentProfile.process,
      bio: this.currentProfile.bio,
      contact: this.currentProfile.contact,
      socialMedia: this.currentProfile.socialMedia,
      pricing: this.currentProfile.pricing,
      availability: this.currentProfile.availability,
      customQuestions: this.currentProfile.customizations.customQuestions,
      colorScheme: this.currentProfile.customizations.colorScheme,
      logo: this.currentProfile.customizations.logo
    };
  }

  // Export profile for sharing
  exportProfile(): string {
    if (!this.currentProfile) return '';

    const exportData = {
      ...this.currentProfile,
      // Remove sensitive data
      contact: {
        email: this.currentProfile.contact.email,
        phone: this.currentProfile.contact.phone
      }
    };

    return JSON.stringify(exportData, null, 2);
  }

  // Import profile
  async importProfile(profileData: string): Promise<boolean> {
    try {
      const importedProfile = JSON.parse(profileData) as ArtistProfile;
      
      // Validate required fields
      if (!importedProfile.shopName || !importedProfile.contact.email) {
        throw new Error('Invalid profile data');
      }

      this.currentProfile = {
        ...importedProfile,
        id: `artist_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      this.saveProfile();
      this.emit('profileImported', this.currentProfile);

      return true;
    } catch (error) {
      console.error('Failed to import profile:', error);
      this.emit('error', error);
      return false;
    }
  }

  // Get profile completion percentage
  getProfileCompletion(): number {
    if (!this.currentProfile) return 0;

    const requiredFields = [
      'shopName',
      'bio',
      'contact.email',
      'contact.phone',
      'specialties',
      'process',
      'pricing.hourlyRate'
    ];

    let completedFields = 0;
    requiredFields.forEach(field => {
      const value = this.getNestedValue(this.currentProfile!, field);
      if (value && value !== '' && value !== 0) {
        completedFields++;
      }
    });

    return Math.round((completedFields / requiredFields.length) * 100);
  }

  // Get nested object value
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
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
  private saveProfile(): void {
    if (typeof window !== 'undefined' && this.currentProfile) {
      localStorage.setItem('apollo_artist_profile', JSON.stringify(this.currentProfile));
    }
  }

  private loadProfile(): void {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('apollo_artist_profile');
      if (saved) {
        try {
          this.currentProfile = JSON.parse(saved);
        } catch (error) {
          console.error('Failed to load profile:', error);
        }
      }
    }
  }

  // Reset profile
  resetProfile(): void {
    this.currentProfile = this.createDefaultProfile();
    this.saveProfile();
    this.emit('profileReset');
  }
}

// Singleton instance
export const apolloArtistProfile = new ApolloArtistProfileManager();

// React hook for artist profile
export function useArtistProfile() {
  const [profile, setProfile] = React.useState<ArtistProfile | null>(null);
  const [completion, setCompletion] = React.useState(0);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const updateProfile = () => {
      setProfile(apolloArtistProfile.getCurrentProfile());
      setCompletion(apolloArtistProfile.getProfileCompletion());
      setIsLoading(false);
    };

    // Initialize profile manager
    apolloArtistProfile.initialize().then(() => {
      updateProfile();
    });

    // Set up event listeners
    apolloArtistProfile.on('profileUpdated', updateProfile);
    apolloArtistProfile.on('profileImported', updateProfile);
    apolloArtistProfile.on('profileReset', updateProfile);

    return () => {
      apolloArtistProfile.off('profileUpdated', updateProfile);
      apolloArtistProfile.off('profileImported', updateProfile);
      apolloArtistProfile.off('profileReset', updateProfile);
    };
  }, []);

  return {
    profile,
    completion,
    isLoading,
    updateProfile: (updates: Partial<ArtistProfileFormData>) => apolloArtistProfile.updateProfile(updates),
    addPortfolioItem: (type: 'image' | 'video', url: string, description?: string) => 
      apolloArtistProfile.addPortfolioItem(type, url, description),
    updateAvailability: (day: string, times: string[]) => 
      apolloArtistProfile.updateAvailability(day, times),
    updatePricing: (pricing: Partial<ArtistProfile['pricing']>) => 
      apolloArtistProfile.updatePricing(pricing),
    updateCustomizations: (customizations: Partial<ArtistProfile['customizations']>) => 
      apolloArtistProfile.updateChatbotCustomizations(customizations),
    generateChatbotConfig: () => apolloArtistProfile.generateChatbotConfig(),
    exportProfile: () => apolloArtistProfile.exportProfile(),
    importProfile: (data: string) => apolloArtistProfile.importProfile(data),
    resetProfile: () => apolloArtistProfile.resetProfile()
  };
}
