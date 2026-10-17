import { useTheme } from '../context/ThemeContext.jsx';

export default function Header({ currentPath, onNavigate, learnerName = 'zeroeight' }) {
  const { isLight, toggleTheme } = useTheme();
  const isChallengesActive = currentPath === '/challenges' || currentPath.startsWith('/challenges/');
  const isProgressActive = currentPath === '/progress';
  const isMilestonesActive = currentPath === '/milestones';
  const isImportActive = currentPath === '/import';

  const logoSrc = isLight
    ? '/assets/brand/brand_logo_wordmark_light.png'
    : '/assets/brand/brand_logo_wordmark.png';

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
            key={logoSrc}
            src={logoSrc}
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
            className={`nav-link ${isImportActive ? 'nav-link--active' : ''}`}
            onClick={() => onNavigate('/import')}
            aria-current={isImportActive ? 'page' : undefined}
          >
            <span>Import Sheets</span>
            <span className="nav-pill-badge">AI</span>
          </button>
          <button
            type="button"
            className={`nav-link ${isProgressActive ? 'nav-link--active' : ''}`}
            onClick={() => onNavigate('/progress')}
            aria-current={isProgressActive ? 'page' : undefined}
          >
            Progress
          </button>
          <button
            type="button"
            className={`nav-link ${isMilestonesActive ? 'nav-link--active' : ''}`}
            onClick={() => onNavigate('/milestones')}
            aria-current={isMilestonesActive ? 'page' : undefined}
          >
            Milestones
          </button>
        </nav>

        <div className="site-header__controls">
          {/* Theme Toggle Button */}
          <button
            type="button"
            className="theme-toggle-btn"
            onClick={toggleTheme}
            aria-label={`Switch to ${isLight ? 'Dark Domain' : 'Light Domain'} mode`}
            title={`Current: ${isLight ? 'Light Domain (#00E3FF)' : 'Dark Domain (Sukuna)'}. Click to switch.`}
          >
            <span className="theme-toggle-icon" aria-hidden="true">{isLight ? '🌙' : '☀️'}</span>
            <span className="theme-toggle-text">{isLight ? 'DARK' : 'LIGHT'}</span>
          </button>

          <div className="site-header__learner" title="Pseudonymous learner identifier">
            <span className="learner-dot" aria-hidden="true">●</span>
            <span className="learner-label">Learner:</span>
            <span className="learner-name">{learnerName}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
