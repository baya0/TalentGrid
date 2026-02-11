// src/pages/Dashboard/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { Users, TrendingUp, Briefcase, Upload, Search, BarChart3, ArrowUpRight, Clock, Info } from 'lucide-react';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { getDashboardStats } from '@/services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);

  // Icon mapping for stats
  const iconMap = {
    'Total Candidates': Users,
    'New This Week': Upload,
    'Avg Match Score': TrendingUp,
    'Database Status': BarChart3,
  };

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const data = await getDashboardStats();
        setDashboardData(data);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data');
        // Use fallback data if API fails
        setDashboardData({
          stats: [
            { label: 'Total Candidates', value: '0', change: '+0', changeType: 'neutral', description: 'Import CVs to get started' },
            { label: 'New This Week', value: '0', change: '+0%', changeType: 'neutral', description: 'vs last week' },
            { label: 'Avg Match Score', value: 'N/A', change: '+0%', changeType: 'neutral', description: 'across all candidates' },
            { label: 'Database Status', value: 'Active', change: 'Online', changeType: 'positive', description: 'all systems operational' },
          ],
          recentActivity: [
            { action: 'No recent activity. Import some CVs to get started!', time: 'Just now', type: 'info' }
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Prepare stats with icons
  const stats = dashboardData?.stats?.map(stat => ({
    ...stat,
    icon: iconMap[stat.label] || Users
  })) || [];

  const recentActivity = dashboardData?.recentActivity || [];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary">
            Welcome back, {user?.full_name?.split(' ')[0] || 'there'}!
          </h1>
          <p className="text-text-secondary mt-1">
            Here's what's happening with your talent pipeline today.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="relative overflow-hidden group hover:shadow-card-hover transition-all duration-300">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-text-secondary text-sm font-medium mb-1">{stat.label}</p>
                  <p className="text-3xl font-bold text-text-primary mb-1">{stat.value}</p>
                  <div className="flex items-center gap-1">
                    <span className="text-sm font-medium text-green-600">{stat.change}</span>
                    <span className="text-xs text-text-muted">{stat.description}</span>
                  </div>
                </div>
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                  <stat.icon className="w-6 h-6 text-primary" />
                </div>
              </div>
              {/* Decorative accent */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-primary to-secondary opacity-0 group-hover:opacity-100 transition-opacity" />
            </Card>
          ))}
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <Card>
              <h2 className="text-xl font-bold text-text-primary mb-6">Quick Actions</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <button
                  onClick={() => navigate('/import')}
                  className="group p-6 rounded-xl border-2 border-dashed border-border hover:border-primary hover:bg-primary/5 transition-all duration-200 text-left"
                >
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                    <Upload className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="font-semibold text-text-primary mb-1">Import CVs</h3>
                  <p className="text-sm text-text-muted">Upload and parse candidate resumes</p>
                </button>

                <button
                  onClick={() => navigate('/sourcing')}
                  className="group p-6 rounded-xl border-2 border-dashed border-border hover:border-secondary hover:bg-secondary/5 transition-all duration-200 text-left"
                >
                  <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center mb-4 group-hover:bg-secondary/20 transition-colors">
                    <Search className="w-6 h-6 text-secondary" />
                  </div>
                  <h3 className="font-semibold text-text-primary mb-1">Search Talent</h3>
                  <p className="text-sm text-text-muted">Find candidates with AI matching</p>
                </button>

                <button
                  onClick={() => navigate('/analytics')}
                  className="group p-6 rounded-xl border-2 border-dashed border-border hover:border-accent hover:bg-accent/5 transition-all duration-200 text-left"
                >
                  <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-4 group-hover:bg-accent/20 transition-colors">
                    <BarChart3 className="w-6 h-6 text-accent" />
                  </div>
                  <h3 className="font-semibold text-text-primary mb-1">View Analytics</h3>
                  <p className="text-sm text-text-muted">Insights and performance metrics</p>
                </button>
              </div>
            </Card>
          </div>

          {/* Recent Activity */}
          <div className="lg:col-span-1">
            <Card className="h-full">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-text-primary">Recent Activity</h2>
                <button className="text-sm text-secondary hover:text-secondary-600 font-medium">
                  View all
                </button>
              </div>
              <div className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-3 rounded-lg hover:bg-background transition-colors"
                  >
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      {activity.type === 'import' && <Upload className="w-4 h-4 text-primary" />}
                      {activity.type === 'search' && <Search className="w-4 h-4 text-primary" />}
                      {activity.type === 'view' && <Users className="w-4 h-4 text-primary" />}
                      {activity.type === 'match' && <TrendingUp className="w-4 h-4 text-primary" />}
                      {activity.type === 'info' && <Info className="w-4 h-4 text-primary" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-text-primary leading-snug">
                        {activity.action}
                      </p>
                      <p className="text-xs text-text-muted mt-1 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
