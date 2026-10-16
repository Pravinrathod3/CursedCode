export default function Header({ currentPath, onNavigate, learnerName = 'zeroeight' }) {
  const isChallengesActive = currentPath === '/challenges' || currentPath.startsWith('/challenges/');
  const isProgressActive = currentPath === '/progress';

  return (
    <header className="site-header">
      <div className="site-header__container">
        <button
          type="button"
          className="brand-logo"
          onClick={() => onNavigate('/')}
          aria-label="cursedCode Home"
        >
          <img
            src="/assets/brand/brand_logo_wordmark.png"
            alt="cursedCode"
            className="brand-logo__img"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
              const fallback = e.currentTarget.parentElement?.querySelector('.brand-logo__fallback');
              if (fallback) fallback.style.display = 'inline-flex';
            }}
          />
          <span className="brand-logo__fallback" style={{ display: 'none' }}>
            <span className="brand-logo__mark" aria-hidden="true">C</span>
            <span className="brand-logo__wordmark">cursedCode</span>
          </span>
        </button>

        <nav className="site-header__nav" aria-label="Primary navigation">
          <button
            type="button"
            className={`nav-link ${isChallengesActive ? 'nav-link--active' : ''}`}
            onClick={() => onNavigate('/challenges')}
            aria-current={isChallengesActive ? 'page' : undefined}
          >
            Challenges
          </button>
          <button
            type="button"
            className={`nav-link ${isProgressActive ? 'nav-link--active' : ''}`}
            onClick={() => onNavigate('/progress')}
            aria-current={isProgressActive ? 'page' : undefined}
          >
            Progress
          </button>
        </nav>

        <div className="site-header__learner" title="Pseudonymous learner identifier">
          <span className="learner-dot" aria-hidden="true">●</span>
          <span className="learner-label">Learner:</span>
          <span className="learner-name">{learnerName}</span>
        </div>
      </div>
    </header>
  );
}
