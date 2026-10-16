import { useState, useMemo, useEffect } from 'react';
import Header from '../components/Header.jsx';
import Footer from '../components/Footer.jsx';
import ChallengeFilters from '../components/ChallengeFilters.jsx';
import ChallengeCard from '../components/ChallengeCard.jsx';
import SkeletonCard from '../components/SkeletonCard.jsx';
import { CHALLENGES } from '../data/challenges.js';
import { getChallenges } from '../services/api.js';

export default function ChallengesPage({ onNavigate, learnerName }) {
  // Parse initial state from URL query parameters if available
  const initialParams = useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    return {
      q: params.get('q') || '',
      grade: params.get('grade') || 'All grades',
      concept: params.get('concept') || 'All concepts',
      status: params.get('status') || 'All statuses'
    };
  }, []);

  const [searchQuery, setSearchQuery] = useState(initialParams.q);
  const [selectedGrade, setSelectedGrade] = useState(initialParams.grade);
  const [selectedConcept, setSelectedConcept] = useState(initialParams.concept);
  const [selectedStatus, setSelectedStatus] = useState(initialParams.status);
  const [isLoading, setIsLoading] = useState(true);
  const [challenges, setChallenges] = useState(CHALLENGES);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let active = true;
    getChallenges(learnerName).then((data) => {
      if (active) {
        setChallenges(data);
        setIsLive(true);
        setIsLoading(false);
      }
    }).catch(() => {
      if (active) {
        setIsLoading(false);
      }
    });

    return () => { active = false; };
  }, [learnerName]);

  // Sync state to URL query params
  useEffect(() => {
    const params = new URLSearchParams();
    if (searchQuery.trim()) params.set('q', searchQuery.trim());
    if (selectedGrade !== 'All grades') params.set('grade', selectedGrade);
    if (selectedConcept !== 'All concepts') params.set('concept', selectedConcept);
    if (selectedStatus !== 'All statuses') params.set('status', selectedStatus);

    const queryString = params.toString();
    const newUrl = queryString ? `/challenges?${queryString}` : '/challenges';
    window.history.replaceState({}, '', newUrl);
  }, [searchQuery, selectedGrade, selectedConcept, selectedStatus]);

  // Handle active filters detection
  const hasActiveFilters = Boolean(
    searchQuery.trim() ||
    selectedGrade !== 'All grades' ||
    selectedConcept !== 'All concepts' ||
    selectedStatus !== 'All statuses'
  );

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedGrade('All grades');
    setSelectedConcept('All concepts');
    setSelectedStatus('All statuses');
  };

  // Filtered dataset
  const filteredChallenges = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return challenges.filter((item) => {
      // Search matching title, description, or concept tags
      const matchesSearch =
        !query ||
        item.title.toLowerCase().includes(query) ||
        (item.description && item.description.toLowerCase().includes(query)) ||
        (item.tags && item.tags.some((tag) => tag.toLowerCase().includes(query)));

      // Grade matching
      const matchesGrade =
        selectedGrade === 'All grades' || item.grade === selectedGrade;

      // Concept matching
      const matchesConcept =
        selectedConcept === 'All concepts' || (item.tags && item.tags.includes(selectedConcept));

      // Status matching
      const matchesStatus =
        selectedStatus === 'All statuses' || item.status === selectedStatus;

      return matchesSearch && matchesGrade && matchesConcept && matchesStatus;
    });
  }, [challenges, searchQuery, selectedGrade, selectedConcept, selectedStatus]);

  // Navigate to challenge workspace
  const handleSelectChallenge = (id) => {
    onNavigate(`/challenges/${id}`);
  };

  return (
    <div className="page-shell">
      <Header currentPath="/challenges" onNavigate={onNavigate} learnerName={learnerName} />

      <main className="content-container">
        {/* Intro Section */}
        <section className="page-intro">
          <p className="eyebrow">
            <span className="eyebrow-accent">// MISSION ARCHIVE</span>
            <span>Browse Challenges</span>
          </p>
          <div className="intro-header">
            <h1 className="page-title">
              CHOOSE YOUR NEXT<br />
              <span className="title-highlight">TRAINING MISSION.</span>
            </h1>
            <p className="intro-lead">
              Solidify the small algorithmic decisions that make Python code bulletproof. From Grade 4 fundamentals to Grade 2 trials, practice under strict test case scrutiny.
            </p>
          </div>
        </section>

        {/* Filter Controls */}
        <ChallengeFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedGrade={selectedGrade}
          onGradeChange={setSelectedGrade}
          selectedConcept={selectedConcept}
          onConceptChange={setSelectedConcept}
          selectedStatus={selectedStatus}
          onStatusChange={setSelectedStatus}
          onClearFilters={handleClearFilters}
          hasActiveFilters={hasActiveFilters}
        />

        {/* Status / Active Filters Bar */}
        <div className="status-bar" aria-live="polite">
          <div className="status-bar__count">
            <strong>{filteredChallenges.length}</strong> {filteredChallenges.length === 1 ? 'challenge' : 'challenges'} available
            {hasActiveFilters && (
              <span className="status-bar__filtered-note"> (filtered from {challenges.length})</span>
            )}
          </div>

          <div className="status-bar__active-pills">
            {searchQuery && (
              <button
                type="button"
                className="filter-pill"
                onClick={() => setSearchQuery('')}
                title="Remove search query"
              >
                Search: "{searchQuery}" ✕
              </button>
            )}
            {selectedGrade !== 'All grades' && (
              <button
                type="button"
                className="filter-pill"
                onClick={() => setSelectedGrade('All grades')}
                title="Remove grade filter"
              >
                {selectedGrade} ✕
              </button>
            )}
            {selectedConcept !== 'All concepts' && (
              <button
                type="button"
                className="filter-pill"
                onClick={() => setSelectedConcept('All concepts')}
                title="Remove concept filter"
              >
                {selectedConcept} ✕
              </button>
            )}
            {selectedStatus !== 'All statuses' && (
              <button
                type="button"
                className="filter-pill"
                onClick={() => setSelectedStatus('All statuses')}
                title="Remove status filter"
              >
                {selectedStatus} ✕
              </button>
            )}
            <span className="status-bar__demo-badge">
              {isLive ? 'Live Dojo Connected' : 'Local practice data'}
            </span>
          </div>
        </div>

        {/* Challenge Cards Grid or States */}
        {isLoading ? (
          <div className="challenges-grid" aria-busy="true">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : filteredChallenges.length > 0 ? (
          <div className="challenges-grid">
            {filteredChallenges.map((challenge) => (
              <ChallengeCard
                key={challenge.id}
                challenge={challenge}
                onSelect={handleSelectChallenge}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state__icon" aria-hidden="true">∅</div>
            <h2 className="empty-state__title">No Challenges Match Filters</h2>
            <p className="empty-state__lead">
              Try adjusting your query or resetting filters to review the full mission roster.
            </p>
            <button
              type="button"
              className="primary-energy-btn"
              onClick={handleClearFilters}
            >
              Reset all filters
            </button>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
