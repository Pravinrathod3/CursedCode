import GradeBadge from './GradeBadge.jsx';

const STATUS_MAP = {
  Solved: { icon: '✓', label: 'Solved' },
  Attempted: { icon: '◬', label: 'Attempted' },
  New: { icon: '●', label: 'New' }
};

export default function ChallengeCard({ challenge, onSelect }) {
  const { id, title, description, grade, difficulty, tags, status, estimatedTime } = challenge;
  const statusInfo = STATUS_MAP[status] || STATUS_MAP.New;

  return (
    <article className={`challenge-card challenge-card--status-${status.toLowerCase()}`}>
      {/* Decorative crimson corner markers */}
      <div className="card-seal-corner card-seal-corner--tl" aria-hidden="true" />
      <div className="card-seal-corner card-seal-corner--tr" aria-hidden="true" />

      <div className="challenge-card__top">
        <GradeBadge grade={grade} difficulty={difficulty} />
        <div className="challenge-card__meta">
          {estimatedTime && (
            <span className="challenge-card__time" title="Estimated completion time">
              <span className="time-icon" aria-hidden="true">⏱</span> {estimatedTime}
            </span>
          )}
          <span 
            className={`status-stamp status-stamp--${status.toLowerCase()}`}
            title={`Status: ${status}`}
          >
            <span className="status-stamp__icon" aria-hidden="true">{statusInfo.icon}</span>
            <span className="status-stamp__text">{statusInfo.label}</span>
          </span>
        </div>
      </div>

      <div className="challenge-card__body">
        <h2 className="challenge-card__title">{title}</h2>
        <p className="challenge-card__desc">{description}</p>
      </div>

      <div className="challenge-card__tags" aria-label="Concepts">
        {tags.map((tag) => (
          <span key={tag} className="concept-ribbon">
            <span className="ribbon-hash" aria-hidden="true">#</span>
            {tag}
          </span>
        ))}
      </div>

      <div className="challenge-card__action">
        <button
          type="button"
          className="challenge-card__enter-btn"
          onClick={() => onSelect(id)}
          aria-label={`Enter challenge: ${title}`}
        >
          <span className="enter-text">Enter Challenge</span>
          <span className="enter-arrow" aria-hidden="true">↗</span>
        </button>
      </div>
    </article>
  );
}
