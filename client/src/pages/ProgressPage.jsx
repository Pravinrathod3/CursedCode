import Header from '../components/Header.jsx';
import Footer from '../components/Footer.jsx';
import GradeBadge from '../components/GradeBadge.jsx';

const JJK_RANKS_LEGEND = [
  { grade: 'Grade 4', rank: 'RANK IV', diff: 'Easy' },
  { grade: 'Grade 3', rank: 'RANK III', diff: 'Medium' },
  { grade: 'Grade 2', rank: 'RANK II', diff: 'Hard' },
  { grade: 'Semi-Grade 1', rank: 'SEMI-RANK I', diff: 'Advanced' },
  { grade: 'Grade 1', rank: 'RANK I', diff: 'Expert' },
  { grade: 'Special Grade', rank: 'SPECIAL', diff: 'Supreme' }
];

export default function ProgressPage({ onNavigate, learnerName }) {
  // Mock mastery data for concepts
  const mockMastery = [
    { concept: 'Lists', score: 0.65, grade: 'Semi-Grade 1', difficulty: 'Advanced' },
    { concept: 'Loops', score: 0.42, grade: 'Grade 2', difficulty: 'Hard' },
    { concept: 'Strings', score: 0.35, grade: 'Grade 3', difficulty: 'Medium' },
    { concept: 'Slicing', score: 0.78, grade: 'Semi-Grade 1', difficulty: 'Advanced' },
    { concept: 'Indexing', score: 0.50, grade: 'Grade 2', difficulty: 'Hard' },
    { concept: 'Comparison', score: 0.25, grade: 'Grade 3', difficulty: 'Medium' }
  ];

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
        <section className="priority-mission-card">
          <div className="card-seal-corner card-seal-corner--tl" aria-hidden="true" />
          <div className="card-seal-corner card-seal-corner--tr" aria-hidden="true" />
          <div className="next-challenge__header">
            <div>
              <p className="eyebrow">
                <span className="eyebrow-accent">// NEXT MISSION</span>
                <span>Recommended Next Mission</span>
              </p>
              <h2 className="next-challenge__title">Count Passes</h2>
            </div>
            <GradeBadge grade="Grade 4" difficulty="Easy" />
          </div>
          <p className="next-challenge__reason">
            <strong>Diagnostic Dispatch:</strong> You attempted this challenge recently. Reinforcing comparison boundaries and edge values will solidify your loop traversal foundations.
          </p>
          <button
            type="button"
            className="primary-energy-btn next-challenge__btn"
            onClick={() => onNavigate('/challenges/countpasses')}
          >
            <span>Engage Mission</span>
            <span className="btn-arrow" aria-hidden="true">→</span>
          </button>
        </section>

        {/* Concept Mastery Grid */}
        <section className="mastery-section">
          <div className="section-title-bar">
            <h2 className="section-heading">Concept Breakdown</h2>
            <span className="section-tag" aria-hidden="true">ANALYSIS</span>
          </div>
          <div className="mastery-grid">
            {mockMastery.map((item) => (
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
            <div className="mistakes-empty-seal" aria-hidden="true">CLEARED</div>
            <h3 className="mistakes-empty-title">No Recurring Mistakes Detected</h3>
            <p className="empty-mistakes-text">
              Clean sorcery record. Diagnostic gap patterns are only flagged when identical error categories appear across multiple distinct challenges.
            </p>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
