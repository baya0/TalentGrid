// src/pages/Search/FilterPanel.jsx
import React, { useState, useEffect } from 'react';
import { RotateCcw } from 'lucide-react';
import Button from '@/components/common/Button';

const FilterPanel = ({ filters, onFilterChange }) => {
  const [localFilters, setLocalFilters] = useState(filters);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  // Experience range slider values
  const [expRange, setExpRange] = useState({
    min: filters.min_experience || 0,
    max: filters.max_experience || 20
  });

  const handleExpMinChange = (e) => {
    const value = parseInt(e.target.value) || 0;
    const newRange = { ...expRange, min: value };
    setExpRange(newRange);
    const newFilters = {
      ...localFilters,
      min_experience: value,
      max_experience: expRange.max
    };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleExpMaxChange = (e) => {
    const value = parseInt(e.target.value) || 20;
    const newRange = { ...expRange, max: value };
    setExpRange(newRange);
    const newFilters = {
      ...localFilters,
      min_experience: expRange.min,
      max_experience: value
    };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleLanguageChange = (e) => {
    const value = e.target.value;
    const languagesArray = value ? value.split(',').map(s => s.trim()).filter(Boolean) : [];
    const newFilters = { ...localFilters, languages: languagesArray };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleLocationChange = (e) => {
    const value = e.target.value;
    const newFilters = { ...localFilters, location: value || null };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleReset = () => {
    const resetFilters = {
      min_experience: null,
      max_experience: null,
      languages: [],
      location: null,
    };
    setLocalFilters(resetFilters);
    setExpRange({ min: 0, max: 20 });
    onFilterChange(resetFilters);
  };

  const hasActiveFilters = () => {
    return (
      localFilters.min_experience !== null ||
      localFilters.max_experience !== null ||
      (localFilters.languages && localFilters.languages.length > 0) ||
      localFilters.location
    );
  };

  return (
    <div className="w-72 flex-shrink-0 border-r border-border p-6 overflow-y-auto bg-background">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-text-primary">Filters</h2>
        {hasActiveFilters() && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            className="text-text-muted hover:text-text-primary"
          >
            <RotateCcw className="w-4 h-4 mr-1" />
            Reset
          </Button>
        )}
      </div>

      {/* Experience Range */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-text-primary mb-4">
          Experience (Years)
        </h3>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <label className="text-xs text-text-muted block mb-1">Min</label>
              <input
                type="number"
                min="0"
                max="50"
                value={expRange.min}
                onChange={handleExpMinChange}
                className="w-full px-3 py-2 rounded-lg border border-border bg-white text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-secondary/50"
              />
            </div>
            <span className="text-text-muted mt-5">-</span>
            <div className="flex-1">
              <label className="text-xs text-text-muted block mb-1">Max</label>
              <input
                type="number"
                min="0"
                max="50"
                value={expRange.max}
                onChange={handleExpMaxChange}
                className="w-full px-3 py-2 rounded-lg border border-border bg-white text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-secondary/50"
              />
            </div>
          </div>
          <p className="text-xs text-text-muted">
            Filter candidates by years of experience
          </p>
        </div>
      </div>

      {/* Language Filter */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-text-primary mb-4">
          Languages
        </h3>
        <input
          type="text"
          placeholder="English, Arabic, French..."
          value={(localFilters.languages || []).join(', ')}
          onChange={handleLanguageChange}
          className="w-full px-3 py-2 rounded-lg border border-border bg-white text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-secondary/50 placeholder:text-text-muted"
        />
        <p className="text-xs text-text-muted mt-2">
          Separate languages with commas
        </p>
      </div>

      {/* Location Filter */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-text-primary mb-4">
          Location
        </h3>
        <input
          type="text"
          placeholder="New York, Remote..."
          value={localFilters.location || ''}
          onChange={handleLocationChange}
          className="w-full px-3 py-2 rounded-lg border border-border bg-white text-text-primary text-sm focus:outline-none focus:ring-2 focus:ring-secondary/50 placeholder:text-text-muted"
        />
      </div>

      {/* Active Filters Summary */}
      {hasActiveFilters() && (
        <div className="pt-4 border-t border-border">
          <p className="text-xs text-text-muted mb-2">Active filters:</p>
          <div className="flex flex-wrap gap-1">
            {(localFilters.min_experience !== null || localFilters.max_experience !== null) && (
              <span className="px-2 py-1 bg-secondary/10 text-secondary text-xs rounded-full">
                {localFilters.min_experience || 0}-{localFilters.max_experience || 20} yrs
              </span>
            )}
            {(localFilters.languages || []).map(lang => (
              <span key={lang} className="px-2 py-1 bg-secondary/10 text-secondary text-xs rounded-full">
                {lang}
              </span>
            ))}
            {localFilters.location && (
              <span className="px-2 py-1 bg-secondary/10 text-secondary text-xs rounded-full">
                {localFilters.location}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterPanel;
