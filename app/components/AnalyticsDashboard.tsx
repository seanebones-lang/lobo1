'use client'

import React, { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';
import { 
  TrendingUp, 
  Users, 
  Calendar, 
  DollarSign, 
  Clock, 
  Star,
  Download,
  Filter
} from 'lucide-react';

interface AnalyticsData {
  appointments: any[];
  revenue: number;
  totalCustomers: number;
  averageSessionTime: number;
  topArtists: any[];
  monthlyRevenue: any[];
  appointmentStatus: any[];
  serviceTypes: any[];
}

const AnalyticsDashboard: React.FC = () => {
  const { state } = useApp();
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({
    appointments: [],
    revenue: 0,
    totalCustomers: 0,
    averageSessionTime: 0,
    topArtists: [],
    monthlyRevenue: [],
    appointmentStatus: [],
    serviceTypes: []
  });
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30');
  const [selectedMetric, setSelectedMetric] = useState('revenue');

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00'];

  useEffect(() => {
    fetchAnalyticsData();
  }, [dateRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Simulate API call - in real app, this would fetch from /api/analytics
      const mockData: AnalyticsData = {
        appointments: [
          { id: '1', date: '2024-01-15', artist: 'John Doe', customer: 'Jane Smith', amount: 300, status: 'COMPLETED' },
          { id: '2', date: '2024-01-16', artist: 'Jane Wilson', customer: 'Bob Johnson', amount: 450, status: 'COMPLETED' },
          { id: '3', date: '2024-01-17', artist: 'Mike Brown', customer: 'Alice Davis', amount: 200, status: 'PENDING' },
          { id: '4', date: '2024-01-18', artist: 'John Doe', customer: 'Charlie Wilson', amount: 600, status: 'COMPLETED' },
          { id: '5', date: '2024-01-19', artist: 'Jane Wilson', customer: 'Diana Prince', amount: 350, status: 'CONFIRMED' }
        ],
        revenue: 1900,
        totalCustomers: 5,
        averageSessionTime: 2.5,
        topArtists: [
          { name: 'John Doe', appointments: 2, revenue: 900, rating: 4.8 },
          { name: 'Jane Wilson', appointments: 2, revenue: 800, rating: 4.9 },
          { name: 'Mike Brown', appointments: 1, revenue: 200, rating: 4.7 }
        ],
        monthlyRevenue: [
          { month: 'Jan', revenue: 1900, appointments: 5 },
          { month: 'Feb', revenue: 2200, appointments: 6 },
          { month: 'Mar', revenue: 1800, appointments: 4 },
          { month: 'Apr', revenue: 2500, appointments: 7 },
          { month: 'May', revenue: 2100, appointments: 5 },
          { month: 'Jun', revenue: 2800, appointments: 8 }
        ],
        appointmentStatus: [
          { status: 'COMPLETED', count: 3, percentage: 60 },
          { status: 'PENDING', count: 1, percentage: 20 },
          { status: 'CONFIRMED', count: 1, percentage: 20 }
        ],
        serviceTypes: [
          { type: 'Custom Tattoo', count: 3, revenue: 1200 },
          { type: 'Cover-up', count: 1, revenue: 400 },
          { type: 'Touch-up', count: 1, revenue: 300 }
        ]
      };

      setAnalyticsData(mockData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportData = () => {
    const dataStr = JSON.stringify(analyticsData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analytics-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  };

  if (loading) {
    return (
      <div className="analytics-dashboard">
        <div className="loading">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <h2>Analytics Dashboard</h2>
        <div className="dashboard-controls">
          <select 
            value={dateRange} 
            onChange={(e) => setDateRange(e.target.value)}
            className="date-range-select"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
          <button onClick={exportData} className="export-button">
            <Download className="icon" />
            Export Data
          </button>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <DollarSign />
          </div>
          <div className="metric-content">
            <h3>Total Revenue</h3>
            <p className="metric-value">${analyticsData.revenue.toLocaleString()}</p>
            <span className="metric-change positive">+12% from last month</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Calendar />
          </div>
          <div className="metric-content">
            <h3>Appointments</h3>
            <p className="metric-value">{analyticsData.appointments.length}</p>
            <span className="metric-change positive">+8% from last month</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Users />
          </div>
          <div className="metric-content">
            <h3>Customers</h3>
            <p className="metric-value">{analyticsData.totalCustomers}</p>
            <span className="metric-change positive">+15% from last month</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Clock />
          </div>
          <div className="metric-content">
            <h3>Avg Session Time</h3>
            <p className="metric-value">{analyticsData.averageSessionTime}h</p>
            <span className="metric-change neutral">Same as last month</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Monthly Revenue Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={analyticsData.monthlyRevenue}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${value}`, 'Revenue']} />
              <Area 
                type="monotone" 
                dataKey="revenue" 
                stroke="#8884d8" 
                fill="#8884d8" 
                fillOpacity={0.6}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Appointment Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analyticsData.appointmentStatus}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ status, percentage }) => `${status}: ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {analyticsData.appointmentStatus.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Top Artists by Revenue</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analyticsData.topArtists}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${value}`, 'Revenue']} />
              <Bar dataKey="revenue" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Service Types</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analyticsData.serviceTypes}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${value}`, 'Revenue']} />
              <Bar dataKey="revenue" fill="#ffc658" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="recent-appointments">
        <h3>Recent Appointments</h3>
        <div className="appointments-table">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Artist</th>
                <th>Customer</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {analyticsData.appointments.map(appointment => (
                <tr key={appointment.id}>
                  <td>{new Date(appointment.date).toLocaleDateString()}</td>
                  <td>{appointment.artist}</td>
                  <td>{appointment.customer}</td>
                  <td>${appointment.amount}</td>
                  <td>
                    <span className={`status ${appointment.status.toLowerCase()}`}>
                      {appointment.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="insights">
        <h3>Key Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <TrendingUp className="insight-icon" />
            <h4>Revenue Growth</h4>
            <p>Revenue has increased by 12% compared to last month, driven by higher appointment volume.</p>
          </div>
          <div className="insight-card">
            <Star className="insight-icon" />
            <h4>Top Performer</h4>
            <p>Jane Wilson is your top-performing artist with the highest revenue and customer ratings.</p>
          </div>
          <div className="insight-card">
            <Calendar className="insight-icon" />
            <h4>Peak Hours</h4>
            <p>Most appointments are scheduled between 2-4 PM on weekdays and 10 AM-2 PM on weekends.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;