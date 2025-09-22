// TypeScript interfaces for NextEleven Tattoo Pro

export interface Message {
  id: number;
  type: 'user' | 'ai';
  content: string;
  timestamp?: Date;
}

export interface Feature {
  icon: string;
  title: string;
  description: string;
  demo: string;
  isImplemented?: boolean;
}

export interface Appointment {
  id: string;
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  artistId: string;
  serviceType: string;
  date: Date;
  duration: number;
  price: number;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
}

export interface Artist {
  id: string;
  name: string;
  specialty: string[];
  bio: string;
  portfolio: string[];
  availability: {
    [key: string]: string[]; // day of week -> time slots
  };
  hourlyRate: number;
}

export interface Service {
  id: string;
  name: string;
  description: string;
  basePrice: number;
  estimatedDuration: number;
  category: 'tattoo' | 'piercing' | 'consultation' | 'touch-up';
}

export interface Customer {
  id: string;
  name: string;
  email: string;
  phone: string;
  dateOfBirth?: Date;
  emergencyContact?: string;
  medicalConditions?: string[];
  allergies?: string[];
  previousTattoos?: string[];
  preferences?: {
    style: string[];
    colors: string[];
    placement: string[];
  };
}

export interface Payment {
  id: string;
  appointmentId: string;
  amount: number;
  method: 'card' | 'cash' | 'crypto' | 'digital_wallet';
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  transactionId?: string;
  processedAt?: Date;
}

export interface Aftercare {
  id: string;
  appointmentId: string;
  instructions: string[];
  checkInDates: Date[];
  photos?: string[];
  notes?: string;
  completed: boolean;
}

export interface Analytics {
  totalAppointments: number;
  totalRevenue: number;
  averageAppointmentValue: number;
  customerRetentionRate: number;
  popularServices: Service[];
  monthlyStats: {
    month: string;
    appointments: number;
    revenue: number;
  }[];
}

export type TabType = 'chat' | 'features' | 'about' | 'appointments' | 'artists' | 'analytics' | 'pipelines' | 'information' | 'integrations' | 'interfaces' | 'services' | 'gallery' | 'contact' | 'pricing';

export interface AppState {
  activeTab: TabType;
  messages: Message[];
  appointments: Appointment[];
  artists: Artist[];
  customers: Customer[];
  isLoading: boolean;
  error: string | null;
}