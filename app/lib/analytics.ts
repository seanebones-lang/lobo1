// APOLLO-GUIDED Advanced Analytics System
import { NextRequest } from 'next/server';

interface AnalyticsEvent {
  id: string;
  type: string;
  category: string;
  action: string;
  label?: string;
  value?: number;
  properties: Record<string, any>;
  timestamp: Date;
  sessionId: string;
  userId?: string;
  userAgent: string;
  ip: string;
  referrer?: string;
}

interface AnalyticsMetrics {
  pageViews: number;
  uniqueVisitors: number;
  bounceRate: number;
  averageSessionDuration: number;
  conversionRate: number;
  topPages: Array<{ path: string; views: number }>;
  topReferrers: Array<{ source: string; visits: number }>;
  deviceBreakdown: Array<{ device: string; percentage: number }>;
  browserBreakdown: Array<{ browser: string; percentage: number }>;
  geographicData: Array<{ country: string; visits: number }>;
  hourlyDistribution: Array<{ hour: number; visits: number }>;
  dailyDistribution: Array<{ day: string; visits: number }>;
}

interface BusinessMetrics {
  totalRevenue: number;
  monthlyRevenue: number;
  averageOrderValue: number;
  totalAppointments: number;
  completedAppointments: number;
  cancelledAppointments: number;
  newCustomers: number;
  returningCustomers: number;
  customerRetentionRate: number;
  topServices: Array<{ service: string; bookings: number; revenue: number }>;
  artistPerformance: Array<{ artist: string; appointments: number; revenue: number; rating: number }>;
  seasonalTrends: Array<{ month: string; bookings: number; revenue: number }>;
}

class ApolloAnalytics {
  private events: AnalyticsEvent[] = [];
  private sessions: Map<string, any> = new Map();
  private userProfiles: Map<string, any> = new Map();
  private businessData: Map<string, any> = new Map();

  // Event tracking
  trackEvent(
    type: string,
    category: string,
    action: string,
    label?: string,
    value?: number,
    properties: Record<string, any> = {},
    request?: NextRequest
  ): void {
    const event: AnalyticsEvent = {
      id: this.generateId(),
      type,
      category,
      action,
      label,
      value,
      properties,
      timestamp: new Date(),
      sessionId: this.getOrCreateSession(request),
      userId: this.getUserId(request),
      userAgent: request?.headers.get('user-agent') || 'unknown',
      ip: this.getClientIP(request),
      referrer: request?.headers.get('referer') || undefined,
    };

    this.events.push(event);
    this.updateSessionMetrics(event);
    this.updateUserProfile(event);
    
    console.log(`🌊 APOLLO Analytics: Tracked ${type} - ${category}.${action}`);
  }

  // Page view tracking
  trackPageView(path: string, title: string, request?: NextRequest): void {
    this.trackEvent(
      'page_view',
      'navigation',
      'view',
      title,
      undefined,
      { path, title },
      request
    );
  }

  // User interaction tracking
  trackInteraction(
    element: string,
    action: string,
    properties: Record<string, any> = {},
    request?: NextRequest
  ): void {
    this.trackEvent(
      'interaction',
      'user_action',
      action,
      element,
      undefined,
      properties,
      request
    );
  }

  // Business event tracking
  trackBusinessEvent(
    eventType: 'appointment_booked' | 'appointment_completed' | 'appointment_cancelled' | 'payment_completed' | 'customer_registered',
    data: Record<string, any>,
    request?: NextRequest
  ): void {
    this.trackEvent(
      'business',
      'appointment',
      eventType,
      undefined,
      data.value || 0,
      data,
      request
    );

    this.updateBusinessMetrics(eventType, data);
  }

  // Performance tracking
  trackPerformance(
    metric: string,
    value: number,
    properties: Record<string, any> = {},
    request?: NextRequest
  ): void {
    this.trackEvent(
      'performance',
      'timing',
      metric,
      undefined,
      value,
      properties,
      request
    );
  }

  // Error tracking
  trackError(
    error: Error,
    context: Record<string, any> = {},
    request?: NextRequest
  ): void {
    this.trackEvent(
      'error',
      'exception',
      'error',
      error.message,
      undefined,
      {
        ...context,
        stack: error.stack,
        name: error.name,
      },
      request
    );
  }

  // Get analytics metrics
  getAnalyticsMetrics(timeRange: '24h' | '7d' | '30d' | '90d' | '1y' = '7d'): AnalyticsMetrics {
    const now = new Date();
    const startDate = this.getStartDate(timeRange, now);
    const filteredEvents = this.events.filter(event => event.timestamp >= startDate);

    return {
      pageViews: this.getPageViews(filteredEvents),
      uniqueVisitors: this.getUniqueVisitors(filteredEvents),
      bounceRate: this.getBounceRate(filteredEvents),
      averageSessionDuration: this.getAverageSessionDuration(filteredEvents),
      conversionRate: this.getConversionRate(filteredEvents),
      topPages: this.getTopPages(filteredEvents),
      topReferrers: this.getTopReferrers(filteredEvents),
      deviceBreakdown: this.getDeviceBreakdown(filteredEvents),
      browserBreakdown: this.getBrowserBreakdown(filteredEvents),
      geographicData: this.getGeographicData(filteredEvents),
      hourlyDistribution: this.getHourlyDistribution(filteredEvents),
      dailyDistribution: this.getDailyDistribution(filteredEvents),
    };
  }

  // Get business metrics
  getBusinessMetrics(timeRange: '24h' | '7d' | '30d' | '90d' | '1y' = '30d'): BusinessMetrics {
    const now = new Date();
    const startDate = this.getStartDate(timeRange, now);
    const filteredEvents = this.events.filter(event => 
      event.timestamp >= startDate && event.category === 'business'
    );

    return {
      totalRevenue: this.getTotalRevenue(filteredEvents),
      monthlyRevenue: this.getMonthlyRevenue(filteredEvents),
      averageOrderValue: this.getAverageOrderValue(filteredEvents),
      totalAppointments: this.getTotalAppointments(filteredEvents),
      completedAppointments: this.getCompletedAppointments(filteredEvents),
      cancelledAppointments: this.getCancelledAppointments(filteredEvents),
      newCustomers: this.getNewCustomers(filteredEvents),
      returningCustomers: this.getReturningCustomers(filteredEvents),
      customerRetentionRate: this.getCustomerRetentionRate(filteredEvents),
      topServices: this.getTopServices(filteredEvents),
      artistPerformance: this.getArtistPerformance(filteredEvents),
      seasonalTrends: this.getSeasonalTrends(filteredEvents),
    };
  }

  // Real-time analytics
  getRealTimeMetrics(): {
    activeUsers: number;
    currentPageViews: number;
    topCurrentPages: Array<{ path: string; views: number }>;
    recentEvents: AnalyticsEvent[];
  } {
    const now = new Date();
    const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000);
    const recentEvents = this.events.filter(event => event.timestamp >= fiveMinutesAgo);

    return {
      activeUsers: this.getActiveUsers(recentEvents),
      currentPageViews: this.getCurrentPageViews(recentEvents),
      topCurrentPages: this.getTopCurrentPages(recentEvents),
      recentEvents: recentEvents.slice(-10),
    };
  }

  // Private helper methods
  private generateId(): string {
    return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  }

  private getOrCreateSession(request?: NextRequest): string {
    // In a real implementation, this would use cookies or session storage
    return 'session_' + Math.random().toString(36).substr(2, 9);
  }

  private getUserId(request?: NextRequest): string | undefined {
    // In a real implementation, this would extract from JWT or session
    return undefined;
  }

  private getClientIP(request?: NextRequest): string {
    if (!request) return 'unknown';
    
    const forwarded = request.headers.get('x-forwarded-for');
    const realIP = request.headers.get('x-real-ip');
    
    if (forwarded) {
      return forwarded.split(',')[0].trim();
    }
    
    if (realIP) {
      return realIP;
    }
    
    return 'unknown';
  }

  private getStartDate(timeRange: string, now: Date): Date {
    const ranges = {
      '24h': 24 * 60 * 60 * 1000,
      '7d': 7 * 24 * 60 * 60 * 1000,
      '30d': 30 * 24 * 60 * 60 * 1000,
      '90d': 90 * 24 * 60 * 60 * 1000,
      '1y': 365 * 24 * 60 * 60 * 1000,
    };
    
    return new Date(now.getTime() - ranges[timeRange as keyof typeof ranges]);
  }

  private updateSessionMetrics(event: AnalyticsEvent): void {
    const session = this.sessions.get(event.sessionId) || {
      startTime: event.timestamp,
      lastActivity: event.timestamp,
      pageViews: 0,
      events: [],
    };
    
    session.lastActivity = event.timestamp;
    session.events.push(event);
    
    if (event.type === 'page_view') {
      session.pageViews++;
    }
    
    this.sessions.set(event.sessionId, session);
  }

  private updateUserProfile(event: AnalyticsEvent): void {
    if (!event.userId) return;
    
    const profile = this.userProfiles.get(event.userId) || {
      firstSeen: event.timestamp,
      lastSeen: event.timestamp,
      totalEvents: 0,
      preferences: {},
    };
    
    profile.lastSeen = event.timestamp;
    profile.totalEvents++;
    
    this.userProfiles.set(event.userId, profile);
  }

  private updateBusinessMetrics(eventType: string, data: Record<string, any>): void {
    const key = `${eventType}_${new Date().toISOString().split('T')[0]}`;
    const current = this.businessData.get(key) || 0;
    this.businessData.set(key, current + (data.value || 1));
  }

  // Metric calculation methods
  private getPageViews(events: AnalyticsEvent[]): number {
    return events.filter(e => e.type === 'page_view').length;
  }

  private getUniqueVisitors(events: AnalyticsEvent[]): number {
    const uniqueSessions = new Set(events.map(e => e.sessionId));
    return uniqueSessions.size;
  }

  private getBounceRate(events: AnalyticsEvent[]): number {
    const sessions = new Map<string, AnalyticsEvent[]>();
    
    events.forEach(event => {
      if (!sessions.has(event.sessionId)) {
        sessions.set(event.sessionId, []);
      }
      sessions.get(event.sessionId)!.push(event);
    });
    
    const singlePageSessions = Array.from(sessions.values())
      .filter(sessionEvents => sessionEvents.filter(e => e.type === 'page_view').length === 1);
    
    return sessions.size > 0 ? (singlePageSessions.length / sessions.size) * 100 : 0;
  }

  private getAverageSessionDuration(events: AnalyticsEvent[]): number {
    const sessions = new Map<string, { start: Date; end: Date }>();
    
    events.forEach(event => {
      if (!sessions.has(event.sessionId)) {
        sessions.set(event.sessionId, { start: event.timestamp, end: event.timestamp });
      } else {
        const session = sessions.get(event.sessionId)!;
        if (event.timestamp < session.start) session.start = event.timestamp;
        if (event.timestamp > session.end) session.end = event.timestamp;
      }
    });
    
    const durations = Array.from(sessions.values())
      .map(session => session.end.getTime() - session.start.getTime());
    
    return durations.length > 0 ? durations.reduce((a, b) => a + b, 0) / durations.length / 1000 : 0;
  }

  private getConversionRate(events: AnalyticsEvent[]): number {
    const totalSessions = new Set(events.map(e => e.sessionId)).size;
    const conversionEvents = events.filter(e => 
      e.category === 'business' && 
      ['appointment_booked', 'payment_completed'].includes(e.action)
    ).length;
    
    return totalSessions > 0 ? (conversionEvents / totalSessions) * 100 : 0;
  }

  private getTopPages(events: AnalyticsEvent[]): Array<{ path: string; views: number }> {
    const pageViews = events.filter(e => e.type === 'page_view');
    const pageCounts = new Map<string, number>();
    
    pageViews.forEach(event => {
      const path = event.properties.path || 'unknown';
      pageCounts.set(path, (pageCounts.get(path) || 0) + 1);
    });
    
    return Array.from(pageCounts.entries())
      .map(([path, views]) => ({ path, views }))
      .sort((a, b) => b.views - a.views)
      .slice(0, 10);
  }

  private getTopReferrers(events: AnalyticsEvent[]): Array<{ source: string; visits: number }> {
    const referrerCounts = new Map<string, number>();
    
    events.forEach(event => {
      const referrer = event.referrer || 'direct';
      referrerCounts.set(referrer, (referrerCounts.get(referrer) || 0) + 1);
    });
    
    return Array.from(referrerCounts.entries())
      .map(([source, visits]) => ({ source, visits }))
      .sort((a, b) => b.visits - a.visits)
      .slice(0, 10);
  }

  private getDeviceBreakdown(events: AnalyticsEvent[]): Array<{ device: string; percentage: number }> {
    const deviceCounts = new Map<string, number>();
    
    events.forEach(event => {
      const userAgent = event.userAgent.toLowerCase();
      let device = 'desktop';
      
      if (userAgent.includes('mobile') || userAgent.includes('android')) {
        device = 'mobile';
      } else if (userAgent.includes('tablet') || userAgent.includes('ipad')) {
        device = 'tablet';
      }
      
      deviceCounts.set(device, (deviceCounts.get(device) || 0) + 1);
    });
    
    const total = Array.from(deviceCounts.values()).reduce((a, b) => a + b, 0);
    
    return Array.from(deviceCounts.entries())
      .map(([device, count]) => ({ 
        device, 
        percentage: total > 0 ? (count / total) * 100 : 0 
      }))
      .sort((a, b) => b.percentage - a.percentage);
  }

  private getBrowserBreakdown(events: AnalyticsEvent[]): Array<{ browser: string; percentage: number }> {
    const browserCounts = new Map<string, number>();
    
    events.forEach(event => {
      const userAgent = event.userAgent.toLowerCase();
      let browser = 'unknown';
      
      if (userAgent.includes('chrome')) browser = 'chrome';
      else if (userAgent.includes('firefox')) browser = 'firefox';
      else if (userAgent.includes('safari')) browser = 'safari';
      else if (userAgent.includes('edge')) browser = 'edge';
      
      browserCounts.set(browser, (browserCounts.get(browser) || 0) + 1);
    });
    
    const total = Array.from(browserCounts.values()).reduce((a, b) => a + b, 0);
    
    return Array.from(browserCounts.entries())
      .map(([browser, count]) => ({ 
        browser, 
        percentage: total > 0 ? (count / total) * 100 : 0 
      }))
      .sort((a, b) => b.percentage - a.percentage);
  }

  private getGeographicData(events: AnalyticsEvent[]): Array<{ country: string; visits: number }> {
    // In a real implementation, this would use IP geolocation
    return [
      { country: 'United States', visits: Math.floor(Math.random() * 1000) },
      { country: 'Canada', visits: Math.floor(Math.random() * 500) },
      { country: 'United Kingdom', visits: Math.floor(Math.random() * 300) },
    ];
  }

  private getHourlyDistribution(events: AnalyticsEvent[]): Array<{ hour: number; visits: number }> {
    const hourlyCounts = new Map<number, number>();
    
    events.forEach(event => {
      const hour = event.timestamp.getHours();
      hourlyCounts.set(hour, (hourlyCounts.get(hour) || 0) + 1);
    });
    
    return Array.from({ length: 24 }, (_, hour) => ({
      hour,
      visits: hourlyCounts.get(hour) || 0,
    }));
  }

  private getDailyDistribution(events: AnalyticsEvent[]): Array<{ day: string; visits: number }> {
    const dailyCounts = new Map<string, number>();
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    
    events.forEach(event => {
      const day = days[event.timestamp.getDay()];
      dailyCounts.set(day, (dailyCounts.get(day) || 0) + 1);
    });
    
    return days.map(day => ({
      day,
      visits: dailyCounts.get(day) || 0,
    }));
  }

  // Business metric methods
  private getTotalRevenue(events: AnalyticsEvent[]): number {
    return events
      .filter(e => e.action === 'payment_completed')
      .reduce((sum, event) => sum + (event.value || 0), 0);
  }

  private getMonthlyRevenue(events: AnalyticsEvent[]): number {
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    
    return events
      .filter(e => e.action === 'payment_completed' && e.timestamp >= startOfMonth)
      .reduce((sum, event) => sum + (event.value || 0), 0);
  }

  private getAverageOrderValue(events: AnalyticsEvent[]): number {
    const paymentEvents = events.filter(e => e.action === 'payment_completed');
    const totalRevenue = paymentEvents.reduce((sum, event) => sum + (event.value || 0), 0);
    
    return paymentEvents.length > 0 ? totalRevenue / paymentEvents.length : 0;
  }

  private getTotalAppointments(events: AnalyticsEvent[]): number {
    return events.filter(e => e.action === 'appointment_booked').length;
  }

  private getCompletedAppointments(events: AnalyticsEvent[]): number {
    return events.filter(e => e.action === 'appointment_completed').length;
  }

  private getCancelledAppointments(events: AnalyticsEvent[]): number {
    return events.filter(e => e.action === 'appointment_cancelled').length;
  }

  private getNewCustomers(events: AnalyticsEvent[]): number {
    return events.filter(e => e.action === 'customer_registered').length;
  }

  private getReturningCustomers(events: AnalyticsEvent[]): number {
    // Simplified logic - in reality would track user sessions over time
    return Math.floor(events.length * 0.3);
  }

  private getCustomerRetentionRate(events: AnalyticsEvent[]): number {
    const newCustomers = this.getNewCustomers(events);
    const returningCustomers = this.getReturningCustomers(events);
    
    return newCustomers > 0 ? (returningCustomers / newCustomers) * 100 : 0;
  }

  private getTopServices(events: AnalyticsEvent[]): Array<{ service: string; bookings: number; revenue: number }> {
    // Simplified - would track actual service data
    return [
      { service: 'Tattoo Design', bookings: 45, revenue: 13500 },
      { service: 'Touch-up', bookings: 20, revenue: 2000 },
      { service: 'Cover-up', bookings: 15, revenue: 7500 },
    ];
  }

  private getArtistPerformance(events: AnalyticsEvent[]): Array<{ artist: string; appointments: number; revenue: number; rating: number }> {
    // Simplified - would track actual artist data
    return [
      { artist: 'Alex Rivera', appointments: 25, revenue: 12500, rating: 4.9 },
      { artist: 'Maya Chen', appointments: 20, revenue: 10000, rating: 4.8 },
      { artist: 'Jordan Smith', appointments: 18, revenue: 9000, rating: 4.7 },
    ];
  }

  private getSeasonalTrends(events: AnalyticsEvent[]): Array<{ month: string; bookings: number; revenue: number }> {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    return months.map(month => ({
      month,
      bookings: Math.floor(Math.random() * 50) + 20,
      revenue: Math.floor(Math.random() * 10000) + 5000,
    }));
  }

  private getActiveUsers(events: AnalyticsEvent[]): number {
    const uniqueSessions = new Set(events.map(e => e.sessionId));
    return uniqueSessions.size;
  }

  private getCurrentPageViews(events: AnalyticsEvent[]): number {
    return events.filter(e => e.type === 'page_view').length;
  }

  private getTopCurrentPages(events: AnalyticsEvent[]): Array<{ path: string; views: number }> {
    return this.getTopPages(events).slice(0, 5);
  }
}

// Export singleton instance
export const analytics = new ApolloAnalytics();
export default analytics;
