// APOLLO-GUIDED Subscriber Integration API Endpoints
import { NextRequest, NextResponse } from 'next/server';
import { apolloSubscriberIntegrationManager } from '../../../lib/subscriber-integration-manager';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    
    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    const preferences = apolloSubscriberIntegrationManager.getSubscriberPreferences(userId);
    const integrationStatus = apolloSubscriberIntegrationManager.getIntegrationStatus(userId);

    return NextResponse.json({
      success: true,
      data: {
        preferences,
        integrationStatus,
      },
    }, { status: 200 });
  } catch (error: any) {
    console.error('❌ Subscriber Integration API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch subscriber integrations', details: error.message },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const { action, userId, data } = await request.json();

    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    let result;
    switch (action) {
      case 'add_payment_method':
        result = await apolloSubscriberIntegrationManager.addPaymentMethod(userId, data);
        break;
      case 'add_calendar_integration':
        result = await apolloSubscriberIntegrationManager.addCalendarIntegration(userId, data);
        break;
      case 'update_subscription_tier':
        result = await apolloSubscriberIntegrationManager.updateSubscriptionTier(userId, data.tier);
        break;
      case 'check_feature_access':
        result = apolloSubscriberIntegrationManager.hasFeatureAccess(userId, data.featureId);
        break;
      case 'check_usage_limit':
        result = apolloSubscriberIntegrationManager.checkUsageLimit(userId, data.featureId);
        break;
      case 'update_usage':
        apolloSubscriberIntegrationManager.updateUsage(userId, data.featureId, data.increment);
        result = { success: true };
        break;
      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }

    return NextResponse.json({
      success: true,
      data: result,
    }, { status: 200 });
  } catch (error: any) {
    console.error('❌ Subscriber Integration API error:', error);
    return NextResponse.json(
      { error: 'Failed to process subscriber integration action', details: error.message },
      { status: 500 }
    );
  }
}
