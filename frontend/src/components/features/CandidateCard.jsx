// src/components/features/CandidateCard.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Bookmark, MapPin } from 'lucide-react';
import Card from '@/components/common/Card';
import Avatar from '@/components/common/Avatar';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';

const CandidateCard = ({ candidate }) => {
  const navigate = useNavigate();

  // Get match score - API returns 'score' (0-1), fallback to matchPercentage or 0
  const matchScore = candidate.score
    ? Math.round(candidate.score * 100)
    : (candidate.matchPercentage || 0);

  const handleViewProfile = () => {
    navigate(`/candidates/${candidate.id}`);
  };

  const handleSave = (e) => {
    e.stopPropagation();
    // TODO: Implement save functionality
    console.log('Saved candidate:', candidate.id);
  };

  return (
    <Card hoverable className="relative">
      {/* Match Badge */}
      <div className="absolute top-4 right-4">
        <Badge variant="match" size="sm" className="font-bold">
          {matchScore}% Match
        </Badge>
      </div>
      
      {/* Avatar & Info */}
      <div className="flex flex-col items-center text-center mb-4">
        <Avatar
          name={candidate.name}
          src={candidate.avatar}
          size="xl"
          className="mb-3"
        />
        <h3 className="text-lg font-bold text-text-primary mb-1">
          {candidate.name}
        </h3>
        <p className="text-sm text-text-secondary mb-2">
          {candidate.title}
        </p>
        <div className="flex items-center gap-1 text-xs text-text-muted">
          <MapPin className="w-3 h-3" />
          <span>{candidate.location}</span>
        </div>
      </div>
      
      {/* Skills */}
      <div className="flex flex-wrap gap-2 mb-4 justify-center">
        {candidate.skills.slice(0, 3).map((skill, index) => (
          <Badge key={index} variant="primary" size="sm">
            {skill}
          </Badge>
        ))}
        {candidate.skills.length > 3 && (
          <Badge variant="default" size="sm">
            +{candidate.skills.length - 3}
          </Badge>
        )}
      </div>
      
      {/* Actions */}
      <div className="flex gap-2">
        <Button
          variant="primary"
          size="md"
          onClick={handleViewProfile}
          className="flex-1"
        >
          View Profile
        </Button>
        <Button
          variant="outline"
          size="md"
          onClick={handleSave}
          icon={<Bookmark className="w-4 h-4" />}
          className="px-3"
        />
      </div>
    </Card>
  );
};

export default CandidateCard;