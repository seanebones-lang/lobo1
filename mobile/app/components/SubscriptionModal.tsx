'use client'

import React, { useState, useEffect } from 'react';
import { useSubscription } from '../lib/subscription-manager';
import { 
  X, 
  Check, 
  Crown, 
  Star, 
  Clock, 
  Shield, 
  Zap,
  Users,
  Cloud,
  Headphones,
  BarChart3,
  Palette,
  Code
} from 'lucide-react';

interface SubscriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubscribe?: (planId: string) => void;
}

export default function SubscriptionModal({ isOpen, onClose, onSubscribe }: SubscriptionModalProps) {
  const { status, plans, isLoading, startTrial, purchase } = useSubscription();
  const [selectedPlan, setSelectedPlan] = useState<string>('premium_monthly');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showTrialSuccess, setShowTrialSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setSelectedPlan('premium_monthly');
    }
  }, [isOpen]);

  const handleStartTrial = async () => {
    setIsProcessing(true);
    try {
      const success = await startTrial(selectedPlan);
      if (success) {
        setShowTrialSuccess(true);
        setTimeout(() => {
          setShowTrialSuccess(false);
          onClose();
        }, 3000);
      }
    } catch (error) {
      console.error('Failed to start trial:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePurchase = async () => {
    setIsProcessing(true);
    try {
      const success = await purchase(selectedPlan);
      if (success) {
        onSubscribe?.(selectedPlan);
        onClose();
      }
    } catch (error) {
      console.error('Failed to purchase:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const getFeatureIcon = (feature: string) => {
    if (feature.includes('AI')) return <Zap className="w-4 h-4 text-blue-500" />;
    if (feature.includes('design')) return <Crown className="w-4 h-4 text-purple-500" />;
    if (feature.includes('booking')) return <Users className="w-4 h-4 text-green-500" />;
    if (feature.includes('support')) return <Headphones className="w-4 h-4 text-orange-500" />;
    if (feature.includes('sync')) return <Cloud className="w-4 h-4 text-cyan-500" />;
    if (feature.includes('offline')) return <Shield className="w-4 h-4 text-gray-500" />;
    if (feature.includes('analytics')) return <BarChart3 className="w-4 h-4 text-indigo-500" />;
    if (feature.includes('branding')) return <Palette className="w-4 h-4 text-pink-500" />;
    if (feature.includes('API')) return <Code className="w-4 h-4 text-cyan-500" />;
    return <Check className="w-4 h-4 text-green-500" />;
  };

  const getPlanColor = (planId: string) => {
    if (planId.includes('basic')) return 'border-gray-500';
    if (planId.includes('premium')) return 'border-blue-500';
    if (planId.includes('pro')) return 'border-purple-500';
    return 'border-gray-500';
  };

  const getPlanBadge = (planId: string) => {
    if (planId.includes('basic')) return { text: 'Basic', color: 'bg-gray-600' };
    if (planId.includes('premium')) return { text: 'Popular', color: 'bg-blue-600' };
    if (planId.includes('pro')) return { text: 'Pro', color: 'bg-purple-600' };
    return { text: '', color: '' };
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <Crown className="w-6 h-6 text-yellow-500" />
            <h2 className="text-xl font-bold text-white">Go Premium</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Trial Success Message */}
        {showTrialSuccess && (
          <div className="p-4 bg-green-900 border border-green-700 rounded-lg mx-6 mt-4">
            <div className="flex items-center gap-2 text-green-400">
              <Check className="w-5 h-5" />
              <span className="font-semibold">Free trial started!</span>
            </div>
            <p className="text-green-300 text-sm mt-1">
              Enjoy 14 days of premium features
            </p>
          </div>
        )}

        {/* Current Status */}
        {status && (
          <div className="p-6 border-b border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-4 h-4 text-blue-500" />
              <span className="text-sm text-gray-300">Current Status</span>
            </div>
            {status.isTrialActive ? (
              <div className="text-green-400">
                <p className="font-semibold">Free Trial Active</p>
                <p className="text-sm">{status.daysRemaining} days remaining</p>
              </div>
            ) : status.isActive ? (
              <div className="text-green-400">
                <p className="font-semibold">Premium Active</p>
                <p className="text-sm">Auto-renewal enabled</p>
              </div>
            ) : (
              <div className="text-gray-400">
                <p className="font-semibold">Free Plan</p>
                <p className="text-sm">Upgrade to unlock premium features</p>
              </div>
            )}
          </div>
        )}

        {/* Plans */}
        <div className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Choose Your Plan</h3>
          
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <div className="space-y-4">
              {plans.map((plan) => {
                const badge = getPlanBadge(plan.id);
                const isSelected = selectedPlan === plan.id;
                const isPopular = plan.id.includes('premium');
                
                return (
                  <div
                    key={plan.id}
                    className={`relative border-2 rounded-xl p-4 cursor-pointer transition-all ${
                      isSelected
                        ? `${getPlanColor(plan.id)} bg-opacity-20`
                        : 'border-gray-700 hover:border-gray-600'
                    } ${isPopular ? 'ring-2 ring-blue-500 ring-opacity-50' : ''}`}
                    onClick={() => setSelectedPlan(plan.id)}
                  >
                    {/* Popular Badge */}
                    {isPopular && (
                      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                        <span className="bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-medium">
                          Most Popular
                        </span>
                      </div>
                    )}

                    {/* Plan Badge */}
                    {badge.text && (
                      <div className="absolute top-4 right-4">
                        <span className={`${badge.color} text-white text-xs px-2 py-1 rounded font-medium`}>
                          {badge.text}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-white">{plan.name}</h4>
                        <div className="flex items-center gap-2">
                          <span className="text-2xl font-bold text-white">${plan.price}</span>
                          <span className="text-gray-400">/{plan.interval}</span>
                          {plan.interval === 'year' && (
                            <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">
                              Save ${plan.id.includes('basic') ? '20' : plan.id.includes('premium') ? '40' : '60'}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className={`w-4 h-4 rounded-full border-2 ${
                        isSelected
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-gray-600'
                      }`}>
                        {isSelected && (
                          <Check className="w-3 h-3 text-white" />
                        )}
                      </div>
                    </div>

                    {/* Features */}
                    <div className="space-y-2">
                      {plan.features.slice(0, 4).map((feature, index) => (
                        <div key={index} className="flex items-center gap-2 text-sm text-gray-300">
                          {getFeatureIcon(feature)}
                          <span>{feature}</span>
                        </div>
                      ))}
                      {plan.features.length > 4 && (
                        <div className="text-xs text-gray-500">
                          +{plan.features.length - 4} more features
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-6 space-y-3">
            <button
              onClick={handleStartTrial}
              disabled={isProcessing || status?.isTrialActive}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:from-blue-700 hover:to-purple-700"
            >
              {isProcessing ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Starting Trial...
                </div>
              ) : status?.isTrialActive ? (
                'Trial Already Active'
              ) : (
                'Start 14-Day Free Trial'
              )}
            </button>

            <button
              onClick={handlePurchase}
              disabled={isProcessing || status?.isActive}
              className="w-full border-2 border-gray-600 text-white py-3 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:border-gray-500"
            >
              {isProcessing ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Processing...
                </div>
              ) : status?.isActive ? (
                'Already Subscribed'
              ) : (
                'Subscribe Now'
              )}
            </button>
          </div>

          {/* Terms */}
          <div className="mt-4 text-xs text-gray-500 text-center">
            <p>
              By subscribing, you agree to our Terms of Service and Privacy Policy.
            </p>
            <p className="mt-1">
              Cancel anytime in your device settings.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
