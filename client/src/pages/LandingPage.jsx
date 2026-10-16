import { useState } from 'react';
import Footer from '../components/Footer.jsx';

export default function LandingPage({ onNavigate, learnerName, onUpdateLearnerName }) {
  const [inputName, setInputName] = useState(learnerName || '');

  const handleSubmit = (e) => {
    e.preventDefault();
    const finalName = inputName.trim() || 'zeroeight';
    onUpdateLearnerName(finalName);
    onNavigate('/challenges');
  };

  return (
    <div className="landing-layout">
      {/* Decorative Manga Halftone Screentone Overlay */}
      <div className="manga-screentone" aria-hidden="true" />

      <main className="landing-hero">
        <div className="landing-content">
          <div className="landing-brand-header">
            <img
              src="/assets/brand/brand_logo_wordmark.png"
              alt="cursedCode"
              className="landing-brand-logo"
              onError={(e) => { e.currentTarget.style.display = 'none'; }}
            />
            <div className="brand-badge-pill">
              <span className="badge-dot" aria-hidden="true">●</span>
              <span>Fan Project · Python Practice Arena</span>
            </div>
          </div>

          <p className="landing-eyebrow">
            <span className="eyebrow-accent">// PRACTICE ARENA</span>
            <span>Python Practice for Patient Problem-Solvers</span>
          </p>

          <h1 className="hero-title">
            FIND THE BUG.<br />
            <span className="hero-gradient-text">KEEP THE INSIGHT.</span>
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
