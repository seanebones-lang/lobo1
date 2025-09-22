import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import jwt from 'jsonwebtoken';

const prisma = new PrismaClient();
const JWT_SECRET = process.env.JWT_SECRET || 'nexteleven-crowley-edition-2024-apollo-powered';

// Helper function to verify JWT token
async function verifyToken(request: NextRequest) {
  const token = request.headers.get('authorization')?.replace('Bearer ', '');
  if (!token) throw new Error('No token provided');
  
  const decoded = jwt.verify(token, JWT_SECRET) as any;
  return decoded;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    const artistId = searchParams.get('artistId');
    const customerId = searchParams.get('customerId');
    const date = searchParams.get('date');

    let whereClause: any = {};

    if (status) {
      whereClause.status = status;
    }

    if (artistId) {
      whereClause.artistId = artistId;
    }

    if (customerId) {
      whereClause.customerId = customerId;
    }

    if (date) {
      const targetDate = new Date(date);
      const nextDay = new Date(targetDate);
      nextDay.setDate(nextDay.getDate() + 1);
      
      whereClause.date = {
        gte: targetDate,
        lt: nextDay
      };
    }

    const appointments = await prisma.appointment.findMany({
      where: whereClause,
      include: {
        customer: true,
        artist: true,
        payments: true,
        aftercare: true
      },
      orderBy: {
        date: 'asc'
      }
    });

    return NextResponse.json({
      success: true,
      appointments
    });

  } catch (error) {
    console.error('Get appointments error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch appointments' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}

export async function POST(request: NextRequest) {
  try {
    const decoded = await verifyToken(request);
    const appointmentData = await request.json();

    // Validate required fields
    if (!appointmentData.customerId || !appointmentData.artistId || !appointmentData.date) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Check for conflicts
    const conflictingAppointment = await prisma.appointment.findFirst({
      where: {
        artistId: appointmentData.artistId,
        date: new Date(appointmentData.date),
        status: {
          not: 'CANCELLED'
        }
      }
    });

    if (conflictingAppointment) {
      return NextResponse.json(
        { error: 'Time slot already booked' },
        { status: 409 }
      );
    }

    // Create appointment
    const appointment = await prisma.appointment.create({
      data: {
        customerId: appointmentData.customerId,
        artistId: appointmentData.artistId,
        serviceType: appointmentData.serviceType || 'Custom Tattoo',
        date: new Date(appointmentData.date),
        duration: appointmentData.duration || 120,
        price: appointmentData.price || 0,
        status: 'PENDING',
        notes: appointmentData.notes || ''
      },
      include: {
        customer: true,
        artist: true
      }
    });

    // Create notification
    await prisma.notification.create({
      data: {
        userId: decoded.userId,
        type: 'APPOINTMENT_REMINDER',
        title: 'Appointment Booked',
        message: `Your appointment with ${appointment.artist.name} has been booked for ${appointment.date.toLocaleDateString()}`,
        data: JSON.stringify({
          appointmentId: appointment.id,
          artistName: appointment.artist.name,
          date: appointment.date
        })
      }
    });

    return NextResponse.json({
      success: true,
      appointment
    }, { status: 201 });

  } catch (error) {
    console.error('Create appointment error:', error);
    return NextResponse.json(
      { error: 'Failed to create appointment' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}

export async function PUT(request: NextRequest) {
  try {
    const decoded = await verifyToken(request);
    const { id, updates } = await request.json();

    const appointment = await prisma.appointment.findUnique({
      where: { id }
    });
    
    if (!appointment) {
      return NextResponse.json(
        { error: 'Appointment not found' },
        { status: 404 }
      );
    }

    const updatedAppointment = await prisma.appointment.update({
      where: { id },
      data: {
        ...updates,
        date: updates.date ? new Date(updates.date) : undefined
      },
      include: {
        customer: true,
        artist: true,
        payments: true,
        aftercare: true
      }
    });

    // Create notification for status changes
    if (updates.status && updates.status !== appointment.status) {
      await prisma.notification.create({
        data: {
          userId: decoded.userId,
          type: 'APPOINTMENT_REMINDER',
          title: 'Appointment Updated',
          message: `Your appointment status has been updated to ${updates.status}`,
        data: JSON.stringify({
          appointmentId: appointment.id,
          oldStatus: appointment.status,
          newStatus: updates.status
        })
        }
      });
    }

    return NextResponse.json({
      success: true,
      appointment: updatedAppointment
    });

  } catch (error) {
    console.error('Update appointment error:', error);
    return NextResponse.json(
      { error: 'Failed to update appointment' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const decoded = await verifyToken(request);
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json(
        { error: 'Appointment ID required' },
        { status: 400 }
      );
    }

    const appointment = await prisma.appointment.findUnique({
      where: { id }
    });
    
    if (!appointment) {
      return NextResponse.json(
        { error: 'Appointment not found' },
        { status: 404 }
      );
    }

    // Soft delete by changing status to CANCELLED
    await prisma.appointment.update({
      where: { id },
      data: { status: 'CANCELLED' }
    });

    // Create notification
    await prisma.notification.create({
      data: {
        userId: decoded.userId,
        type: 'APPOINTMENT_REMINDER',
        title: 'Appointment Cancelled',
        message: 'Your appointment has been cancelled',
        data: JSON.stringify({
          appointmentId: id
        })
      }
    });

    return NextResponse.json({
      success: true,
      message: 'Appointment cancelled'
    });

  } catch (error) {
    console.error('Delete appointment error:', error);
    return NextResponse.json(
      { error: 'Failed to cancel appointment' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}