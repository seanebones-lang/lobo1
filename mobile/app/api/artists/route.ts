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
    const specialty = searchParams.get('specialty');
    const available = searchParams.get('available');
    const isActive = searchParams.get('isActive');

    let whereClause: any = {};

    if (specialty) {
      whereClause.specialty = {
        has: specialty
      };
    }

    if (isActive !== null) {
      whereClause.isActive = isActive === 'true';
    }

    if (available === 'true') {
      const today = new Date();
      const dayName = today.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
      
      whereClause.availability = {
        some: {
          dayOfWeek: dayName,
          isActive: true
        }
      };
    }

    const artists = await prisma.artist.findMany({
      where: whereClause,
      include: {
        portfolio: true,
        availability: true,
        appointments: {
          where: {
            status: {
              in: ['PENDING', 'CONFIRMED']
            }
          },
          include: {
            customer: true
          }
        }
      },
      orderBy: {
        name: 'asc'
      }
    });

    return NextResponse.json({
      success: true,
      artists
    });

  } catch (error) {
    console.error('Get artists error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch artists' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}

export async function POST(request: NextRequest) {
  try {
    const decoded = await verifyToken(request);
    
    // Check if user is admin
    if (decoded.role !== 'ADMIN') {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 403 }
      );
    }

    const artistData = await request.json();

    // Validate required fields
    if (!artistData.name || !artistData.email || !artistData.specialty || !artistData.hourlyRate) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Check if artist email already exists
    const existingArtist = await prisma.artist.findUnique({
      where: { email: artistData.email }
    });

    if (existingArtist) {
      return NextResponse.json(
        { error: 'Artist with this email already exists' },
        { status: 409 }
      );
    }

    // Create artist
    const artist = await prisma.artist.create({
      data: {
        name: artistData.name,
        email: artistData.email,
        phone: artistData.phone || '',
        specialty: artistData.specialty,
        bio: artistData.bio || '',
        hourlyRate: parseFloat(artistData.hourlyRate),
        isActive: artistData.isActive !== false
      },
      include: {
        portfolio: true,
        availability: true
      }
    });

    // Create default availability if provided
    if (artistData.availability) {
      for (const availability of artistData.availability) {
        await prisma.availability.create({
          data: {
            artistId: artist.id,
            dayOfWeek: availability.dayOfWeek,
            startTime: availability.startTime,
            endTime: availability.endTime,
            isActive: availability.isActive !== false
          }
        });
      }
    }

    return NextResponse.json({
      success: true,
      artist
    }, { status: 201 });

  } catch (error) {
    console.error('Create artist error:', error);
    return NextResponse.json(
      { error: 'Failed to create artist' },
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

    // Check if user is admin or the artist themselves
    if (decoded.role !== 'ADMIN' && decoded.role !== 'ARTIST') {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 403 }
      );
    }

    const artist = await prisma.artist.findUnique({
      where: { id }
    });
    
    if (!artist) {
      return NextResponse.json(
        { error: 'Artist not found' },
        { status: 404 }
      );
    }

    const updatedArtist = await prisma.artist.update({
      where: { id },
      data: {
        ...updates,
        hourlyRate: updates.hourlyRate ? parseFloat(updates.hourlyRate) : undefined
      },
      include: {
        portfolio: true,
        availability: true,
        appointments: {
          where: {
            status: {
              in: ['PENDING', 'CONFIRMED']
            }
          },
          include: {
            customer: true
          }
        }
      }
    });

    return NextResponse.json({
      success: true,
      artist: updatedArtist
    });

  } catch (error) {
    console.error('Update artist error:', error);
    return NextResponse.json(
      { error: 'Failed to update artist' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const decoded = await verifyToken(request);
    
    // Check if user is admin
    if (decoded.role !== 'ADMIN') {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 403 }
      );
    }

    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json(
        { error: 'Artist ID required' },
        { status: 400 }
      );
    }

    const artist = await prisma.artist.findUnique({
      where: { id }
    });
    
    if (!artist) {
      return NextResponse.json(
        { error: 'Artist not found' },
        { status: 404 }
      );
    }

    // Soft delete by setting isActive to false
    await prisma.artist.update({
      where: { id },
      data: { isActive: false }
    });

    return NextResponse.json({
      success: true,
      message: 'Artist deactivated'
    });

  } catch (error) {
    console.error('Delete artist error:', error);
    return NextResponse.json(
      { error: 'Failed to deactivate artist' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}