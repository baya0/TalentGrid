// src/pages/Analytics/Analytics.jsx
import React from 'react';
import Card from '@/components/common/Card';

const Analytics = () => {
  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-text-primary mb-6">Analytics</h1>
        
        <Card>
          <div className="text-center py-12">
            <p className="text-text-secondary">Analytics dashboard coming soon...</p>
            <p className="text-sm text-text-muted mt-2">
              This is where AI-powered insights and source performance metrics will appear.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Analytics;