// APOLLO-GUIDED Subscriber Integration Dashboard
'use client'

import React, { useState, useEffect } from 'react';
import { 
  CreditCard, 
  Calendar, 
  Settings, 
  Plus, 
  Check, 
  X, 
  AlertCircle, 
  Shield, 
  Zap,
  Users,
  BarChart3,
  Palette,
  Code,
  Crown,
  Star
} from 'lucide-react';
import { apolloSubscriberIntegrationManager, PaymentMethod, CalendarIntegration, FeatureAccess } from '../lib/subscriber-integration-manager';

interface SubscriberIntegrationDashboardProps {
  userId: string;
  className?: string;
}

export default function SubscriberIntegrationDashboard({ userId, className = '' }: SubscriberIntegrationDashboardProps) {
  const [activeTab, setActiveTab] = useState<'payment' | 'calendar' | 'features' | 'preferences'>('payment');
  const [showAddPayment, setShowAddPayment] = useState(false);
  const [showAddCalendar, setShowAddCalendar] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { preferences, loading: prefsLoading } = apolloSubscriberIntegrationManager.useSubscriberPreferences(userId);
  const integrationStatus = apolloSubscriberIntegrationManager.getIntegrationStatus(userId);

  const handleAddPaymentMethod = async (paymentData: Partial<PaymentMethod>) => {
    setLoading(true);
    setError(null);
    try {
      await apolloSubscriberIntegrationManager.addPaymentMethod(userId, paymentData);
      setShowAddPayment(false);
    } catch (err) {
      setError('Failed to add payment method');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCalendarIntegration = async (integrationData: Partial<CalendarIntegration>) => {
    setLoading(true);
    setError(null);
    try {
      await apolloSubscriberIntegrationManager.addCalendarIntegration(userId, integrationData);
      setShowAddCalendar(false);
    } catch (err) {
      setError('Failed to add calendar integration');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgradeTier = async (newTier: 'premium' | 'pro') => {
    setLoading(true);
    setError(null);
    try {
      await apolloSubscriberIntegrationManager.updateSubscriptionTier(userId, newTier);
    } catch (err) {
      setError('Failed to upgrade subscription');
    } finally {
      setLoading(false);
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'basic': return 'text-gray-400';
      case 'premium': return 'text-blue-400';
      case 'pro': return 'text-purple-400';
      default: return 'text-gray-400';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'basic': return <Shield className="w-5 h-5" />;
      case 'premium': return <Star className="w-5 h-5" />;
      case 'pro': return <Crown className="w-5 h-5" />;
      default: return <Shield className="w-5 h-5" />;
    }
  };

  const getFeatureIcon = (featureId: string) => {
    if (featureId.includes('chat')) return <Zap className="w-4 h-4" />;
    if (featureId.includes('calendar')) return <Calendar className="w-4 h-4" />;
    if (featureId.includes('payment')) return <CreditCard className="w-4 h-4" />;
    if (featureId.includes('analytics')) return <BarChart3 className="w-4 h-4" />;
    if (featureId.includes('branding')) return <Palette className="w-4 h-4" />;
    if (featureId.includes('api')) return <Code className="w-4 h-4" />;
    if (featureId.includes('team')) return <Users className="w-4 h-4" />;
    return <Settings className="w-4 h-4" />;
  };

  if (prefsLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="text-center p-8">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-400">Failed to load subscriber preferences</p>
      </div>
    );
  }

  return (
    <div className={`subscriber-integration-dashboard ${className}`}>
      {/* Header */}
      <div className="dashboard-header mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <Settings className="w-6 h-6 text-blue-500" />
              Subscriber Integration Center
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              Manage your payment methods, calendar integrations, and feature access
            </p>
          </div>
          <div className="flex items-center gap-2">
            {getTierIcon(preferences.subscriptionTier)}
            <span className={`font-semibold ${getTierColor(preferences.subscriptionTier)}`}>
              {preferences.subscriptionTier.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900 text-white p-3 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="tab-navigation mb-6">
        <div className="flex space-x-1 bg-gray-800 p-1 rounded-lg">
          {[
            { id: 'payment', label: 'Payment Methods', icon: CreditCard },
            { id: 'calendar', label: 'Calendar Sync', icon: Calendar },
            { id: 'features', label: 'Feature Access', icon: Settings },
            { id: 'preferences', label: 'Preferences', icon: Settings },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
                activeTab === id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {/* Payment Methods Tab */}
        {activeTab === 'payment' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Payment Methods</h3>
              <button
                onClick={() => setShowAddPayment(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add Payment Method
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {preferences.paymentMethods.map((payment) => (
                <div key={payment.id} className="bg-gray-800 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <CreditCard className="w-5 h-5 text-blue-500" />
                    <div className="flex items-center gap-2">
                      {payment.isVerified ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <X className="w-4 h-4 text-red-500" />
                      )}
                      {payment.isDefault && (
                        <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Default</span>
                      )}
                    </div>
                  </div>
                  <div className="text-white font-medium">
                    {payment.brand?.toUpperCase()} •••• {payment.last4}
                  </div>
                  <div className="text-gray-400 text-sm">
                    {payment.provider} • {payment.type.replace('_', ' ')}
                  </div>
                  {payment.expiryMonth && payment.expiryYear && (
                    <div className="text-gray-400 text-sm">
                      Expires {payment.expiryMonth}/{payment.expiryYear}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {preferences.paymentMethods.length === 0 && (
              <div className="text-center py-8 text-gray-400">
                <CreditCard className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No payment methods added yet</p>
                <p className="text-sm">Add a payment method to enable seamless transactions</p>
              </div>
            )}
          </div>
        )}

        {/* Calendar Integration Tab */}
        {activeTab === 'calendar' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Calendar Integrations</h3>
              <button
                onClick={() => setShowAddCalendar(true)}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Connect Calendar
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {preferences.calendarIntegrations.map((integration) => (
                <div key={integration.id} className="bg-gray-800 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <Calendar className="w-5 h-5 text-green-500" />
                    <div className="flex items-center gap-2">
                      {integration.isActive ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <X className="w-4 h-4 text-red-500" />
                      )}
                      {integration.syncEnabled && (
                        <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">Syncing</span>
                      )}
                    </div>
                  </div>
                  <div className="text-white font-medium">{integration.calendarName}</div>
                  <div className="text-gray-400 text-sm capitalize">{integration.provider}</div>
                  {integration.lastSyncAt && (
                    <div className="text-gray-400 text-sm">
                      Last sync: {new Date(integration.lastSyncAt).toLocaleString()}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {preferences.calendarIntegrations.length === 0 && (
              <div className="text-center py-8 text-gray-400">
                <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No calendar integrations connected</p>
                <p className="text-sm">Connect your calendar to sync appointments automatically</p>
              </div>
            )}
          </div>
        )}

        {/* Feature Access Tab */}
        {activeTab === 'features' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Feature Access</h3>
              {preferences.subscriptionTier !== 'pro' && (
                <button
                  onClick={() => handleUpgradeTier(preferences.subscriptionTier === 'basic' ? 'premium' : 'pro')}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <Crown className="w-4 h-4" />
                  Upgrade Plan
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {preferences.featureAccess.map((feature) => (
                <div key={feature.featureId} className="bg-gray-800 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    {getFeatureIcon(feature.featureId)}
                    <div className="flex items-center gap-2">
                      {feature.isEnabled ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <X className="w-4 h-4 text-red-500" />
                      )}
                      <span className={`text-xs px-2 py-1 rounded ${
                        feature.tier === 'basic' ? 'bg-gray-600' :
                        feature.tier === 'premium' ? 'bg-blue-600' : 'bg-purple-600'
                      } text-white`}>
                        {feature.tier.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="text-white font-medium">{feature.featureName}</div>
                  {feature.limits && (
                    <div className="text-gray-400 text-sm mt-2">
                      {Object.entries(feature.limits).map(([key, value]) => (
                        <div key={key}>
                          {key.replace(/([A-Z])/g, ' $1').toLowerCase()}: {
                            value === -1 ? 'Unlimited' : value
                          }
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Preferences Tab */}
        {activeTab === 'preferences' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-white">Preferences</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Notifications */}
              <div className="bg-gray-800 p-4 rounded-lg">
                <h4 className="text-white font-medium mb-4">Notifications</h4>
                <div className="space-y-3">
                  {Object.entries(preferences.notifications).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-gray-300 capitalize">
                        {key.replace(/([A-Z])/g, ' $1').toLowerCase()}
                      </span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={value}
                          onChange={() => {
                            const newPrefs = { ...preferences };
                            newPrefs.notifications[key as keyof typeof newPrefs.notifications] = !value;
                            newPrefs.updatedAt = Date.now();
                            // Update preferences logic would go here
                          }}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Privacy */}
              <div className="bg-gray-800 p-4 rounded-lg">
                <h4 className="text-white font-medium mb-4">Privacy</h4>
                <div className="space-y-3">
                  {Object.entries(preferences.privacy).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-gray-300 capitalize">
                        {key.replace(/([A-Z])/g, ' $1').toLowerCase()}
                      </span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={value}
                          onChange={() => {
                            const newPrefs = { ...preferences };
                            newPrefs.privacy[key as keyof typeof newPrefs.privacy] = !value;
                            newPrefs.updatedAt = Date.now();
                            // Update preferences logic would go here
                          }}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Integration Status Summary */}
      <div className="mt-8 bg-gray-800 p-4 rounded-lg">
        <h4 className="text-white font-medium mb-4">Integration Status</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-500">{integrationStatus.paymentMethods.count}</div>
            <div className="text-gray-400 text-sm">Payment Methods</div>
            <div className="text-green-500 text-xs">{integrationStatus.paymentMethods.verified} verified</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-500">{integrationStatus.calendarIntegrations.count}</div>
            <div className="text-gray-400 text-sm">Calendar Integrations</div>
            <div className="text-green-500 text-xs">{integrationStatus.calendarIntegrations.active} active</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-500">{integrationStatus.featureAccess.enabled}</div>
            <div className="text-gray-400 text-sm">Features Enabled</div>
            <div className="text-blue-500 text-xs">{integrationStatus.featureAccess.tier} tier</div>
          </div>
        </div>
      </div>
    </div>
  );
}
