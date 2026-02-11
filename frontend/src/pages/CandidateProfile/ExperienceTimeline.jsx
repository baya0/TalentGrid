// src/pages/CandidateProfile/ExperienceTimeline.jsx
import React from 'react';

const ExperienceTimeline = ({ experience }) => {
  return (
    <div className="relative">
      {/* Timeline Line */}
      <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />
      
      {/* Experience Items */}
      <div className="space-y-6">
        {experience.map((exp, index) => (
          <div key={index} className="relative pl-16">
            {/* Timeline Dot */}
            <div className="absolute left-3 top-2 w-6 h-6">
              {exp.logo ? (
                <img src={exp.logo} alt={exp.company} className="w-full h-full rounded object-cover border-2 border-white shadow" />
              ) : (
                <div className="w-full h-full rounded bg-gradient-to-br from-primary to-secondary flex items-center justify-center border-2 border-white shadow">
                  <span className="text-white text-xs font-bold">
                    {exp.company.substring(0, 1)}
                  </span>
                </div>
              )}
            </div>
            
            {/* Content */}
            <div>
              <h3 className="text-lg font-bold text-text-primary mb-1">
                {exp.title}
              </h3>
              <p className="text-sm text-secondary font-medium mb-2">
                {exp.company}, {exp.period}
              </p>
              <p className="text-text-secondary text-sm leading-relaxed">
                {exp.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExperienceTimeline;