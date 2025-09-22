import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { apolloCache } from '../../../lib/cache';
import { apolloPerformance } from '../../../lib/performance';

const prisma = new PrismaClient();

interface SyncItem {
  id: string;
  type: 'appointment' | 'customer' | 'artist' | 'message' | 'analytics';
  data: any;
  timestamp: number;
  version: number;
  deviceId: string;
  userId: string;
  status: 'pending' | 'synced' | 'conflict' | 'error';
}

interface SyncBatchRequest {
  items: SyncItem[];
  deviceId: string;
  userId: string;
}

interface SyncBatchResponse {
  synced: string[];
  conflicts: any[];
  errors: any[];
  timestamp: number;
}

export async function POST(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    const body: SyncBatchRequest = await request.json();
    const { items, deviceId, userId } = body;

    // Validate request
    if (!items || !Array.isArray(items) || items.length === 0) {
      return NextResponse.json(
        { error: 'Invalid sync items' },
        { status: 400 }
      );
    }

    if (!deviceId || !userId) {
      return NextResponse.json(
        { error: 'Missing deviceId or userId' },
        { status: 400 }
      );
    }

    // Process sync items
    const result = await processSyncItems(items, deviceId, userId);

    // Record performance metric
    const duration = Date.now() - startTime;
    apolloPerformance.recordAPICall('/api/sync/batch', 'POST', duration, 200, userId);

    return NextResponse.json(result, { status: 200 });

  } catch (error) {
    console.error('Sync batch API error:', error);
    
    const duration = Date.now() - startTime;
    apolloPerformance.recordAPICall('/api/sync/batch', 'POST', duration, 500);

    return NextResponse.json(
      { 
        error: 'Sync batch failed',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}

async function processSyncItems(
  items: SyncItem[],
  deviceId: string,
  userId: string
): Promise<SyncBatchResponse> {
  const synced: string[] = [];
  const conflicts: any[] = [];
  const errors: any[] = [];

  // Group items by type for batch processing
  const itemsByType = groupItemsByType(items);

  for (const [type, typeItems] of Array.from(itemsByType.entries())) {
    try {
      const result = await processItemsByType(type, typeItems, deviceId, userId);
      synced.push(...result.synced);
      conflicts.push(...result.conflicts);
      errors.push(...result.errors);
    } catch (error) {
      console.error(`Error processing ${type} items:`, error);
      typeItems.forEach(item => {
        errors.push({
          itemId: item.id,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      });
    }
  }

  return {
    synced,
    conflicts,
    errors,
    timestamp: Date.now()
  };
}

function groupItemsByType(items: SyncItem[]): Map<string, SyncItem[]> {
  const grouped = new Map<string, SyncItem[]>();
  
  items.forEach(item => {
    if (!grouped.has(item.type)) {
      grouped.set(item.type, []);
    }
    grouped.get(item.type)!.push(item);
  });

  return grouped;
}

async function processItemsByType(
  type: string,
  items: SyncItem[],
  deviceId: string,
  userId: string
): Promise<{ synced: string[]; conflicts: any[]; errors: any[] }> {
  const synced: string[] = [];
  const conflicts: any[] = [];
  const errors: any[] = [];

  switch (type) {
    case 'appointment':
      return await processAppointmentItems(items, deviceId, userId);
    case 'customer':
      return await processCustomerItems(items, deviceId, userId);
    case 'artist':
      return await processArtistItems(items, deviceId, userId);
    case 'message':
      return await processMessageItems(items, deviceId, userId);
    case 'analytics':
      return await processAnalyticsItems(items, deviceId, userId);
    default:
      items.forEach(item => {
        errors.push({
          itemId: item.id,
          error: `Unknown item type: ${type}`
        });
      });
      return { synced, conflicts, errors };
  }
}

async function processAppointmentItems(
  items: SyncItem[],
  deviceId: string,
  userId: string
): Promise<{ synced: string[]; conflicts: any[]; errors: any[] }> {
  const synced: string[] = [];
  const conflicts: any[] = [];
  const errors: any[] = [];

  for (const item of items) {
    try {
      const { data } = item;
      
      // Check for conflicts
      const existing = await prisma.appointment.findUnique({
        where: { id: data.id }
      });

      if (existing && existing.updatedAt.getTime() > item.timestamp) {
        // Conflict detected
        conflicts.push({
          itemId: item.id,
          serverData: existing,
          clientData: data,
          conflictType: 'version_mismatch'
        });
        continue;
      }

      // Upsert appointment
      await prisma.appointment.upsert({
        where: { id: data.id },
        update: {
          ...data,
          updatedAt: new Date()
        },
        create: {
          ...data,
          createdAt: new Date(),
          updatedAt: new Date()
        }
      });

      synced.push(item.id);

      // Invalidate cache
      apolloCache.delete(`appointment_${data.id}`);
      apolloCache.delete(`appointments_${userId}`);

    } catch (error) {
      errors.push({
        itemId: item.id,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  return { synced, conflicts, errors };
}

async function processCustomerItems(
  items: SyncItem[],
  deviceId: string,
  userId: string
): Promise<{ synced: string[]; conflicts: any[]; errors: any[] }> {
  const synced: string[] = [];
  const conflicts: any[] = [];
  const errors: any[] = [];

  for (const item of items) {
    try {
      const { data } = item;
      
      // Check for conflicts
      const existing = await prisma.customer.findUnique({
        where: { id: data.id }
      });

      if (existing && existing.updatedAt.getTime() > item.timestamp) {
        conflicts.push({
          itemId: item.id,
          serverData: existing,
          clientData: data,
          conflictType: 'version_mismatch'
        });
        continue;
      }

      // Upsert customer
      await prisma.customer.upsert({
        where: { id: data.id },
        update: {
          ...data,
          updatedAt: new Date()
        },
        create: {
          ...data,
          createdAt: new Date(),
          updatedAt: new Date()
        }
      });

      synced.push(item.id);

      // Invalidate cache
      apolloCache.delete(`customer_${data.id}`);
      apolloCache.delete(`customers_${userId}`);

    } catch (error) {
      errors.push({
        itemId: item.id,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  return { synced, conflicts, errors };
}

async function processArtistItems(
  items: SyncItem[],
  deviceId: string,
  userId: string
): Promise<{ synced: string[]; conflicts: any[]; errors: any[] }> {
  const synced: string[] = [];
  const conflicts: any[] = [];
  const errors: any[] = [];

  for (const item of items) {
    try {
      const { data } = item;
      
      // Check for conflicts
      const existing = await prisma.artist.findUnique({
        where: { id: data.id }
      });

      if (existing && existing.updatedAt.getTime() > item.timestamp) {
        conflicts.push({
          itemId: item.id,
          serverData: existing,
          clientData: data,
          conflictType: 'version_mismatch'
        });
        continue;
      }

      // Upsert artist
      await prisma.artist.upsert({
        where: { id: data.id },
        update: {
          ...data,
          updatedAt: new Date()
        },
        create: {
          ...data,
          createdAt: new Date(),
          updatedAt: new Date()
        }
      });

      synced.push(item.id);

      // Invalidate cache
      apolloCache.delete(`artist_${data.id}`);
      apolloCache.delete('artists_all');

    } catch (error) {
      errors.push({
        itemId: item.id,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  return { synced, conflicts, errors };
}

async function processMessageItems(
  items: SyncItem[],
  deviceId: string,
  userId: string
): Promise<{ synced: string[]; conflicts: any[]; errors: any[] }> {
  const synced: string[] = [];
  const conflicts: any[] = [];
  const errors: any[] = [];

  // Messages are typically append-only, so no conflict resolution needed
  for (const item of items) {
    try {
      const { data } = item;
      
      // Store message in cache (messages are typically not persisted to DB)
      const cacheKey = `message_${data.id}`;
      apolloCache.set(cacheKey, data, 24 * 60 * 60 * 1000); // 24 hours

      synced.push(item.id);

    } catch (error) {
      errors.push({
        itemId: item.id,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  return { synced, conflicts, errors };
}

async function processAnalyticsItems(
  items: SyncItem[],
  deviceId: string,
  userId: string
): Promise<{ synced: string[]; conflicts: any[]; errors: any[] }> {
  const synced: string[] = [];
  const conflicts: any[] = [];
  const errors: any[] = [];

  for (const item of items) {
    try {
      const { data } = item;
      
      // Analytics are typically aggregated, so merge data
      const cacheKey = `analytics_${data.type}_${userId}`;
      const existing = apolloCache.get(cacheKey) || {};
      
      const merged = {
        ...existing,
        ...data,
        lastUpdated: Date.now()
      };

      apolloCache.set(cacheKey, merged, 60 * 60 * 1000); // 1 hour

      synced.push(item.id);

    } catch (error) {
      errors.push({
        itemId: item.id,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  return { synced, conflicts, errors };
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    const type = searchParams.get('type');

    if (!userId) {
      return NextResponse.json(
        { error: 'Missing userId parameter' },
        { status: 400 }
      );
    }

    // Get sync status for user
    const syncStatus = {
      lastSync: Date.now(),
      pendingItems: 0,
      conflicts: 0,
      errors: 0
    };

    return NextResponse.json(syncStatus, { status: 200 });

  } catch (error) {
    console.error('Sync status API error:', error);
    return NextResponse.json(
      { error: 'Failed to get sync status' },
      { status: 500 }
    );
  }
}
