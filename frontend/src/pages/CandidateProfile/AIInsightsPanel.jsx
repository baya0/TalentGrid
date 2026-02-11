// src/pages/CandidateProfile/AIInsightsPanel.jsx
import React from 'react';
import { Brain, Shield } from 'lucide-react';
import Card from '@/components/common/Card';
import ProgressBar from '@/components/common/ProgressBar';

const AIInsightsPanel = ({ insights }) => {
  return (
    <Card className="sticky top-6 border-2 border-primary-200">
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <Brain className="w-6 h-6 text-primary" />
        <h2 className="text-lg font-bold text-primary">INSIGHTS</h2>
      </div>
      
      {/* Cultural Match - Large Circle */}
      <div className="flex flex-col items-center mb-8 p-6 bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl">
        <div className="relative w-40 h-40 mb-4">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="80"
              cy="80"
              r="70"
              stroke="#E5E7EB"
              strokeWidth="12"
              fill="none"
            />
            <circle
              cx="80"
              cy="80"
              r="70"
              stroke="#C4A962"
              strokeWidth="12"
              fill="none"
              strokeDasharray={`${2 * Math.PI * 70}`}
              strokeDashoffset={`${2 * Math.PI * 70 * (1 - insights.culturalMatch / 100)}`}
              className="transition-all duration-1000"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-bold text-primary">{insights.culturalMatch}%</span>
          </div>
        </div>
        <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wide">
          CULTURAL MATCH
        </h3>
      </div>
      
      {/* Technical Depth */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-semibold text-text-primary">TECHNICAL DEPTH</span>
          <span className="text-sm font-bold text-primary">{insights.technicalDepth}%</span>
        </div>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-1000"
            style={{ width: `${insights.technicalDepth}%` }}
          />
        </div>
      </div>
      
      {/* Leadership Potential */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-semibold text-text-primary">LEADERSHIP POTENTIAL</span>
          <span className="text-sm font-bold text-primary">{insights.leadershipPotential}%</span>
        </div>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-1000"
            style={{ width: `${insights.leadershipPotential}%` }}
          />
        </div>
      </div>
      
      {/* Blockchain Verified Badge */}
      {insights.blockchainVerified && (
        <div className="flex flex-col items-center p-6 bg-primary rounded-xl">
          <div className="w-24 h-24 mb-3 relative">
            {/* Blockchain Badge SVG */}
            <div className="w-full h-full bg-secondary rounded-full flex items-center justify-center border-4 border-white shadow-lg">
              <Shield className="w-12 h-12 text-white" />
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-20 h-20 border-4 border-secondary-300 rounded-full animate-ping opacity-75"></div>
            </div>
          </div>
          <span className="text-white font-bold text-sm tracking-wider">
            BLOCKCHAIN
          </span>
          <span className="text-white font-bold text-sm tracking-wider">
            VERIFIED
          </span>
        </div>
      )}
    </Card>
  );
};

export default AIInsightsPanel;