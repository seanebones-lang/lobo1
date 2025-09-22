import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { apolloPerformance } from '../../lib/performance';
import { apolloCache } from '../../lib/cache';

const prisma = new PrismaClient();

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get('type') || 'overview';
    const dateRange = searchParams.get('range') || '30';
    const userId = searchParams.get('userId');

    // Check cache first
    const cacheKey = `analytics_${type}_${dateRange}_${userId || 'all'}`;
    const cached = apolloCache.get(cacheKey);
    if (cached) {
      return NextResponse.json({ success: true, data: cached, cached: true });
    }

    let data;

    switch (type) {
      case 'overview':
        data = await getOverviewAnalytics(dateRange);
        break;
      case 'revenue':
        data = await getRevenueAnalytics(dateRange);
        break;
      case 'appointments':
        data = await getAppointmentAnalytics(dateRange);
        break;
      case 'artists':
        data = await getArtistAnalytics(dateRange);
        break;
      case 'customers':
        data = await getCustomerAnalytics(dateRange);
        break;
      case 'performance':
        data = apolloPerformance.getPerformanceSummary();
        break;
      case 'system':
        data = apolloPerformance.getSystemHealth();
        break;
      case 'api':
        data = apolloPerformance.getAPIStats();
        break;
      default:
        data = await getOverviewAnalytics(dateRange);
    }

    // Cache the result for 5 minutes
    apolloCache.set(cacheKey, data, 5 * 60 * 1000);

    return NextResponse.json({ success: true, data });

  } catch (error) {
    console.error('Analytics API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch analytics data' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}

async function getOverviewAnalytics(dateRange: string) {
  const days = parseInt(dateRange);
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  const [
    totalAppointments,
    totalRevenue,
    totalCustomers,
    newCustomers,
    completedAppointments,
    pendingAppointments,
    cancelledAppointments
  ] = await Promise.all([
    prisma.appointment.count({
      where: { createdAt: { gte: startDate } }
    }),
    prisma.payment.aggregate({
      where: { 
        status: 'COMPLETED',
        createdAt: { gte: startDate }
      },
      _sum: { amount: true }
    }),
    prisma.customer.count({
      where: { createdAt: { gte: startDate } }
    }),
    prisma.customer.count({
      where: { 
        createdAt: { 
          gte: new Date(startDate.getTime() + (days - 7) * 24 * 60 * 60 * 1000) 
        }
      }
    }),
    prisma.appointment.count({
      where: { 
        status: 'COMPLETED',
        createdAt: { gte: startDate }
      }
    }),
    prisma.appointment.count({
      where: { 
        status: 'PENDING',
        createdAt: { gte: startDate }
      }
    }),
    prisma.appointment.count({
      where: { 
        status: 'CANCELLED',
        createdAt: { gte: startDate }
      }
    })
  ]);

  return {
    totalAppointments,
    totalRevenue: totalRevenue._sum.amount || 0,
    totalCustomers,
    newCustomers,
    completedAppointments,
    pendingAppointments,
    cancelledAppointments,
    completionRate: totalAppointments > 0 ? (completedAppointments / totalAppointments) * 100 : 0,
    cancellationRate: totalAppointments > 0 ? (cancelledAppointments / totalAppointments) * 100 : 0
  };
}

async function getRevenueAnalytics(dateRange: string) {
  const days = parseInt(dateRange);
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  // Daily revenue for the period
  const dailyRevenue = [];
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const nextDate = new Date(date);
    nextDate.setDate(nextDate.getDate() + 1);

    const revenue = await prisma.payment.aggregate({
      where: {
        status: 'COMPLETED',
        createdAt: {
          gte: date,
          lt: nextDate
        }
      },
      _sum: { amount: true }
    });

    dailyRevenue.push({
      date: date.toISOString().split('T')[0],
      revenue: revenue._sum.amount || 0
    });
  }

  // Revenue by payment method
  const revenueByMethod = await prisma.payment.groupBy({
    by: ['method'],
    where: {
      status: 'COMPLETED',
      createdAt: { gte: startDate }
    },
    _sum: { amount: true },
    _count: { id: true }
  });

  // Revenue by artist
  const revenueByArtist = await prisma.payment.findMany({
    where: {
      status: 'COMPLETED',
      createdAt: { gte: startDate }
    },
    include: {
      appointment: {
        include: {
          artist: true
        }
      }
    }
  });

  const artistRevenue = revenueByArtist.reduce((acc, payment) => {
    const artistName = payment.appointment.artist.name;
    if (!acc[artistName]) {
      acc[artistName] = { revenue: 0, count: 0 };
    }
    acc[artistName].revenue += payment.amount;
    acc[artistName].count += 1;
    return acc;
  }, {} as Record<string, { revenue: number; count: number }>);

  return {
    dailyRevenue,
    revenueByMethod,
    artistRevenue: Object.entries(artistRevenue).map(([artist, data]) => ({
      artist,
      revenue: data.revenue,
      count: data.count
    }))
  };
}

async function getAppointmentAnalytics(dateRange: string) {
  const days = parseInt(dateRange);
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  // Appointments by status
  const appointmentsByStatus = await prisma.appointment.groupBy({
    by: ['status'],
    where: { createdAt: { gte: startDate } },
    _count: { id: true }
  });

  // Appointments by service type
  const appointmentsByService = await prisma.appointment.groupBy({
    by: ['serviceType'],
    where: { createdAt: { gte: startDate } },
    _count: { id: true }
  });

  // Average appointment duration
  const avgDuration = await prisma.appointment.aggregate({
    where: { 
      createdAt: { gte: startDate },
      status: 'COMPLETED'
    },
    _avg: { duration: true }
  });

  // Peak hours analysis
  const appointments = await prisma.appointment.findMany({
    where: { createdAt: { gte: startDate } },
    select: { date: true }
  });

  const hourCounts = new Array(24).fill(0);
  appointments.forEach(appointment => {
    const hour = new Date(appointment.date).getHours();
    hourCounts[hour]++;
  });

  const peakHours = hourCounts
    .map((count, hour) => ({ hour, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  return {
    appointmentsByStatus,
    appointmentsByService,
    averageDuration: avgDuration._avg.duration || 0,
    peakHours
  };
}

async function getArtistAnalytics(dateRange: string) {
  const days = parseInt(dateRange);
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  const artists = await prisma.artist.findMany({
    include: {
      appointments: {
        where: { createdAt: { gte: startDate } },
        include: {
          payments: {
            where: { status: 'COMPLETED' }
          }
        }
      }
    }
  });

  const artistStats = artists.map(artist => {
    const appointments = artist.appointments;
    const revenue = appointments.reduce((sum, apt) => 
      sum + apt.payments.reduce((sum, payment) => sum + payment.amount, 0), 0
    );
    const completedAppointments = appointments.filter(apt => apt.status === 'COMPLETED').length;
    const avgRating = 4.5; // This would come from a ratings system

    return {
      id: artist.id,
      name: artist.name,
      specialty: artist.specialty,
      appointments: appointments.length,
      completedAppointments,
      revenue,
      averageRating: avgRating,
      hourlyRate: artist.hourlyRate,
      isActive: artist.isActive
    };
  });

  return artistStats.sort((a, b) => b.revenue - a.revenue);
}

async function getCustomerAnalytics(dateRange: string) {
  const days = parseInt(dateRange);
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);

  const customers = await prisma.customer.findMany({
    where: { createdAt: { gte: startDate } },
    include: {
      appointments: {
        include: {
          payments: {
            where: { status: 'COMPLETED' }
          }
        }
      }
    }
  });

  const customerStats = customers.map(customer => {
    const appointments = customer.appointments;
    const totalSpent = appointments.reduce((sum, apt) => 
      sum + apt.payments.reduce((sum, payment) => sum + payment.amount, 0), 0
    );

    return {
      id: customer.id,
      name: customer.name,
      email: customer.email,
      appointments: appointments.length,
      totalSpent,
      lastAppointment: appointments.length > 0 
        ? Math.max(...appointments.map(apt => new Date(apt.date).getTime()))
        : null
    };
  });

  return customerStats.sort((a, b) => b.totalSpent - a.totalSpent);
}

export async function POST(request: NextRequest) {
  try {
    const { event, data, userId } = await request.json();

    // Record custom analytics event
    await prisma.analytics.create({
      data: {
        date: new Date(),
        metric: event,
        value: data.value || 1,
        metadata: JSON.stringify({ ...data, userId })
      }
    });

    // Record performance metric
    apolloPerformance.recordMetric(`analytics_${event}`, data.value || 1, {
      userId: userId || 'anonymous',
      timestamp: Date.now().toString()
    });

    return NextResponse.json({ success: true });

  } catch (error) {
    console.error('Analytics tracking error:', error);
    return NextResponse.json(
      { error: 'Failed to track analytics event' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}
