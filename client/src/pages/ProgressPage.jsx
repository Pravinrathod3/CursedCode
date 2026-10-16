import { useState, useEffect } from 'react';
import Header from '../components/Header.jsx';
import Footer from '../components/Footer.jsx';
import GradeBadge from '../components/GradeBadge.jsx';
import { getLearnerProfile } from '../services/api.js';

const JJK_RANKS_LEGEND = [
  { grade: 'Grade 4', rank: 'RANK IV', diff: 'Easy' },
  { grade: 'Grade 3', rank: 'RANK III', diff: 'Medium' },
  { grade: 'Grade 2', rank: 'RANK II', diff: 'Hard' },
  { grade: 'Semi-Grade 1', rank: 'SEMI-RANK I', diff: 'Advanced' },
  { grade: 'Grade 1', rank: 'RANK I', diff: 'Expert' },
  { grade: 'Special Grade', rank: 'SPECIAL', diff: 'Supreme' }
];

const MISTAKE_METADATA = {
  off_by_one: {
    title: 'Off by one',
    description: 'Your loop or index stops one step too early or goes one step too far.'
  },
  unhandled_short_input: {
    title: 'Short input not handled',
    description: 'Your code breaks, or gives a wrong answer, on empty or very short input.'
  },
  print_not_return: {
    title: 'Printed instead of returned',
    description: 'Your function prints a result instead of returning it.'
  },
  boundary_comparison: {
    title: 'Boundary comparison',
    description: 'A comparison such as less-than versus less-than-or-equal is off at the exact boundary value.'
  },
  mutates_input: {
    title: 'Mutates input',
    description: 'The function changes an input collection when it should preserve it.'
  }
};

const DEFAULT_MASTERY = [
  { concept: 'Lists', score: 0.00, grade: 'Grade 4', difficulty: 'Easy' },
  { concept: 'Loops', score: 0.00, grade: 'Grade 4', difficulty: 'Easy' },
  { concept: 'Strings', score: 0.00, grade: 'Grade 4', difficulty: 'Easy' },
  { concept: 'Slicing', score: 0.00, grade: 'Grade 4', difficulty: 'Easy' },
  { concept: 'Indexing', score: 0.00, grade: 'Grade 4', difficulty: 'Easy' },
  { concept: 'Comparison', score: 0.00, grade: 'Grade 4', difficulty: 'Easy' }
];

export default function ProgressPage({ onNavigate, learnerName }) {
  const [masteryData, setMasteryData] = useState(DEFAULT_MASTERY);
  const [nextChallenge, setNextChallenge] = useState({
    challenge_id: 'last-k-total',
    title: 'Last K Total',
    grade: 'Grade 4',
    difficulty: 'Easy',
    reason: 'Start with fundamental sequence slicing to establish your diagnostic foundation.'
  });
  const [recurringMistakes, setRecurringMistakes] = useState([]);

  useEffect(() => {
    let active = true;
    getLearnerProfile(learnerName).then((profile) => {
      if (!active || !profile) return;

      if (Array.isArray(profile.mastery) && profile.mastery.length > 0) {
        setMasteryData(profile.mastery.map((m) => ({
          concept: m.concept,
          score: m.score !== undefined ? m.score : (m.estimate || 0),
          grade: m.grade || 'Grade 4',
          difficulty: m.difficulty || 'Easy'
        })));
      }

      if (profile.next_challenge) {
        setNextChallenge(profile.next_challenge);
      }

      if (Array.isArray(profile.recurring_mistakes)) {
        setRecurringMistakes(profile.recurring_mistakes);
      }
    });

    return () => { active = false; };
  }, [learnerName]);

  return (
    <div className="page-shell">
      <Header currentPath="/progress" onNavigate={onNavigate} learnerName={learnerName} />

      <main className="content-container">
        <section className="page-intro">
          <p className="eyebrow">
            <span className="eyebrow-accent">// SORCERER RANK EVALUATION</span>
            <span>Sorcerer Grade Evaluation</span>
          </p>
          <div className="intro-header">
            <h1 className="page-title">
              CONCEPT MASTERY &<br />
              <span className="title-highlight">RANKING PROFILE.</span>
            </h1>
            <p className="intro-lead">
              Diagnostic telemetry across core Python techniques. Mastery points are awarded exclusively through independent problem resolution without hint consumption.
            </p>
          </div>
        </section>

        {/* Grade Legend Callout per rules.md 2.2 */}
        <div className="sorcerer-ladder-callout">
          <div className="ladder-header">
            <span className="ladder-icon" aria-hidden="true">★</span>
            <div className="ladder-title-group">
              <span className="ladder-title">OFFICIAL JUJUTSU GRADE LADDER</span>
              <span className="ladder-desc">Grade 4 is the starting level. Special Grade is the highest.</span>
            </div>
          </div>
          <div className="ladder-ranks-track">
            {JJK_RANKS_LEGEND.map((g, idx) => (
              <div key={g.grade} className="ladder-step">
                <span className="step-rank" aria-hidden="true">{g.rank}</span>
                <span className="step-name">{g.grade}</span>
                <span className="step-diff">{g.diff}</span>
                {idx < JJK_RANKS_LEGEND.length - 1 && (
                  <span className="step-divider" aria-hidden="true">›</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Next Challenge Recommendation */}
        {nextChallenge && (
          <section className="priority-mission-card">
            <div className="card-seal-corner card-seal-corner--tl" aria-hidden="true" />
            <div className="card-seal-corner card-seal-corner--tr" aria-hidden="true" />
            <div className="next-challenge__header">
              <div>
                <p className="eyebrow">
                  <span className="eyebrow-accent">// NEXT MISSION</span>
                  <span>Recommended Next Mission</span>
                </p>
                <h2 className="next-challenge__title">{nextChallenge.title || 'Next Mission'}</h2>
              </div>
              <GradeBadge grade={nextChallenge.grade || 'Grade 4'} difficulty={nextChallenge.difficulty || 'Easy'} />
            </div>
            <p className="next-challenge__reason">
              <strong>Diagnostic Dispatch:</strong> {nextChallenge.reason}
            </p>
            <button
              type="button"
              className="primary-energy-btn next-challenge__btn"
              onClick={() => onNavigate(`/challenges/${nextChallenge.challenge_id}`)}
            >
              <span>Engage Mission</span>
              <span className="btn-arrow" aria-hidden="true">→</span>
            </button>
          </section>
        )}

        {/* Concept Mastery Grid */}
        <section className="mastery-section">
          <div className="section-title-bar">
            <h2 className="section-heading">Concept Breakdown</h2>
            <span className="section-tag" aria-hidden="true">ANALYSIS</span>
          </div>
          <div className="mastery-grid">
            {masteryData.map((item) => (
              <article key={item.concept} className="mastery-dossier-card">
                <div className="mastery-card__header">
                  <h3 className="mastery-card__name">{item.concept}</h3>
                  <GradeBadge grade={item.grade} difficulty={item.difficulty} size="sm" />
                </div>
                <div className="mastery-bar-container">
                  <div
                    className="mastery-bar-fill"
                    style={{ width: `${Math.round(item.score * 100)}%` }}
                    aria-valuenow={Math.round(item.score * 100)}
                    aria-valuemin="0"
                    aria-valuemax="100"
                    role="progressbar"
                  ></div>
                </div>
                <div className="mastery-card__footer">
                  <span className="mastery-score-label">Rating: <strong>{item.score.toFixed(2)}</strong> / 1.00</span>
                  <span className="mastery-pct-label">{Math.round(item.score * 100)}%</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        {/* Recurring Mistakes Panel per rules.md */}
        <section className="mistakes-section">
          <div className="section-title-bar">
            <h2 className="section-heading">Recurring Mistake Patterns</h2>
            <span className="section-tag" aria-hidden="true">HISTORY</span>
          </div>
          <div className="mistakes-panel">
            {recurringMistakes.length > 0 ? (
              <div className="mistakes-list" style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '100%' }}>
                {recurringMistakes.map((m) => {
                  const meta = MISTAKE_METADATA[m.category] || {
                    title: m.category,
                    description: `Appeared across ${m.challenge_count} different trials.`
                  };
                  return (
                    <div key={m.category} className="hint-step--revealed" style={{ width: '100%' }}>
                      <span className="step-badge">{meta.title} · {m.challenge_count} Challenges</span>
                      <span className="step-text">{meta.description}</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <>
                <div className="mistakes-empty-seal" aria-hidden="true">CLEARED</div>
                <h3 className="mistakes-empty-title">No Recurring Mistakes Detected</h3>
                <p className="empty-mistakes-text">
                  Clean sorcery record. Diagnostic gap patterns are only flagged when identical error categories appear across multiple distinct challenges.
                </p>
              </>
            )}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
