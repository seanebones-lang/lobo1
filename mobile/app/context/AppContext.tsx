'use client'

import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { AppState, TabType, Message, Appointment, Artist, Customer } from '../types';

// Action types
type AppAction =
  | { type: 'SET_ACTIVE_TAB'; payload: TabType }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'ADD_APPOINTMENT'; payload: Appointment }
  | { type: 'UPDATE_APPOINTMENT'; payload: { id: string; updates: Partial<Appointment> } }
  | { type: 'DELETE_APPOINTMENT'; payload: string }
  | { type: 'ADD_ARTIST'; payload: Artist }
  | { type: 'ADD_CUSTOMER'; payload: Customer }
  | { type: 'CLEAR_MESSAGES' };

// Initial state
const initialState: AppState = {
  activeTab: 'chat',
  messages: [
    {
      id: 'msg_welcome_001',
      type: 'ai',
      content: 'The eye knows what you are here, to retain human custom, ask your questions anyway',
      timestamp: new Date()
    }
  ],
  appointments: [],
  artists: [
    {
      id: '1',
      name: 'Alex Crowley',
      specialty: ['Traditional', 'Blackwork', 'Geometric'],
      bio: 'Master of the dark arts and traditional tattooing with 15+ years experience.',
      portfolio: [],
      availability: {
        'monday': ['10:00', '11:00', '14:00', '15:00'],
        'tuesday': ['10:00', '11:00', '14:00', '15:00'],
        'wednesday': ['10:00', '11:00', '14:00', '15:00'],
        'thursday': ['10:00', '11:00', '14:00', '15:00'],
        'friday': ['10:00', '11:00', '14:00', '15:00'],
        'saturday': ['10:00', '11:00', '14:00']
      },
      hourlyRate: 150
    },
    {
      id: '2',
      name: 'Luna Mystic',
      specialty: ['Realistic', 'Portraits', 'Nature'],
      bio: 'Specialist in realistic and portrait work with a mystical touch.',
      portfolio: [],
      availability: {
        'tuesday': ['12:00', '13:00', '16:00', '17:00'],
        'wednesday': ['12:00', '13:00', '16:00', '17:00'],
        'thursday': ['12:00', '13:00', '16:00', '17:00'],
        'friday': ['12:00', '13:00', '16:00', '17:00'],
        'saturday': ['12:00', '13:00', '16:00']
      },
      hourlyRate: 180
    }
  ],
  customers: [],
  isLoading: false,
  error: null
};

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_ACTIVE_TAB':
      return { ...state, activeTab: action.payload };
    
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    
    case 'ADD_APPOINTMENT':
      return { ...state, appointments: [...state.appointments, action.payload] };
    
    case 'UPDATE_APPOINTMENT':
      return {
        ...state,
        appointments: state.appointments.map(apt =>
          apt.id === action.payload.id
            ? { ...apt, ...action.payload.updates }
            : apt
        )
      };
    
    case 'DELETE_APPOINTMENT':
      return {
        ...state,
        appointments: state.appointments.filter(apt => apt.id !== action.payload)
      };
    
    case 'ADD_ARTIST':
      return { ...state, artists: [...state.artists, action.payload] };
    
    case 'ADD_CUSTOMER':
      return { ...state, customers: [...state.customers, action.payload] };
    
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [state.messages[0]] }; // Keep initial AI message
    
    default:
      return state;
  }
}

// Context
const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

// Provider
export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

// Hook
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

// Action creators
export const appActions = {
  setActiveTab: (tab: TabType): AppAction => ({ type: 'SET_ACTIVE_TAB', payload: tab }),
  addMessage: (message: Message): AppAction => ({ type: 'ADD_MESSAGE', payload: message }),
  setLoading: (loading: boolean): AppAction => ({ type: 'SET_LOADING', payload: loading }),
  setError: (error: string | null): AppAction => ({ type: 'SET_ERROR', payload: error }),
  addAppointment: (appointment: Appointment): AppAction => ({ type: 'ADD_APPOINTMENT', payload: appointment }),
  updateAppointment: (id: string, updates: Partial<Appointment>): AppAction => ({ 
    type: 'UPDATE_APPOINTMENT', 
    payload: { id, updates } 
  }),
  deleteAppointment: (id: string): AppAction => ({ type: 'DELETE_APPOINTMENT', payload: id }),
  addArtist: (artist: Artist): AppAction => ({ type: 'ADD_ARTIST', payload: artist }),
  addCustomer: (customer: Customer): AppAction => ({ type: 'ADD_CUSTOMER', payload: customer }),
  clearMessages: (): AppAction => ({ type: 'CLEAR_MESSAGES' })
};