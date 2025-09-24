import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import jwt from 'jsonwebtoken';
import Stripe from 'stripe';

const prisma = new PrismaClient();
const JWT_SECRET = process.env.JWT_SECRET || 'nexteleven-crowley-edition-2024-apollo-powered';
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || 'sk_test_...', {
  apiVersion: '2023-10-16',
});

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
    const appointmentId = searchParams.get('appointmentId');
    const customerId = searchParams.get('customerId');
    const status = searchParams.get('status');

    let whereClause: any = {};

    if (appointmentId) {
      whereClause.appointmentId = appointmentId;
    }

    if (customerId) {
      whereClause.customerId = customerId;
    }

    if (status) {
      whereClause.status = status;
    }

    const payments = await prisma.payment.findMany({
      where: whereClause,
      include: {
        appointment: {
          include: {
            customer: true,
            artist: true
          }
        },
        customer: true
      },
      orderBy: {
        createdAt: 'desc'
      }
    });

    return NextResponse.json({
      success: true,
      payments
    });

  } catch (error) {
    console.error('Get payments error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch payments' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}

export async function POST(request: NextRequest) {
  try {
    const decoded = await verifyToken(request);
    const paymentData = await request.json();

    // Validate required fields
    if (!paymentData.appointmentId || !paymentData.amount || !paymentData.method) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Get appointment details
    const appointment = await prisma.appointment.findUnique({
      where: { id: paymentData.appointmentId },
      include: {
        customer: true,
        artist: true
      }
    });

    if (!appointment) {
      return NextResponse.json(
        { error: 'Appointment not found' },
        { status: 404 }
      );
    }

    let paymentIntent;
    let transactionId = null;

    // Handle different payment methods
    if (paymentData.method === 'CARD') {
      // Create Stripe payment intent
      paymentIntent = await stripe.paymentIntents.create({
        amount: Math.round(paymentData.amount * 100), // Convert to cents
        currency: 'usd',
        metadata: {
          appointmentId: paymentData.appointmentId,
          customerId: appointment.customerId,
          artistId: appointment.artistId
        },
        automatic_payment_methods: {
          enabled: true,
        },
      });

      transactionId = paymentIntent.id;
    } else if (paymentData.method === 'CRYPTO') {
      // For crypto payments, we'll simulate a transaction ID
      transactionId = `crypto_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    } else if (paymentData.method === 'DIGITAL_WALLET') {
      // For digital wallet payments
      transactionId = `wallet_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Create payment record
    const payment = await prisma.payment.create({
      data: {
        appointmentId: paymentData.appointmentId,
        customerId: appointment.customerId,
        amount: paymentData.amount,
        method: paymentData.method,
        status: paymentData.method === 'CARD' ? 'PENDING' : 'COMPLETED',
        transactionId: transactionId,
        processedAt: paymentData.method !== 'CARD' ? new Date() : null
      },
      include: {
        appointment: {
          include: {
            customer: true,
            artist: true
          }
        },
        customer: true
      }
    });

    // Create notification
    await prisma.notification.create({
      data: {
        userId: decoded.userId,
        type: 'PAYMENT_CONFIRMATION',
        title: 'Payment Processed',
        message: `Payment of $${paymentData.amount} has been processed for your appointment with ${appointment.artist.name}`,
        data: JSON.stringify({
          paymentId: payment.id,
          amount: paymentData.amount,
          method: paymentData.method,
          appointmentId: paymentData.appointmentId
        })
      }
    });

    return NextResponse.json({
      success: true,
      payment,
      clientSecret: paymentIntent?.client_secret || null
    }, { status: 201 });

  } catch (error) {
    console.error('Create payment error:', error);
    return NextResponse.json(
      { error: 'Failed to create payment' },
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

    const payment = await prisma.payment.findUnique({
      where: { id }
    });
    
    if (!payment) {
      return NextResponse.json(
        { error: 'Payment not found' },
        { status: 404 }
      );
    }

    const updatedPayment = await prisma.payment.update({
      where: { id },
      data: {
        ...updates,
        processedAt: updates.status === 'COMPLETED' && !payment.processedAt ? new Date() : payment.processedAt
      },
      include: {
        appointment: {
          include: {
            customer: true,
            artist: true
          }
        },
        customer: true
      }
    });

    // Create notification for status changes
    if (updates.status && updates.status !== payment.status) {
      await prisma.notification.create({
        data: {
          userId: decoded.userId,
          type: 'PAYMENT_CONFIRMATION',
          title: 'Payment Status Updated',
          message: `Your payment status has been updated to ${updates.status}`,
          data: JSON.stringify({
            paymentId: payment.id,
            oldStatus: payment.status,
            newStatus: updates.status
          })
        }
      });
    }

    return NextResponse.json({
      success: true,
      payment: updatedPayment
    });

  } catch (error) {
    console.error('Update payment error:', error);
    return NextResponse.json(
      { error: 'Failed to update payment' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}

// Stripe webhook handler
export async function PATCH(request: NextRequest) {
  try {
    const body = await request.text();
    const signature = request.headers.get('stripe-signature');

    if (!signature) {
      return NextResponse.json(
        { error: 'No signature provided' },
        { status: 400 }
      );
    }

    let event;
    try {
      event = stripe.webhooks.constructEvent(
        body,
        signature,
        process.env.STRIPE_WEBHOOK_SECRET || 'whsec_...'
      );
    } catch (err) {
      console.error('Webhook signature verification failed:', err);
      return NextResponse.json(
        { error: 'Invalid signature' },
        { status: 400 }
      );
    }

    // Handle the event
    switch (event.type) {
      case 'payment_intent.succeeded':
        const paymentIntent = event.data.object;
        
        // Update payment status
        await prisma.payment.updateMany({
          where: { transactionId: paymentIntent.id },
          data: {
            status: 'COMPLETED',
            processedAt: new Date()
          }
        });

        // Update appointment status if payment is completed
        const payment = await prisma.payment.findFirst({
          where: { transactionId: paymentIntent.id },
          include: { appointment: true }
        });

        if (payment) {
          await prisma.appointment.update({
            where: { id: payment.appointmentId },
            data: { status: 'CONFIRMED' }
          });
        }
        break;

      case 'payment_intent.payment_failed':
        const failedPayment = event.data.object;
        
        // Update payment status
        await prisma.payment.updateMany({
          where: { transactionId: failedPayment.id },
          data: { status: 'FAILED' }
        });
        break;

      default:
        console.log(`Unhandled event type ${event.type}`);
    }

    return NextResponse.json({ received: true });

  } catch (error) {
    console.error('Webhook error:', error);
    return NextResponse.json(
      { error: 'Webhook processing failed' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}
