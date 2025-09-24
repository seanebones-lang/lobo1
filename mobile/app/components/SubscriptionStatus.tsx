'use client'

import React from 'react';
import { useSubscription } from '../lib/subscription-manager';
import { 
  Crown, 
  Clock, 
  AlertCircle, 
  CheckCircle, 
  Settings,
  RefreshCw
} from 'lucide-react';

interface SubscriptionStatusProps {
  className?: string;
  onManageSubscription?: () => void;
}

export default function SubscriptionStatus({ className = '', onManageSubscription }: SubscriptionStatusProps) {
  const { status, isLoading, restore } = useSubscription();

  if (isLoading) {
    return (
      <div className={`subscription-status ${className}`}>
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className={`subscription-status ${className}`}>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center gap-2 text-gray-400">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">Subscription status unavailable</span>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = () => {
    if (status.isActive) return 'text-green-400';
    if (status.isTrialActive) return 'text-blue-400';
    if (status.isTrialExpired) return 'text-orange-400';
    return 'text-gray-400';
  };

  const getStatusIcon = () => {
    if (status.isActive) return <CheckCircle className="w-4 h-4 text-green-400" />;
    if (status.isTrialActive) return <Clock className="w-4 h-4 text-blue-400" />;
    if (status.isTrialExpired) return <AlertCircle className="w-4 h-4 text-orange-400" />;
    return <Crown className="w-4 h-4 text-gray-400" />;
  };

  const getStatusText = () => {
    if (status.isActive) return 'Premium Active';
    if (status.isTrialActive) return 'Free Trial Active';
    if (status.isTrialExpired) return 'Trial Expired';
    return 'Free Plan';
  };

  const getStatusDescription = () => {
    if (status.isActive) {
      return status.autoRenew ? 'Auto-renewal enabled' : 'Auto-renewal disabled';
    }
    if (status.isTrialActive) {
      return `${status.daysRemaining} days remaining`;
    }
    if (status.isTrialExpired) {
      return 'Upgrade to continue using premium features';
    }
    return 'Upgrade to unlock premium features';
  };

  return (
    <div className={`subscription-status ${className}`}>
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className={`font-semibold ${getStatusColor()}`}>
              {getStatusText()}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={restore}
              className="p-1 text-gray-400 hover:text-white transition-colors"
              title="Restore Purchases"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            
            {onManageSubscription && (
              <button
                onClick={onManageSubscription}
                className="p-1 text-gray-400 hover:text-white transition-colors"
                title="Manage Subscription"
              >
                <Settings className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        <p className="text-sm text-gray-300 mb-3">
          {getStatusDescription()}
        </p>

        {/* Progress Bar for Trial */}
        {status.isTrialActive && status.daysRemaining > 0 && (
          <div className="mb-3">
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>Trial Progress</span>
              <span>{status.daysRemaining} days left</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ 
                  width: `${((14 - status.daysRemaining) / 14) * 100}%` 
                }}
              ></div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2">
          {!status.isActive && !status.isTrialActive && (
            <button className="flex-1 bg-blue-600 text-white py-2 px-3 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
              Upgrade to Premium
            </button>
          )}
          
          {status.isTrialActive && (
            <button className="flex-1 bg-green-600 text-white py-2 px-3 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors">
              Subscribe Now
            </button>
          )}
          
          {status.isTrialExpired && (
            <button className="flex-1 bg-orange-600 text-white py-2 px-3 rounded-lg text-sm font-medium hover:bg-orange-700 transition-colors">
              Renew Subscription
            </button>
          )}
        </div>

        {/* Additional Info */}
        {status.subscriptionEndDate && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <p className="text-xs text-gray-500">
              {status.isActive ? 'Next billing' : 'Expires'}: {' '}
              {status.subscriptionEndDate.toLocaleDateString()}
            </p>
          </div>
        )}

        {status.trialEndDate && status.isTrialActive && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <p className="text-xs text-gray-500">
              Trial ends: {status.trialEndDate.toLocaleDateString()}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
