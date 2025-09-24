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
  dateOfBirth: string;
  ageVerified: boolean;
  artistId: string;
  serviceType: string;
  date: string;
  time: string;
  duration: number;
  description: string;
  priceEstimate: number;
  depositAmount: number;
  depositPaid: boolean;
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
    dateOfBirth: '',
    ageVerified: false,
    artistId: '',
    serviceType: 'Custom Tattoo',
    date: '',
    time: '',
    duration: 120,
    description: '',
    priceEstimate: 0,
    depositAmount: 0,
    depositPaid: false
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

  const calculateDeposit = (totalPrice: number) => {
    // APOLLO-approved deposit calculation: 30% of total price, minimum $50
    const depositPercentage = 0.30;
    const minimumDeposit = 50;
    const calculatedDeposit = Math.max(totalPrice * depositPercentage, minimumDeposit);
    return Math.round(calculatedDeposit * 100) / 100; // Round to 2 decimal places
  };

  const calculateAge = (dateOfBirth: string): number => {
    if (!dateOfBirth) return 0;
    const birthDate = new Date(dateOfBirth);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  };

  const isAgeValid = (dateOfBirth: string): boolean => {
    const age = calculateAge(dateOfBirth);
    return age >= 18; // Minimum age requirement
  };

  const handleArtistSelect = (artistId: string) => {
    const artist = artists.find(a => a.id === artistId);
    setSelectedArtist(artist || null);
    setFormData(prev => ({ ...prev, artistId }));
    
    if (artist) {
      // Calculate price estimate based on hourly rate
      const estimatedPrice = (artist.hourlyRate * formData.duration) / 60;
      const depositAmount = calculateDeposit(estimatedPrice);
      setFormData(prev => ({ 
        ...prev, 
        priceEstimate: estimatedPrice,
        depositAmount: depositAmount,
        depositPaid: false
      }));
    }
  };

  const handleDurationChange = (duration: number) => {
    setFormData(prev => ({ ...prev, duration }));
    
    if (selectedArtist) {
      const estimatedPrice = (selectedArtist.hourlyRate * duration) / 60;
      const depositAmount = calculateDeposit(estimatedPrice);
      setFormData(prev => ({ 
        ...prev, 
        priceEstimate: estimatedPrice,
        depositAmount: depositAmount,
        depositPaid: false
      }));
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
    
    if (!formData.customerName || !formData.customerEmail || !formData.artistId || !formData.date || !formData.time || !formData.depositPaid || !formData.ageVerified) {
      alert('Please fill in all required fields, verify your age, and pay the deposit');
      return;
    }

    // Additional age validation
    if (!formData.dateOfBirth || !isAgeValid(formData.dateOfBirth)) {
      alert('You must be 18 years or older to book a tattoo appointment');
      return;
    }

    try {
      setLoading(true);
      
      // Create appointment
      const appointmentData = {
        customerId: 'temp-customer-id', // In real app, this would come from auth
        customerName: formData.customerName,
        customerEmail: formData.customerEmail,
        customerPhone: formData.customerPhone,
        dateOfBirth: formData.dateOfBirth,
        ageVerified: formData.ageVerified,
        customerAge: calculateAge(formData.dateOfBirth),
        artistId: formData.artistId,
        serviceType: formData.serviceType,
        date: new Date(`${formData.date}T${formData.time}`).toISOString(),
        duration: formData.duration,
        price: formData.priceEstimate,
        depositAmount: formData.depositAmount,
        depositPaid: formData.depositPaid,
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
          dateOfBirth: '',
          ageVerified: false,
          artistId: '',
          serviceType: 'Custom Tattoo',
          date: '',
          time: '',
          duration: 120,
          description: '',
          priceEstimate: 0,
          depositAmount: 0,
          depositPaid: false
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

        <div className="form-section age-verification">
          <h3>🔒 Age Verification (Required)</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="dateOfBirth">
                <User className="form-icon" />
                Date of Birth *
              </label>
              <input
                type="date"
                id="dateOfBirth"
                value={formData.dateOfBirth}
                onChange={(e) => setFormData(prev => ({ ...prev, dateOfBirth: e.target.value, ageVerified: false }))}
                required
                max={new Date().toISOString().split('T')[0]}
              />
              {formData.dateOfBirth && (
                <div className="age-display">
                  <p className={`age-text ${isAgeValid(formData.dateOfBirth) ? 'age-valid' : 'age-invalid'}`}>
                    Age: {calculateAge(formData.dateOfBirth)} years
                    {isAgeValid(formData.dateOfBirth) ? ' ✅' : ' ❌'}
                  </p>
                </div>
              )}
            </div>
          </div>
          
          {formData.dateOfBirth && isAgeValid(formData.dateOfBirth) && (
            <div className="age-confirmation">
              <div className="form-group">
                <label htmlFor="ageVerified">
                  <input
                    type="checkbox"
                    id="ageVerified"
                    checked={formData.ageVerified}
                    onChange={(e) => setFormData(prev => ({ ...prev, ageVerified: e.target.checked }))}
                    required
                  />
                  <span>I confirm that I am 18 years of age or older and understand that tattoo services are only available to adults.</span>
                </label>
                <small className="legal-note">
                  * By checking this box, you verify that you meet the legal age requirement for tattoo services in your jurisdiction. 
                  You may be required to show valid government-issued photo ID upon arrival for your appointment.
                </small>
              </div>
            </div>
          )}
          
          {formData.dateOfBirth && !isAgeValid(formData.dateOfBirth) && (
            <div className="age-error">
              <p className="error-message">
                ❌ You must be 18 years or older to book a tattoo appointment. 
                Please contact us if you have questions about our age requirements.
              </p>
            </div>
          )}
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

        <div className="deposit-section">
          <h3>💰 Required Deposit</h3>
          <div className="deposit-info">
            <div className="deposit-amount">
              {formData.depositAmount > 0 ? (
                <>
                  <h4>Deposit Required: ${formData.depositAmount.toFixed(2)}</h4>
                  <p>30% of total price (minimum $50) - This secures your appointment</p>
                </>
              ) : (
                <>
                  <h4>Deposit Required: TBD</h4>
                  <p>Deposit will be calculated after selecting an artist and duration</p>
                  <p className="deposit-info-text">
                    <strong>Deposit Policy:</strong> 30% of total price (minimum $50)
                  </p>
                </>
              )}
            </div>
            
            {formData.depositAmount > 0 && (
              <div className="form-group">
                <label htmlFor="depositPaid">
                  <input
                    type="checkbox"
                    id="depositPaid"
                    checked={formData.depositPaid}
                    onChange={(e) => setFormData(prev => ({ ...prev, depositPaid: e.target.checked }))}
                    required
                  />
                  <span>I confirm that I have paid the required deposit of ${formData.depositAmount.toFixed(2)}</span>
                </label>
                <small className="deposit-note">
                  * Deposit payment is required to secure your appointment. 
                  Payment can be made via cash, card, or online payment methods.
                </small>
              </div>
            )}
            
            {formData.depositAmount === 0 && (
              <div className="deposit-placeholder">
                <p className="deposit-instructions">
                  🔒 <strong>Important:</strong> A deposit is required to secure your appointment. 
                  The deposit amount will be calculated once you select an artist and duration above.
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            disabled={loading || !formData.customerName || !formData.customerEmail || !formData.artistId || !formData.date || !formData.time || !formData.depositPaid || !formData.ageVerified}
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