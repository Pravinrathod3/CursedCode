import { useState, useEffect } from 'react';
import Header from '../components/Header.jsx';
import Footer from '../components/Footer.jsx';
import GradeBadge from '../components/GradeBadge.jsx';
import { CHALLENGES } from '../data/challenges.js';
import { getChallenge, submitCode, getHint } from '../services/api.js';

function formatOutcome(outcome) {
  switch (outcome) {
    case 'passed':
      return 'Passed';
    case 'wrong_output':
      return 'Wrong output';
    case 'runtime_error':
      return 'Runtime error';
    case 'timeout':
      return 'Timeout';
    default:
      return 'Pending';
  }
}

function getOutcomeIcon(outcome) {
  switch (outcome) {
    case 'passed':
      return '✓';
    case 'wrong_output':
      return '✕';
    case 'runtime_error':
      return '⚠';
    case 'timeout':
      return '⏱';
    default:
      return '●';
  }
}

export default function WorkspacePage({ challengeId, onNavigate, learnerName }) {
  const initialChallenge = CHALLENGES.find((c) => c.id === challengeId) || CHALLENGES[0];
  const [challenge, setChallenge] = useState(initialChallenge);
  const [code, setCode] = useState(initialChallenge.starterCode || '');
  const [sandboxStatus, setSandboxStatus] = useState('Sandbox ready');
  const [activeTab, setActiveTab] = useState('tests');
  const [hasRun, setHasRun] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  // Execution state
  const [submissionId, setSubmissionId] = useState(null);
  const [visibleResults, setVisibleResults] = useState([]);
  const [hiddenResults, setHiddenResults] = useState([]);

  // Hints state
  const [revealedHints, setRevealedHints] = useState([]);
  const [isFetchingHint, setIsFetchingHint] = useState(false);
  const [remainingHints, setRemainingHints] = useState(4);

  // Fetch challenge details from backend
  useEffect(() => {
    let active = true;
    getChallenge(challengeId).then((data) => {
      if (active && data) {
        setChallenge(data);
        const starter = data.starterCode || data.starter_code || '';
        setCode(starter);
        setHasRun(false);
        setSubmissionId(null);
        setVisibleResults([]);
        setHiddenResults([]);
        setRevealedHints([]);
        setRemainingHints(4);
        setSandboxStatus('Sandbox ready');
      }
    });
    return () => { active = false; };
  }, [challengeId]);

  const handleRun = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setSandboxStatus('Running your code in the sandbox');

    try {
      const res = await submitCode(learnerName, challenge.id, code);
      setSubmissionId(res.submission_id);
      setVisibleResults(res.visible || []);
      setHiddenResults(res.hidden || []);
      setHasRun(true);

      if (res.limit) {
        setSandboxStatus(`Stopped: ${res.limit} limit reached`);
      } else {
        setSandboxStatus('Run finished');
      }
    } catch (err) {
      console.error('Code execution failed:', err);
      setSandboxStatus('Something went wrong running your code. Please try again.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleGetHint = async () => {
    if (!submissionId || isFetchingHint) return;
    setIsFetchingHint(true);

    try {
      const res = await getHint(submissionId);
      setRevealedHints((prev) => {
        // Avoid duplicate hints
        if (prev.some((h) => h.index === res.hint_index)) return prev;
        return [...prev, { index: res.hint_index, text: res.hint }];
      });
      if (res.remaining !== undefined) {
        setRemainingHints(res.remaining);
      } else {
        setRemainingHints((prev) => Math.max(0, prev - 1));
      }
    } catch {
      // Ignore or show neutral message
    } finally {
      setIsFetchingHint(false);
    }
  };

  // Compute test tallies
  const visibleTotal = challenge.visibleTests ? challenge.visibleTests.length : 0;
  const visiblePassed = visibleResults.filter((r) => r.outcome === 'passed').length;
  const hiddenTotal = challenge.hiddenTestCount || (hiddenResults.length ? hiddenResults.length : 5);
  const hiddenPassed = hiddenResults.filter((r) => r.outcome === 'passed').length;
  const allPassed = hasRun && (visiblePassed === visibleTotal && hiddenPassed === hiddenTotal);

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
              {(challenge.tags || []).map((tag) => (
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
                  disabled={isRunning}
                >
                  <span aria-hidden="true">▶</span>
                  <span>{isRunning ? 'Running…' : 'Run Execution'}</span>
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
                    <span className={allPassed ? 'test-summary-line--success' : ''}>
                      {allPassed ? '✓ ' : ''}{visiblePassed} of {visibleTotal} visible tests passed · {hiddenPassed} of {hiddenTotal} hidden tests passed
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
                    {(challenge.visibleTests || []).map((t, idx) => {
                      const res = visibleResults.find((r) => r.test === (t.test || idx + 1)) || visibleResults[idx];
                      const outcome = res ? res.outcome : (hasRun ? 'wrong_output' : null);
                      const isPassed = outcome === 'passed';
                      const gotVal = res && res.got !== undefined && res.got !== null
                        ? res.got
                        : (isPassed ? t.expected : '');

                      return (
                        <div 
                          key={t.test || idx} 
                          className={`test-row ${hasRun && isPassed ? 'test-row--passed' : ''}`}
                        >
                          <div className="test-row__header">
                            <span className="test-row__num">Test #{t.test || idx + 1}</span>
                            <span className={`outcome-pill ${outcome ? `outcome-pill--${outcome}` : 'outcome-pill--idle'}`}>
                              <span className="outcome-pill__icon" aria-hidden="true">
                                {getOutcomeIcon(outcome)}
                              </span>{' '}
                              {formatOutcome(outcome)}
                            </span>
                          </div>
                          <div className="test-row__detail">
                            <code>Call: {t.call}</code>
                          </div>
                          <div className="test-row__io">
                            <span className="test-row__expected">Expected: <code>{t.expected}</code></span>
                            {hasRun && gotVal !== '' && (
                              <span className="test-row__got">Got: <code>{gotVal}</code></span>
                            )}
                          </div>
                        </div>
                      );
                    })}
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
                    {Array.from({ length: hiddenTotal }).map((_, i) => {
                      const res = hiddenResults[i];
                      const outcome = res ? res.outcome : (hasRun ? 'wrong_output' : null);
                      const isPassed = outcome === 'passed';

                      return (
                        <div key={i} className={`hidden-test-row ${hasRun && isPassed ? 'hidden-test-row--passed' : ''}`}>
                          <span className="hidden-test-name">
                            Hidden Test #{(challenge.visibleTests ? challenge.visibleTests.length : 0) + i + 1}
                          </span>
                          <span className="hidden-test-lock" title="Details private" aria-hidden="true">
                            🔒
                          </span>
                          <span className={`outcome-pill ${outcome ? `outcome-pill--${outcome}` : 'outcome-pill--idle'}`}>
                            <span className="outcome-pill__icon" aria-hidden="true">
                              {getOutcomeIcon(outcome)}
                            </span>{' '}
                            {formatOutcome(outcome)}
                          </span>
                        </div>
                      );
                    })}
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
                    {revealedHints.length === 0 ? (
                      <div className="hint-step hint-step--locked">
                        <span className="step-badge">Hint 1 of 4</span>
                        <span className="step-lock">
                          {hasRun ? '🔒 Ready to reveal diagnostic hint' : '🔒 Execute code to unlock first hint'}
                        </span>
                      </div>
                    ) : (
                      revealedHints.map((h) => (
                        <div key={h.index} className="hint-step--revealed">
                          <span className="step-badge">Hint {h.index} of 4</span>
                          <span className="step-text">{h.text}</span>
                        </div>
                      ))
                    )}
                  </div>

                  {remainingHints > 0 && revealedHints.length < 4 ? (
                    <button
                      type="button"
                      className="secondary-btn hint-btn"
                      disabled={!hasRun || !submissionId || isFetchingHint}
                      onClick={handleGetHint}
                      title={hasRun ? 'Reveal next progressive hint' : 'Run code to unlock progressive hints'}
                    >
                      {isFetchingHint ? 'Fetching hint…' : 'Get a hint'}
                    </button>
                  ) : (
                    <p className="panel-desc" style={{ marginTop: '12px', fontWeight: 600 }}>
                      That's all the hints. You're closer than you think. Try another attempt.
                    </p>
                  )}
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
