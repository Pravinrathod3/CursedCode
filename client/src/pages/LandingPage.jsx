import { useEffect, useState } from 'react';
import Footer from '../components/Footer.jsx';
import { useTheme } from '../context/ThemeContext.jsx';

const CODE_SAMPLE = 'def find_first_match(values):\n    for index, value in enumerate(values):\n        if value > 0:\n            return index\n    return -1';

export default function LandingPage({ onNavigate, learnerName, onUpdateLearnerName }) {
  const { isLight } = useTheme();
  const [inputName, setInputName] = useState(learnerName || '');
  const [typedCode, setTypedCode] = useState(() => (
    window.matchMedia('(prefers-reduced-motion: reduce)').matches ? CODE_SAMPLE : ''
  ));

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return undefined;

    let characterIndex = 0;
    let deleting = false;
    let typingTimer;

    const animateCode = () => {
      if (deleting) {
        characterIndex = Math.max(0, characterIndex - 2);
        setTypedCode(CODE_SAMPLE.slice(0, characterIndex));
        if (characterIndex === 0) deleting = false;
      } else {
        characterIndex = Math.min(CODE_SAMPLE.length, characterIndex + 1);
        setTypedCode(CODE_SAMPLE.slice(0, characterIndex));
        if (characterIndex === CODE_SAMPLE.length) deleting = true;
      }

      const pause = characterIndex === CODE_SAMPLE.length ? 1500 : characterIndex === 0 ? 500 : 32;
      typingTimer = window.setTimeout(animateCode, pause);
    };

    typingTimer = window.setTimeout(animateCode, 450);

    return () => window.clearTimeout(typingTimer);
  }, []);

  const logoSrc = isLight
    ? '/assets/brand/brand_logo_wordmark_light.png'
    : '/assets/brand/brand_logo_wordmark.png';

  const handleSubmit = (e) => {
    e.preventDefault();
    const finalName = inputName.trim() || 'zeroeight';
    onUpdateLearnerName(finalName);
    onNavigate('/challenges');
  };

  return (
    <div className="landing-layout">
      <video
        className="landing-video-background"
        src="/assets/landing_energy.mp4"
        autoPlay
        muted
        loop
        playsInline
        preload="metadata"
        aria-hidden="true"
        tabIndex={-1}
      />
      {/* Decorative Manga Halftone Screentone Overlay */}
      <div className="manga-screentone" aria-hidden="true" />

      <main className="landing-hero">
        <div className="landing-content">
          <div className="landing-brand-header">
            <img
              key={logoSrc}
              src={logoSrc}
              alt="cursedCode"
              className="landing-brand-logo"
              onError={(e) => { e.currentTarget.style.display = 'none'; }}
            />
          </div>

          <h1 className="hero-title hero-title--tagline">
            Debugging the dark arts of software engineering.
          </h1>

          <p className="hero-lead">
            Dissect complex logic errors with zero distraction. Learn the exact boundary conditions that make Python code reliable — with progressive hints ready only when you hit a wall.
          </p>

          {/* Dossier Registration Card */}
          <div className="sorcerer-dossier-card">
            <div className="card-seal-corner card-seal-corner--tl" aria-hidden="true" />
            <div className="card-seal-corner card-seal-corner--tr" aria-hidden="true" />
            <div className="card-seal-corner card-seal-corner--bl" aria-hidden="true" />
            <div className="card-seal-corner card-seal-corner--br" aria-hidden="true" />

            <div className="dossier-header">
              <span className="dossier-tag">LEARNER DOSSIER</span>
              <span className="dossier-sub">REGISTRATION</span>
            </div>

            <form className="learner-form" onSubmit={handleSubmit}>
              <div className="form-field">
                <label className="learner-form__label" htmlFor="learner-input">
                  Choose a learner pseudonym
                </label>
                <div className="input-affix-wrapper">
                  <span className="input-prefix" aria-hidden="true">user:</span>
                  <input
                    id="learner-input"
                    type="text"
                    className="learner-form__input"
                    value={inputName}
                    onChange={(e) => setInputName(e.target.value)}
                    placeholder="e.g. silentpanda"
                    maxLength={24}
                    autoComplete="off"
                  />
                </div>
              </div>

              <button type="submit" className="primary-energy-btn">
                <span>Start Training</span>
                <span className="btn-arrow" aria-hidden="true">→</span>
              </button>

              <p className="learner-form__tip">
                <span className="tip-shield" aria-hidden="true">🛡</span>
                Use a pseudonym — no real names or external accounts needed.
              </p>
            </form>
          </div>
        </div>

        {/* Pillars / Three Tenets */}
        <aside className="landing-pillars" aria-label="Core training tenets">
          <div className="landing-code-terminal" aria-label="Python code example">
            <div className="landing-code-terminal__bar">
              <span className="landing-code-lights" aria-hidden="true"><i /><i /><i /></span>
              <span>practice.py</span>
              <span className="landing-code-status">LIVE PREVIEW</span>
            </div>
            <pre className="landing-code-terminal__body"><code>{typedCode}<span className="landing-code-caret" aria-hidden="true" /></code></pre>
            <div className="landing-code-terminal__footer"><span>Python 3</span><span>trace the logic · master each edge case</span></div>
          </div>
          <div className="pillars-header">
            <span className="pillars-header__tag">TRAINING PROTOCOLS</span>
            <span className="pillars-header__sub">3 PILLARS</span>
          </div>

          <div className="pillar-item">
            <div className="pillar-num-badge">
              <span className="pillar-num">01</span>
            </div>
            <div className="pillar-info">
              <h3 className="pillar-title">Focused Workspace</h3>
              <p className="pillar-text">
                Clean, distraction-reduced editor preloaded with Python starters. No clunky IDE clutter.
              </p>
            </div>
          </div>

          <div className="pillar-item">
            <div className="pillar-num-badge">
              <span className="pillar-num">02</span>
            </div>
            <div className="pillar-info">
              <h3 className="pillar-title">Immediate Verdict</h3>
              <p className="pillar-text">
                Visible test assertions alongside rigorous hidden checks that test corner and edge cases privately.
              </p>
            </div>
          </div>

          <div className="pillar-item">
            <div className="pillar-num-badge">
              <span className="pillar-num">03</span>
            </div>
            <div className="pillar-info">
              <h3 className="pillar-title">Progressive Insight</h3>
              <p className="pillar-text">
                Reveal structured diagnostic hints one step at a time without ever giving away the full answer.
              </p>
            </div>
          </div>
        </aside>
      </main>

      <Footer />
    </div>
  );
}
