// src/pages/CandidateProfile/CandidateProfile.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, Phone, MapPin, Calendar, Briefcase } from 'lucide-react';
import Button from '@/components/common/Button';
import Badge from '@/components/common/Badge';
import Avatar from '@/components/common/Avatar';
import Card from '@/components/common/Card';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import AIInsightsPanel from './AIInsightsPanel';
import ExperienceTimeline from './ExperienceTimeline';
import { getCandidate } from '@/services/api';

const CandidateProfile = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCandidate = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getCandidate(id);

        // Transform backend data to match component expectations
        const transformedCandidate = {
          id: data.id,
          name: data.name || 'Unknown',
          title: data.title || 'Not specified',
          location: data.location || 'Not specified',
          email: data.email || '',
          phone: data.phone || '',
          avatar: null,
          topTalent: data.quality_score >= 8 || data.match_percentage >= 90,
          summary: data.summary || '',
          yearsExperience: data.years_experience || 0,

          // Transform experience array
          experience: (data.experience || []).map(exp => ({
            title: exp.role || exp.title || 'Role',
            company: exp.organization || exp.company || 'Company',
            logo: null,
            period: `${exp.from || exp.start_date || ''} - ${exp.to || exp.end_date || 'Present'}`,
            description: exp.description || '',
          })),

          // Transform education - handle both array and object
          education: Array.isArray(data.education) && data.education.length > 0
            ? {
                degree: data.education[0].degree || '',
                field: data.education[0].field || '',
                institution: data.education[0].institution || '',
                location: '',
              }
            : {
                degree: data.education?.degree || '',
                field: data.education?.field || '',
                institution: data.education?.institution || '',
                location: '',
              },

          // Skills array
          skills: data.skills || [],

          // AI insights (use real data or defaults)
          aiInsights: {
            culturalMatch: data.match_percentage || 75,
            technicalDepth: data.quality_score ? data.quality_score * 10 : 80,
            leadershipPotential: data.years_experience ? Math.min(data.years_experience * 10, 95) : 70,
            blockchainVerified: false,
          },

          // Additional data
          languages: data.languages || [],
          certifications: data.certifications || [],
          links: data.links || {},
          source: data.source,
          status: data.status,
        };

        setCandidate(transformedCandidate);
      } catch (err) {
        console.error('Failed to fetch candidate:', err);
        setError('Failed to load candidate profile');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchCandidate();
    }
  }, [id]);
  
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading candidate profile..." />
      </div>
    );
  }
  
  if (error || !candidate) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-text-primary mb-2">
            {error || 'Candidate Not Found'}
          </h2>
          <Button onClick={() => navigate('/sourcing')}>
            Back to Search
          </Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-background">
      {/* Header with gradient background */}
      <div className="bg-gradient-to-r from-primary to-primary-600 text-white">
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Back Button */}
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-white hover:text-gray-200 transition-colors mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Results</span>
          </button>
          
          <div className="flex items-start gap-6">
            {/* Profile Photo */}
            <div className="relative">
              <Avatar
                name={candidate.name}
                src={candidate.avatar}
                size="2xl"
                className="border-4 border-white shadow-lg"
              />
            </div>
            
            {/* Basic Info */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold">{candidate.name}</h1>
                {candidate.topTalent && (
                  <Badge variant="secondary" size="lg" className="gap-2">
                    <span className="text-lg">🛡️</span>
                    TOP 1% TALENT
                  </Badge>
                )}
              </div>
              <p className="text-xl text-gray-100 mb-4">{candidate.title}, {candidate.location}</p>
              
              {/* Contact Info */}
              <div className="flex flex-wrap gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  <span>{candidate.email}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Phone className="w-4 h-4" />
                  <span>{candidate.phone}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  <span>{candidate.location}</span>
                </div>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex gap-3">
              <Button variant="secondary" size="lg">
                Contact
              </Button>
              <Button variant="outline" size="lg" className="bg-white text-primary hover:bg-gray-100">
                Save
              </Button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Experience */}
            <Card>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-full bg-secondary-100 flex items-center justify-center">
                  <Briefcase className="w-5 h-5 text-secondary" />
                </div>
                <h2 className="text-xl font-bold text-text-primary">Experience</h2>
              </div>
              <ExperienceTimeline experience={candidate.experience} />
            </Card>
            
            {/* Education */}
            <Card>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-primary" />
                </div>
                <h2 className="text-xl font-bold text-text-primary">Education</h2>
              </div>
              <div>
                <h3 className="font-bold text-text-primary text-lg mb-1">
                  {candidate.education.institution}
                </h3>
                <p className="text-text-secondary mb-2">
                  {candidate.education.degree} - {candidate.education.location}
                </p>
              </div>
            </Card>
            
            {/* Skills */}
            <Card>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-full bg-accent-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-text-primary">Skills</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {candidate.skills.map((skill, index) => (
                  <Badge key={index} variant="primary" size="md">
                    {skill}
                  </Badge>
                ))}
              </div>
            </Card>
          </div>
          
          {/* Right Column - AI Insights */}
          <div className="lg:col-span-1">
            <AIInsightsPanel insights={candidate.aiInsights} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateProfile;