// src/pages/Search/Search.jsx
import React, { useState, useEffect } from 'react';
import { Search as SearchIcon, Sparkles, FileText, Users, ArrowRight } from 'lucide-react';
import FilterPanel from './FilterPanel';
import CandidateCard from '@/components/features/CandidateCard';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import Button from '@/components/common/Button';
import { searchCandidates } from '@/services/api';

const STORAGE_KEY = 'talentgrid_search_state';

const Search = () => {
  const [filters, setFilters] = useState({
    min_experience: null,
    max_experience: null,
    languages: [],
    location: null,
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [candidates, setCandidates] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState(null);

  // Load saved state from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const state = JSON.parse(saved);
        if (state.searchQuery) setSearchQuery(state.searchQuery);
        if (state.candidates) setCandidates(state.candidates);
        if (state.hasSearched) setHasSearched(state.hasSearched);
        if (state.filters) setFilters(state.filters);
      } catch (e) {
        console.error('Failed to load search state:', e);
      }
    }
  }, []);

  // Save state to localStorage
  useEffect(() => {
    if (hasSearched) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        searchQuery,
        candidates,
        hasSearched,
        filters,
      }));
    }
  }, [searchQuery, candidates, hasSearched, filters]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      // Pass filters wrapped in options object as expected by API
      const results = await searchCandidates(searchQuery, { filters });
      setCandidates(results.candidates || results || []);
    } catch (err) {
      console.error('Search failed:', err);
      setError('Search failed. Please try again.');
      setCandidates([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setCandidates([]);
    setHasSearched(false);
    localStorage.removeItem(STORAGE_KEY);
  };

  // Empty state component
  const EmptyState = () => (
    <div className="flex flex-col items-center justify-center py-16 px-8">
      <div className="w-24 h-24 bg-gradient-to-br from-secondary/20 to-primary/20 rounded-full flex items-center justify-center mb-6">
        <Sparkles className="w-12 h-12 text-secondary" />
      </div>

      <h2 className="text-2xl font-bold text-text-primary mb-3 text-center">
        Find Your Perfect Candidates
      </h2>

      <p className="text-text-secondary text-center max-w-md mb-8">
        Use AI-powered search to find candidates that match your requirements.
        Enter skills, job descriptions, or any criteria to get started.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl mb-8">
        <div className="bg-white rounded-xl p-4 border border-border">
          <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center mb-3">
            <FileText className="w-5 h-5 text-blue-600" />
          </div>
          <h3 className="font-semibold text-text-primary mb-1">Job Description</h3>
          <p className="text-sm text-text-secondary">Paste a job description to find matching candidates</p>
        </div>

        <div className="bg-white rounded-xl p-4 border border-border">
          <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center mb-3">
            <SearchIcon className="w-5 h-5 text-green-600" />
          </div>
          <h3 className="font-semibold text-text-primary mb-1">Skills Search</h3>
          <p className="text-sm text-text-secondary">Search by specific skills like "React, Python, AWS"</p>
        </div>

        <div className="bg-white rounded-xl p-4 border border-border">
          <div className="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center mb-3">
            <Users className="w-5 h-5 text-purple-600" />
          </div>
          <h3 className="font-semibold text-text-primary mb-1">Role Search</h3>
          <p className="text-sm text-text-secondary">Find by role: "Senior Data Scientist"</p>
        </div>
      </div>

      <div className="bg-gradient-to-r from-secondary/10 to-primary/10 rounded-xl p-6 w-full max-w-2xl">
        <h3 className="font-semibold text-text-primary mb-2 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-secondary" />
          Try these examples:
        </h3>
        <div className="flex flex-wrap gap-2">
          {[
            'Senior React Developer with 5+ years experience',
            'Python, Machine Learning, TensorFlow',
            'Full-stack engineer Node.js',
            'Data Scientist SQL AWS',
          ].map((example, i) => (
            <button
              key={i}
              onClick={() => {
                setSearchQuery(example);
              }}
              className="px-3 py-1.5 bg-white rounded-lg text-sm text-text-secondary hover:text-secondary hover:border-secondary border border-border transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex min-h-[calc(100vh-64px)]">
      {/* Left Sidebar - Filters */}
      <FilterPanel filters={filters} onFilterChange={handleFilterChange} />

      {/* Main Content */}
      <div className="flex-1 p-8 overflow-y-auto">
        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="relative">
            <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by skills, job description, or requirements..."
              className="w-full pl-12 pr-32 py-4 rounded-xl border border-border bg-white text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-secondary/50 focus:border-secondary transition-all"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-2">
              {hasSearched && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleClearSearch}
                >
                  Clear
                </Button>
              )}
              <Button
                type="submit"
                variant="secondary"
                size="sm"
                disabled={!searchQuery.trim() || loading}
              >
                {loading ? 'Searching...' : 'Search'}
                {!loading && <ArrowRight className="w-4 h-4 ml-1" />}
              </Button>
            </div>
          </div>
        </form>

        {/* Results Header - only show after search */}
        {hasSearched && (
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-text-primary">Results</h2>
            <p className="text-text-secondary mt-1">
              {loading
                ? 'Searching...'
                : `Found ${candidates.length} matching candidate${candidates.length !== 1 ? 's' : ''}`
              }
            </p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner size="lg" text="Searching candidates with AI..." />
          </div>
        ) : hasSearched ? (
          /* Search Results */
          candidates.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {candidates.map((candidate) => (
                <CandidateCard
                  key={candidate.id}
                  candidate={candidate}
                />
              ))}
            </div>
          ) : (
            /* No Results */
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-text-primary mb-2">No candidates found</h3>
              <p className="text-text-secondary max-w-md mx-auto">
                Try adjusting your search query or filters. You can also upload more CVs to expand your talent pool.
              </p>
            </div>
          )
        ) : (
          /* Empty State - No search yet */
          <EmptyState />
        )}
      </div>
    </div>
  );
};

export default Search;
