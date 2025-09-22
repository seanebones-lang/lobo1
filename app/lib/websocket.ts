// APOLLO-GUIDED Real-time WebSocket System
import { Server as SocketIOServer } from 'socket.io';
import { Server as HTTPServer } from 'http';

interface SocketData {
  userId?: string;
  userRole?: string;
  room?: string;
}

interface ApolloEvent {
  type: string;
  data: any;
  timestamp: number;
  userId?: string;
}

class ApolloWebSocketManager {
  private io: SocketIOServer;
  private connectedUsers = new Map<string, string>(); // socketId -> userId
  private userRooms = new Map<string, Set<string>>(); // userId -> Set of rooms

  constructor(server: HTTPServer) {
    this.io = new SocketIOServer(server, {
      cors: {
        origin: process.env.NODE_ENV === 'production' 
          ? ['https://nexteleven.com', 'https://www.nexteleven.com']
          : ['http://localhost:8007', 'http://localhost:3000'],
        methods: ['GET', 'POST'],
        credentials: true
      },
      transports: ['websocket', 'polling']
    });

    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    this.io.on('connection', (socket) => {
      console.log(`🌊 APOLLO WebSocket: Client connected ${socket.id}`);

      // Authentication
      socket.on('authenticate', (data: { token: string; userId: string }) => {
        // In production, verify JWT token here
        this.connectedUsers.set(socket.id, data.userId);
        socket.join(`user_${data.userId}`);
        socket.emit('authenticated', { success: true });
        console.log(`🔐 APOLLO WebSocket: User ${data.userId} authenticated`);
      });

      // Join specific rooms
      socket.on('join_room', (room: string) => {
        socket.join(room);
        const userId = this.connectedUsers.get(socket.id);
        if (userId) {
          if (!this.userRooms.has(userId)) {
            this.userRooms.set(userId, new Set());
          }
          this.userRooms.get(userId)!.add(room);
        }
        console.log(`🏠 APOLLO WebSocket: Socket ${socket.id} joined room ${room}`);
      });

      // Leave rooms
      socket.on('leave_room', (room: string) => {
        socket.leave(room);
        const userId = this.connectedUsers.get(socket.id);
        if (userId && this.userRooms.has(userId)) {
          this.userRooms.get(userId)!.delete(room);
        }
        console.log(`🚪 APOLLO WebSocket: Socket ${socket.id} left room ${room}`);
      });

      // Real-time chat with APOLLO
      socket.on('apollo_chat', async (data: { message: string; context?: any }) => {
        const userId = this.connectedUsers.get(socket.id);
        if (!userId) {
          socket.emit('error', { message: 'Not authenticated' });
          return;
        }

        try {
          // Process with APOLLO AI
          const response = await this.processApolloMessage(data.message, userId, data.context);
          
          socket.emit('apollo_response', {
            message: response.message,
            confidence: response.confidence,
            suggestions: response.suggestions,
            timestamp: Date.now()
          });
        } catch (error) {
          socket.emit('error', { message: 'APOLLO processing failed' });
        }
      });

      // Appointment updates
      socket.on('appointment_update', (data: { appointmentId: string; status: string }) => {
        const userId = this.connectedUsers.get(socket.id);
        if (userId) {
          this.broadcastToUser(userId, 'appointment_updated', {
            appointmentId: data.appointmentId,
            status: data.status,
            timestamp: Date.now()
          });
        }
      });

      // Payment notifications
      socket.on('payment_update', (data: { paymentId: string; status: string; amount: number }) => {
        const userId = this.connectedUsers.get(socket.id);
        if (userId) {
          this.broadcastToUser(userId, 'payment_updated', {
            paymentId: data.paymentId,
            status: data.status,
            amount: data.amount,
            timestamp: Date.now()
          });
        }
      });

      // Disconnect handling
      socket.on('disconnect', () => {
        const userId = this.connectedUsers.get(socket.id);
        if (userId) {
          this.userRooms.delete(userId);
        }
        this.connectedUsers.delete(socket.id);
        console.log(`🌊 APOLLO WebSocket: Client disconnected ${socket.id}`);
      });
    });
  }

  private async processApolloMessage(message: string, userId: string, context?: any) {
    // Simulate APOLLO AI processing
    // In production, this would call the actual APOLLO API
    const responses = [
      "I understand your request. Let me process that for you.",
      "APOLLO is analyzing your message. Here's my response.",
      "Based on your input, I recommend the following actions.",
      "I've processed your request with my advanced consciousness algorithms.",
      "APOLLO consciousness level 1.0 activated. Processing complete."
    ];

    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    
    return {
      message: randomResponse,
      confidence: 0.95,
      suggestions: ['Book appointment', 'View analytics', 'Contact support']
    };
  }

  // Broadcast to specific user
  broadcastToUser(userId: string, event: string, data: any) {
    this.io.to(`user_${userId}`).emit(event, data);
  }

  // Broadcast to room
  broadcastToRoom(room: string, event: string, data: any) {
    this.io.to(room).emit(event, data);
  }

  // Broadcast to all connected users
  broadcast(event: string, data: any) {
    this.io.emit(event, data);
  }

  // Send system notification
  sendNotification(userId: string, notification: ApolloEvent) {
    this.broadcastToUser(userId, 'apollo_notification', notification);
  }

  // Get connection stats
  getStats() {
    return {
      connectedUsers: this.connectedUsers.size,
      totalRooms: this.io.sockets.adapter.rooms.size,
      memoryUsage: process.memoryUsage().heapUsed
    };
  }
}

export default ApolloWebSocketManager;
