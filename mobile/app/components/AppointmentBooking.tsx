'use client'

import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { Calendar, Clock, User, DollarSign, MapPin, Phone, Mail } from 'lucide-react';

interface Artist {
  id: string;
  name: string;
  specialty: string;
  hourlyRate: number;
  bio: string;
  availability: any[];
}

interface AppointmentFormData {
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  artistId: string;
  serviceType: string;
  date: string;
  time: string;
  duration: number;
  description: string;
  priceEstimate: number;
}

const AppointmentBooking: React.FC = () => {
  const { state, dispatch } = useApp();
  const [artists, setArtists] = useState<Artist[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedArtist, setSelectedArtist] = useState<Artist | null>(null);
  const [availableSlots, setAvailableSlots] = useState<string[]>([]);
  const [formData, setFormData] = useState<AppointmentFormData>({
    customerName: '',
    customerEmail: '',
    customerPhone: '',
    artistId: '',
    serviceType: 'Custom Tattoo',
    date: '',
    time: '',
    duration: 120,
    description: '',
    priceEstimate: 0
  });

  const serviceTypes = [
    'Custom Tattoo',
    'Cover-up Tattoo',
    'Touch-up',
    'Consultation',
    'Piercing',
    'Other'
  ];

  const durationOptions = [
    { value: 60, label: '1 hour' },
    { value: 120, label: '2 hours' },
    { value: 180, label: '3 hours' },
    { value: 240, label: '4 hours' },
    { value: 300, label: '5+ hours' }
  ];

  useEffect(() => {
    fetchArtists();
  }, []);

  const fetchArtists = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/artists');
      const data = await response.json();
      if (data.success) {
        setArtists(data.artists);
      }
    } catch (error) {
      console.error('Error fetching artists:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleArtistSelect = (artistId: string) => {
    const artist = artists.find(a => a.id === artistId);
    setSelectedArtist(artist || null);
    setFormData(prev => ({ ...prev, artistId }));
    
    if (artist) {
      // Calculate price estimate based on hourly rate
      const estimatedPrice = (artist.hourlyRate * formData.duration) / 60;
      setFormData(prev => ({ ...prev, priceEstimate: estimatedPrice }));
    }
  };

  const handleDurationChange = (duration: number) => {
    setFormData(prev => ({ ...prev, duration }));
    
    if (selectedArtist) {
      const estimatedPrice = (selectedArtist.hourlyRate * duration) / 60;
      setFormData(prev => ({ ...prev, priceEstimate: estimatedPrice }));
    }
  };

  const generateTimeSlots = (date: string) => {
    if (!selectedArtist) return [];
    
    const slots = [];
    const startHour = 10; // 10 AM
    const endHour = 18; // 6 PM
    
    for (let hour = startHour; hour < endHour; hour++) {
      for (let minute = 0; minute < 60; minute += 30) {
        const timeString = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        slots.push(timeString);
      }
    }
    
    return slots;
  };

  const handleDateChange = (date: string) => {
    setFormData(prev => ({ ...prev, date }));
    const slots = generateTimeSlots(date);
    setAvailableSlots(slots);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.customerName || !formData.customerEmail || !formData.artistId || !formData.date || !formData.time) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      
      // Create appointment
      const appointmentData = {
        customerId: 'temp-customer-id', // In real app, this would come from auth
        artistId: formData.artistId,
        serviceType: formData.serviceType,
        date: new Date(`${formData.date}T${formData.time}`).toISOString(),
        duration: formData.duration,
        price: formData.priceEstimate,
        notes: formData.description
      };

      const response = await fetch('/api/appointments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        },
        body: JSON.stringify(appointmentData)
      });

      const result = await response.json();
      
      if (result.success) {
        dispatch({ type: 'ADD_APPOINTMENT', payload: result.appointment });
        alert('Appointment booked successfully!');
        
        // Reset form
        setFormData({
          customerName: '',
          customerEmail: '',
          customerPhone: '',
          artistId: '',
          serviceType: 'Custom Tattoo',
          date: '',
          time: '',
          duration: 120,
          description: '',
          priceEstimate: 0
        });
        setSelectedArtist(null);
        setAvailableSlots([]);
      } else {
        alert('Error booking appointment: ' + result.error);
      }
    } catch (error) {
      console.error('Error booking appointment:', error);
      alert('Error booking appointment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="appointment-booking">
      <div className="booking-header">
        <h2>Book Your Appointment</h2>
        <p>Schedule your tattoo session with our professional artists</p>
      </div>

      <form onSubmit={handleSubmit} className="booking-form">
        <div className="form-section">
          <h3>Customer Information</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="customerName">
                <User className="form-icon" />
                Full Name *
              </label>
              <input
                type="text"
                id="customerName"
                value={formData.customerName}
                onChange={(e) => setFormData(prev => ({ ...prev, customerName: e.target.value }))}
                required
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="customerEmail">
                <Mail className="form-icon" />
                Email *
              </label>
              <input
                type="email"
                id="customerEmail"
                value={formData.customerEmail}
                onChange={(e) => setFormData(prev => ({ ...prev, customerEmail: e.target.value }))}
                required
                placeholder="Enter your email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="customerPhone">
                <Phone className="form-icon" />
                Phone Number
              </label>
              <input
                type="tel"
                id="customerPhone"
                value={formData.customerPhone}
                onChange={(e) => setFormData(prev => ({ ...prev, customerPhone: e.target.value }))}
                placeholder="Enter your phone number"
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Appointment Details</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="artistId">
                <User className="form-icon" />
                Select Artist *
              </label>
              <select
                id="artistId"
                value={formData.artistId}
                onChange={(e) => handleArtistSelect(e.target.value)}
                required
              >
                <option value="">Choose an artist</option>
                {artists.map(artist => (
                  <option key={artist.id} value={artist.id}>
                    {artist.name} - {JSON.parse(artist.specialty || '[]').join(', ')}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="serviceType">
                <DollarSign className="form-icon" />
                Service Type
              </label>
              <select
                id="serviceType"
                value={formData.serviceType}
                onChange={(e) => setFormData(prev => ({ ...prev, serviceType: e.target.value }))}
              >
                {serviceTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="duration">
                <Clock className="form-icon" />
                Duration
              </label>
              <select
                id="duration"
                value={formData.duration}
                onChange={(e) => handleDurationChange(Number(e.target.value))}
              >
                {durationOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Schedule</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="date">
                <Calendar className="form-icon" />
                Date *
              </label>
              <input
                type="date"
                id="date"
                value={formData.date}
                onChange={(e) => handleDateChange(e.target.value)}
                required
                min={new Date().toISOString().split('T')[0]}
              />
            </div>

            <div className="form-group">
              <label htmlFor="time">
                <Clock className="form-icon" />
                Time *
              </label>
              <select
                id="time"
                value={formData.time}
                onChange={(e) => setFormData(prev => ({ ...prev, time: e.target.value }))}
                required
                disabled={!formData.date}
              >
                <option value="">Select time</option>
                {availableSlots.map(slot => (
                  <option key={slot} value={slot}>{slot}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {selectedArtist && (
          <div className="artist-info">
            <h4>Selected Artist: {selectedArtist.name}</h4>
            <p><strong>Specialty:</strong> {JSON.parse(selectedArtist.specialty || '[]').join(', ')}</p>
            <p><strong>Hourly Rate:</strong> ${selectedArtist.hourlyRate}</p>
            <p><strong>Bio:</strong> {selectedArtist.bio}</p>
          </div>
        )}

        <div className="form-section">
          <h3>Additional Information</h3>
          <div className="form-group">
            <label htmlFor="description">Tattoo Description</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe your tattoo idea, placement, size, and any specific requirements..."
              rows={4}
            />
          </div>
        </div>

        {formData.priceEstimate > 0 && (
          <div className="price-estimate">
            <h4>Price Estimate</h4>
            <p className="price">${formData.priceEstimate.toFixed(2)}</p>
            <small>Based on {selectedArtist?.name}'s hourly rate and selected duration</small>
          </div>
        )}

        <div className="form-actions">
          <button
            type="submit"
            disabled={loading || !formData.customerName || !formData.customerEmail || !formData.artistId || !formData.date || !formData.time}
            className="book-button"
          >
            {loading ? 'Booking...' : 'Book Appointment'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AppointmentBooking;