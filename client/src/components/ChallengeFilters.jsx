import { CONCEPTS, GRADE_SCALE, STATUSES } from '../data/challenges.js';

export default function ChallengeFilters({
  searchQuery,
  onSearchChange,
  selectedGrade,
  onGradeChange,
  selectedConcept,
  onConceptChange,
  selectedStatus,
  onStatusChange,
  onClearFilters,
  hasActiveFilters
}) {
  return (
    <section className="filters-console" aria-label="Filter challenges">
      <div className="filters-console__header">
        <span className="console-indicator" aria-hidden="true">◆</span>
        <span className="console-title">Challenge Filters</span>
        <span className="console-line" aria-hidden="true" />
      </div>

      <div className="filters-grid">
        {/* Search Field */}
        <div className="filter-group filter-group--search">
          <label htmlFor="challenge-search" className="filter-label">
            <span className="filter-label__main">Search</span>
          </label>
          <div className="search-input-wrapper">
            <span className="search-icon" aria-hidden="true">⌕</span>
            <input
              id="challenge-search"
              type="text"
              className="filter-input filter-input--search"
              placeholder="Search challenges by keyword, concept, or title..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              aria-label="Search challenges by title, description, or concept"
            />
            {searchQuery && (
              <button
                type="button"
                className="clear-search-btn"
                onClick={() => onSearchChange('')}
                aria-label="Clear search input"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Grade / Difficulty Filter */}
        <div className="filter-group">
          <label htmlFor="grade-filter" className="filter-label">
            <span className="filter-label__main">Grade</span>
          </label>
          <div className="select-wrapper">
            <select
              id="grade-filter"
              className="filter-select"
              value={selectedGrade}
              onChange={(e) => onGradeChange(e.target.value)}
            >
              <option value="All grades">All grades</option>
              {GRADE_SCALE.slice(0, 3).map((item) => (
                <option key={item.grade} value={item.grade}>
                  {item.grade} · {item.difficulty}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Concept Filter */}
        <div className="filter-group">
          <label htmlFor="concept-filter" className="filter-label">
            <span className="filter-label__main">Concept</span>
          </label>
          <div className="select-wrapper">
            <select
              id="concept-filter"
              className="filter-select"
              value={selectedConcept}
              onChange={(e) => onConceptChange(e.target.value)}
            >
              <option value="All concepts">All concepts</option>
              {CONCEPTS.map((concept) => (
                <option key={concept} value={concept}>
                  {concept}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Status Filter */}
        <div className="filter-group">
          <label htmlFor="status-filter" className="filter-label">
            <span className="filter-label__main">Status</span>
          </label>
          <div className="select-wrapper">
            <select
              id="status-filter"
              className="filter-select"
              value={selectedStatus}
              onChange={(e) => onStatusChange(e.target.value)}
            >
              <option value="All statuses">All statuses</option>
              {STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Clear Filters Action */}
        <div className="filter-group filter-group--action">
          <label className="filter-label filter-label--spacer" aria-hidden="true">&nbsp;</label>
          <button
            type="button"
            className="reset-filters-btn"
            onClick={onClearFilters}
            disabled={!hasActiveFilters}
            title={hasActiveFilters ? "Reset all search and filter fields" : "No active filters to reset"}
          >
            <span className="btn-icon" aria-hidden="true">↺</span>
            <span>Clear filters</span>
          </button>
        </div>
      </div>
    </section>
  );
}
