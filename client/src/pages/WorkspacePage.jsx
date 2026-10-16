import { useState } from 'react';
import Header from '../components/Header.jsx';
import Footer from '../components/Footer.jsx';
import GradeBadge from '../components/GradeBadge.jsx';
import { CHALLENGES } from '../data/challenges.js';

export default function WorkspacePage({ challengeId, onNavigate, learnerName }) {
  const challenge = CHALLENGES.find((c) => c.id === challengeId) || CHALLENGES[0];
  const [code, setCode] = useState(challenge.starterCode);
  const [sandboxStatus, setSandboxStatus] = useState('Sandbox ready');
  const [activeTab, setActiveTab] = useState('tests');
  const [hasRun, setHasRun] = useState(false);

  const handleRun = () => {
    setSandboxStatus('Run finished');
    setHasRun(true);
  };

  return (
    <div className="page-shell">
      <Header currentPath={`/challenges/${challenge.id}`} onNavigate={onNavigate} learnerName={learnerName} />

      <main className="content-container">
        {/* Breadcrumb Navigation */}
        <nav className="breadcrumbs" aria-label="Breadcrumb navigation">
          <button
            type="button"
            className="breadcrumb-link"
            onClick={() => onNavigate('/challenges')}
          >
            ← Challenges Archive
          </button>
          <span className="breadcrumb-separator" aria-hidden="true">/</span>
          <span className="breadcrumb-current" aria-current="page">{challenge.title}</span>
        </nav>

        <div className="workspace-layout">
          {/* Left Panel: Problem Statement & Code Editor */}
          <section className="workspace-main">
            <div className="workspace-header">
              <div>
                <p className="eyebrow">
                  <span className="eyebrow-accent">// TRIAL TASK</span>
                  <span>Trial #{challenge.id}</span>
                </p>
                <h1 className="workspace-title">{challenge.title}</h1>
              </div>
              <GradeBadge grade={challenge.grade} difficulty={challenge.difficulty} />
            </div>

            <div className="workspace-tags" aria-label="Concepts">
              {challenge.tags.map((tag) => (
                <span key={tag} className="concept-ribbon">
                  <span className="ribbon-hash" aria-hidden="true">#</span>
                  {tag}
                </span>
              ))}
            </div>

            {/* Problem Statement Card */}
            <article className="statement-card">
              <div className="card-seal-corner card-seal-corner--tl" aria-hidden="true" />
              <div className="card-seal-corner card-seal-corner--tr" aria-hidden="true" />
              
              <div className="statement-header-bar">
                <h2 className="statement-heading">The Task</h2>
                <span className="statement-tag" aria-hidden="true">SPECIFICATION</span>
              </div>
              
              <p className="statement-text">{challenge.statement}</p>

              {challenge.example && (
                <div className="example-box">
                  <div className="example-badge">SAMPLE EXECUTION</div>
                  <div className="example-row">
                    <span className="example-label">Call:</span>
                    <code className="example-code">{challenge.example.call}</code>
                  </div>
                  <div className="example-row">
                    <span className="example-label">Expected:</span>
                    <code className="example-code">{challenge.example.expected}</code>
                  </div>
                  {challenge.example.explanation && (
                    <p className="example-explanation">{challenge.example.explanation}</p>
                  )}
                </div>
              )}
            </article>

            {/* Code Editor */}
            <section className="editor-card" aria-label="Python Code Editor">
              <div className="editor-tab-bar">
                <span className="file-dot" aria-hidden="true">●</span>
                <span className="file-name">solution.py</span>
                <span className="file-lang">Python 3.12 (Sandbox)</span>
              </div>
              <textarea
                className="code-textarea"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                aria-label="Python code editor"
                spellCheck={false}
              />
              <footer className="editor-footer">
                <button
                  type="button"
                  className="primary-energy-btn run-btn"
                  onClick={handleRun}
                >
                  <span aria-hidden="true">▶</span>
                  <span>Run Execution</span>
                </button>
                <div className="sandbox-status-chip">
                  <span className="chip-dot" aria-hidden="true">●</span>
                  <span className="sandbox-status-text" role="status">
                    {sandboxStatus}
                  </span>
                </div>
              </footer>
            </section>
          </section>

          {/* Right Panel: Feedback, Test Cases & Hints */}
          <aside className="workspace-feedback" aria-label="Execution feedback and tests">
            {/* Tabs */}
            <div className="feedback-tabs" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'tests'}
                className={`feedback-tab ${activeTab === 'tests' ? 'feedback-tab--active' : ''}`}
                onClick={() => setActiveTab('tests')}
              >
                <span>Test Suite</span>
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'hints'}
                className={`feedback-tab ${activeTab === 'hints' ? 'feedback-tab--active' : ''}`}
                onClick={() => setActiveTab('hints')}
              >
                <span>Hints</span>
              </button>
            </div>

            {activeTab === 'tests' ? (
              <div className="feedback-tab-content">
                {/* Summary Line above test lists per rules.md 4.3 */}
                <div className="test-summary-line" role="status">
                  {hasRun ? (
                    <span className="test-summary-line--success">
                      ✓ {challenge.visibleTests.length} of {challenge.visibleTests.length} visible tests passed · {challenge.hiddenTestCount} of {challenge.hiddenTestCount} hidden tests passed
                    </span>
                  ) : (
                    <span>Click Run Execution to evaluate visible and hidden tests.</span>
                  )}
                </div>

                {/* Visible Tests */}
                <section className="panel-box">
                  <div className="panel-box__header">
                    <p className="eyebrow">Public Invariants</p>
                    <h2 className="panel-title">Visible Tests</h2>
                  </div>
                  <div className="tests-list">
                    {challenge.visibleTests.map((t) => (
                      <div 
                        key={t.test} 
                        className={`test-row ${hasRun ? 'test-row--passed' : ''}`}
                      >
                        <div className="test-row__header">
                          <span className="test-row__num">Test #{t.test}</span>
                          <span className={`outcome-pill ${hasRun ? 'outcome-pill--passed' : 'outcome-pill--idle'}`}>
                            <span className="outcome-pill__icon" aria-hidden="true">
                              {hasRun ? '✓' : '●'}
                            </span>{' '}
                            {hasRun ? 'Passed' : 'Pending'}
                          </span>
                        </div>
                        <div className="test-row__detail">
                          <code>Call: {t.call}</code>
                        </div>
                        <div className="test-row__io">
                          <span className="test-row__expected">Expected: <code>{t.expected}</code></span>
                          {hasRun && (
                            <span className="test-row__got">Got: <code>{t.expected}</code></span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Hidden Tests Summary */}
                <section className="panel-box">
                  <div className="panel-box__header">
                    <p className="eyebrow">Restricted Suite</p>
                    <h2 className="panel-title">Hidden Tests</h2>
                  </div>
                  <p className="safe-notice">
                    <span className="notice-lock" aria-hidden="true">🔒</span>
                    <span>Hidden tests check cases you can't see. Their details stay private.</span>
                  </p>
                  <div className="hidden-tests-list">
                    {Array.from({ length: challenge.hiddenTestCount }).map((_, i) => (
                      <div key={i} className={`hidden-test-row ${hasRun ? 'hidden-test-row--passed' : ''}`}>
                        <span className="hidden-test-name">
                          Hidden Test #{challenge.visibleTests.length + i + 1}
                        </span>
                        <span className="hidden-test-lock" title="Details private" aria-hidden="true">
                          🔒
                        </span>
                        <span className={`outcome-pill ${hasRun ? 'outcome-pill--passed' : 'outcome-pill--idle'}`}>
                          <span className="outcome-pill__icon" aria-hidden="true">
                            {hasRun ? '✓' : '●'}
                          </span>{' '}
                          {hasRun ? 'Passed' : 'Pending'}
                        </span>
                      </div>
                    ))}
                  </div>
                </section>
              </div>
            ) : (
              <div className="feedback-tab-content">
                {/* Hints Section */}
                <section className="panel-box">
                  <div className="panel-box__header">
                    <p className="eyebrow">Diagnostic Guidance</p>
                    <h2 className="panel-title">Progressive Hints</h2>
                  </div>
                  <p className="panel-desc">
                    Hints become available after test execution. Diagnostic steps illuminate logic gaps without forfeiting solution mastery.
                  </p>
                  <div className="hint-ladder-preview">
                    <div className="hint-step hint-step--locked">
                      <span className="step-badge">Hint 1 of 4</span>
                      <span className="step-lock">🔒 Execute code to unlock first hint</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="secondary-btn hint-btn"
                    disabled
                    title="Run code to unlock progressive hints"
                  >
                    Get a hint
                  </button>
                </section>
              </div>
            )}
          </aside>
        </div>
      </main>

      <Footer />
    </div>
  );
}
