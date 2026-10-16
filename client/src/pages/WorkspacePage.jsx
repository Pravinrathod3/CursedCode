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
  const [hasRun, setHasRun] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  // Inspector and details state
  const [selectedCaseIndex, setSelectedCaseIndex] = useState(0);
  const [consoleTab, setConsoleTab] = useState('testcase'); // 'testcase' | 'result'
  const [explanation, setExplanation] = useState('');
  const [mistakeTags, setMistakeTags] = useState([]);
  const [limitHit, setLimitHit] = useState(null);

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
        setConsoleTab('testcase');
        setSubmissionId(null);
        setVisibleResults([]);
        setHiddenResults([]);
        setRevealedHints([]);
        setRemainingHints(4);
        setSandboxStatus('Sandbox ready');
        setSelectedCaseIndex(0);
        setExplanation('');
        setMistakeTags([]);
        setLimitHit(null);
      }
    });
    return () => { active = false; };
  }, [challengeId]);

  const handleRun = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setSandboxStatus('Running code in sandbox…');

    try {
      const res = await submitCode(learnerName, challenge.id, code);
      setSubmissionId(res.submission_id);
      setVisibleResults(res.visible || []);
      setHiddenResults(res.hidden || []);
      setExplanation(res.explanation || '');
      setMistakeTags(res.mistake_tags || []);
      setLimitHit(res.limit || null);
      setHasRun(true);
      setConsoleTab('result');

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
        if (prev.some((h) => h.index === res.hint_index)) return prev;
        return [...prev, { index: res.hint_index, text: res.hint }];
      });
      if (res.remaining !== undefined) {
        setRemainingHints(res.remaining);
      } else {
        setRemainingHints((prev) => Math.max(0, prev - 1));
      }
    } catch {
      // Ignore or maintain state
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

  // Inspector details for active visible test
  const visibleTestsList = challenge.visibleTests || [];
  const selectedCase = visibleTestsList[selectedCaseIndex] || visibleTestsList[0];
  const selectedResult = visibleResults.find((r) => r.test === (selectedCase?.test || selectedCaseIndex + 1)) || visibleResults[selectedCaseIndex];
  const selectedOutcome = selectedResult ? selectedResult.outcome : null;
  const selectedDurationMs = selectedResult?.duration_ms;
  const selectedGot = selectedResult && selectedResult.got !== undefined && selectedResult.got !== null
    ? selectedResult.got
    : (selectedOutcome === 'passed' ? selectedCase?.expected : '');

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

        {/* Wireframe Bar */}
        <div className="schematic-section-bar">
          <div className="schematic-section-bar__left">
            <span># WORKBENCH // LEETCODE_WORKSPACE</span>
            <span className="schematic-section-bar__tag">[ DUAL-PANE SPLIT VIEW ]</span>
          </div>
          <span className="schematic-section-bar__tag">FIG. 01: PROBLEM SPEC &amp; DOCKED RUNNER</span>
        </div>

        {/* LeetCode 2-Column Split Layout */}
        <div className="leetcode-layout">
          {/* LEFT COLUMN: Problem Statement, Theory, Examples, Hints */}
          <div className="leetcode-left-panel">
            {/* Box 1: Problem Header & Statement */}
            <article className="schematic-card">
              <div className="schematic-card-header">
                <h2 className="schematic-card-header__title">
                  <span aria-hidden="true">▶</span> [ PROBLEM STATEMENT ]
                </h2>
                <span className="schematic-card-header__tag">[ ID: #{challenge.id} ]</span>
              </div>

              <div className="schematic-theory-row" style={{ padding: '0 0 12px', borderBottom: '1px solid rgba(224, 36, 58, 0.15)' }}>
                <div className="schematic-theory-meta">
                  <GradeBadge grade={challenge.grade} difficulty={challenge.difficulty} />
                  {challenge.function_signature && (
                    <code style={{ fontSize: '12px' }}>{challenge.function_signature}</code>
                  )}
                </div>
                <div className="workspace-tags" style={{ margin: '6px 0 0' }}>
                  {(challenge.tags || []).map((tag) => (
                    <span key={tag} className="concept-ribbon">
                      <span className="ribbon-hash" aria-hidden="true">#</span>
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              <p className="schematic-text" style={{ marginTop: '14px', lineHeight: 1.65 }}>
                {challenge.statement}
              </p>
            </article>

            {/* Box 2: Example Vectors */}
            {challenge.example && (
              <article className="schematic-card">
                <div className="schematic-card-header">
                  <h2 className="schematic-card-header__title">
                    <span aria-hidden="true">▶</span> [ EXAMPLE ]
                  </h2>
                  <span className="schematic-card-header__tag">1 VECTOR DEFINED</span>
                </div>
                <div className="schematic-example-box">
                  <div className="schematic-example-row">
                    <span className="schematic-example-label">INPUT / CALL:</span>
                    <code>{challenge.example.call}</code>
                  </div>
                  <div className="schematic-example-row">
                    <span className="schematic-example-label">EXPECTED:</span>
                    <code>{challenge.example.expected}</code>
                  </div>
                  {challenge.example.explanation && (
                    <p className="schematic-text" style={{ fontSize: '12px', marginTop: '6px' }}>
                      {challenge.example.explanation}
                    </p>
                  )}
                </div>
              </article>
            )}

            {/* Box 3: Hint Assistant Ladder */}
            <article className="schematic-card">
              <div className="schematic-card-header">
                <h2 className="schematic-card-header__title">
                  <span aria-hidden="true">▶</span> [ HINT ASSISTANT ]
                </h2>
                <span className="schematic-card-header__tag">
                  {revealedHints.length > 0 ? `[ HINT ${revealedHints.length}/4 UNLOCKED ]` : '[ BOT READY ]'}
                </span>
              </div>
              <div className="schematic-bot-hint">
                <div className="schematic-bot-avatar">
                  <span aria-hidden="true">🤖</span>
                  [ BOT ]
                </div>
                <div className="schematic-bot-content">
                  {revealedHints.length === 0 ? (
                    <p className="schematic-text" style={{ fontSize: '12.5px' }}>
                      {hasRun
                        ? 'Diagnostic guidance available. Ask the assistant to inspect your logical assumptions.'
                        : 'Execute code in the sandbox to unlock progressive diagnostic hints.'}
                    </p>
                  ) : (
                    revealedHints.map((h) => (
                      <div key={h.index} style={{ marginBottom: '6px' }}>
                        <span className="step-badge" style={{ marginRight: '8px' }}>Hint {h.index} of 4</span>
                        <span className="schematic-text" style={{ fontSize: '12.5px' }}>{h.text}</span>
                      </div>
                    ))
                  )}

                  {remainingHints > 0 && revealedHints.length < 4 ? (
                    <button
                      type="button"
                      className="secondary-btn hint-btn"
                      style={{ alignSelf: 'flex-start', padding: '6px 14px', fontSize: '12px', marginTop: '6px' }}
                      disabled={!hasRun || !submissionId || isFetchingHint}
                      onClick={handleGetHint}
                    >
                      {isFetchingHint ? 'Fetching hint…' : `Ask bot for hint (${remainingHints} remaining)`}
                    </button>
                  ) : revealedHints.length >= 4 ? (
                    <p className="schematic-text" style={{ fontSize: '12px', fontWeight: 600 }}>
                      All 4 hints unlocked. Analyze the hints and submit a revised solution.
                    </p>
                  ) : null}
                </div>
              </div>
            </article>
          </div>

          {/* RIGHT COLUMN: Code Editor + Docked LeetCode Console */}
          <div className="leetcode-right-panel">
            {/* Box 1: Code Editor */}
            <div className="schematic-editor-container">
              <div className="schematic-editor-topbar">
                <div className="schematic-editor-title">
                  <span className="file-dot" aria-hidden="true">●</span>
                  <span>[ PYTHON 3 ]</span>
                  <span style={{ color: 'var(--color-muted)', fontSize: '11px' }}>solution.py</span>
                </div>
                <div className="schematic-editor-actions">
                  <button
                    type="button"
                    className="primary-energy-btn schematic-run-btn"
                    onClick={handleRun}
                    disabled={isRunning}
                  >
                    <span aria-hidden="true">▶</span>
                    <span>{isRunning ? 'RUNNING…' : 'RUN'}</span>
                  </button>
                </div>
              </div>

              <textarea
                className="code-textarea"
                style={{ minHeight: '280px', height: '300px', borderRadius: 0, border: 'none' }}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                aria-label="Python code editor"
                spellCheck={false}
              />

              <div className="schematic-editor-footer">
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span className="chip-dot" aria-hidden="true">●</span>
                  <span>[ STATUS: {sandboxStatus.toUpperCase()} ]</span>
                </div>
                <span>LN {code.split('\n').length}, COL 1 · UTF-8</span>
              </div>
            </div>

            {/* Box 2: LeetCode Console (Testcase & Test Result) */}
            <div className="leetcode-console">
              {/* Console Tabs Header */}
              <div className="leetcode-console-tabs">
                <div className="leetcode-tabs-group" role="tablist">
                  <button
                    type="button"
                    role="tab"
                    aria-selected={consoleTab === 'testcase'}
                    className={`leetcode-console-tab ${consoleTab === 'testcase' ? 'leetcode-console-tab--active' : ''}`}
                    onClick={() => setConsoleTab('testcase')}
                  >
                    <span>☑</span> Testcase
                  </button>
                  <button
                    type="button"
                    role="tab"
                    aria-selected={consoleTab === 'result'}
                    className={`leetcode-console-tab ${consoleTab === 'result' ? 'leetcode-console-tab--active' : ''}`}
                    onClick={() => setConsoleTab('result')}
                  >
                    <span>▶</span> Test Result
                    {hasRun && (
                      <span style={{
                        fontSize: '10px',
                        padding: '1px 6px',
                        borderRadius: '4px',
                        backgroundColor: allPassed ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)',
                        color: allPassed ? '#22c55e' : '#ef4444'
                      }}>
                        {allPassed ? 'Accepted' : `${visiblePassed + hiddenPassed}/${visibleTotal + hiddenTotal}`}
                      </span>
                    )}
                  </button>
                </div>
                <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)' }}>
                  CONSOLE
                </span>
              </div>

              {/* Console Body */}
              <div className="leetcode-console-body">
                {consoleTab === 'testcase' ? (
                  /* Testcase Tab */
                  <>
                    <div className="leetcode-case-pills" role="tablist">
                      {visibleTestsList.map((t, idx) => (
                        <button
                          key={t.test || idx}
                          type="button"
                          className={`leetcode-case-pill ${selectedCaseIndex === idx ? 'leetcode-case-pill--active' : ''}`}
                          onClick={() => setSelectedCaseIndex(idx)}
                        >
                          Case {idx + 1}
                        </button>
                      ))}
                    </div>

                    {selectedCase && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
                        <div className="leetcode-io-block">
                          <span className="leetcode-io-label">Call / Input:</span>
                          <code className="leetcode-io-value">{selectedCase.call}</code>
                        </div>
                        <div className="leetcode-io-block">
                          <span className="leetcode-io-label">Expected Output:</span>
                          <code className="leetcode-io-value">{selectedCase.expected}</code>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  /* Test Result Tab */
                  <>
                    {!hasRun ? (
                      <div style={{ padding: '24px 12px', textAlign: 'center', color: 'var(--color-muted)', fontFamily: 'var(--font-mono)', fontSize: '13px' }}>
                        Please run your code first to see test results.
                      </div>
                    ) : (
                      <>
                        {/* LeetCode Result Banner */}
                        <div className={`leetcode-result-banner ${allPassed ? 'leetcode-result-banner--passed' : 'leetcode-result-banner--failed'}`}>
                          <div>
                            <span style={{ fontSize: '15px' }}>
                              {allPassed ? '✓ Accepted' : (limitHit ? `⚠ ${limitHit.toUpperCase()} Limit Exceeded` : '✕ Wrong Answer')}
                            </span>
                            {selectedDurationMs !== undefined && (
                              <span style={{ fontSize: '12px', fontWeight: 400, marginLeft: '12px', color: 'var(--color-muted)' }}>
                                Runtime: {selectedDurationMs} ms
                              </span>
                            )}
                          </div>
                          <span>
                            Passed {visiblePassed + hiddenPassed} / {visibleTotal + hiddenTotal}
                          </span>
                        </div>

                        {/* Case Pills for Result View */}
                        <div className="leetcode-case-pills">
                          {visibleTestsList.map((t, idx) => {
                            const res = visibleResults.find((r) => r.test === (t.test || idx + 1)) || visibleResults[idx];
                            const outcome = res ? res.outcome : null;
                            const isPassed = outcome === 'passed';
                            const isFailed = outcome && outcome !== 'passed';
                            return (
                              <button
                                key={`res-case-${idx}`}
                                type="button"
                                className={`leetcode-case-pill ${selectedCaseIndex === idx ? 'leetcode-case-pill--active' : ''}`}
                                onClick={() => setSelectedCaseIndex(idx)}
                              >
                                <span style={{ color: isPassed ? '#22c55e' : (isFailed ? '#ef4444' : 'inherit'), fontWeight: 'bold' }}>
                                  {isPassed ? '●' : (isFailed ? '●' : '○')}
                                </span>
                                Case {idx + 1}
                              </button>
                            );
                          })}
                        </div>

                        {/* Inspector for selected case in Result tab */}
                        {selectedCase && (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <div className="leetcode-io-block">
                              <span className="leetcode-io-label">Input / Call:</span>
                              <code className="leetcode-io-value">{selectedCase.call}</code>
                            </div>
                            <div className="leetcode-io-block">
                              <span className="leetcode-io-label">Output (Got):</span>
                              <code className="leetcode-io-value" style={{ color: selectedOutcome === 'passed' ? '#22c55e' : '#ef4444' }}>
                                {selectedGot !== '' && selectedGot !== undefined ? selectedGot : (selectedOutcome || 'N/A')}
                              </code>
                            </div>
                            <div className="leetcode-io-block">
                              <span className="leetcode-io-label">Expected:</span>
                              <code className="leetcode-io-value">{selectedCase.expected}</code>
                            </div>
                          </div>
                        )}

                        {/* Validation Suite Matrix */}
                        <div style={{ marginTop: '8px' }}>
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-muted)', display: 'block', marginBottom: '6px' }}>
                            [ VALIDATION MATRIX: {visibleTotal} VISIBLE + {hiddenTotal} RESTRICTED VECTORS ]
                          </span>
                          <div className="schematic-matrix-grid">
                            {visibleTestsList.map((t, idx) => {
                              const res = visibleResults.find((r) => r.test === (t.test || idx + 1)) || visibleResults[idx];
                              const outcome = res ? res.outcome : null;
                              const isPassed = outcome === 'passed';
                              const isFailed = outcome && outcome !== 'passed';
                              return (
                                <div
                                  key={`grid-vis-${idx}`}
                                  className={`schematic-matrix-cell ${isPassed ? 'schematic-matrix-cell--passed' : (isFailed ? 'schematic-matrix-cell--failed' : '')}`}
                                  onClick={() => setSelectedCaseIndex(idx)}
                                  style={{ cursor: 'pointer' }}
                                >
                                  <span>Case {idx + 1}</span>
                                  <span style={{ color: isPassed ? '#22c55e' : (isFailed ? '#ef4444' : 'var(--color-muted)'), fontWeight: 'bold' }}>
                                    {isPassed ? '✓' : (isFailed ? '✗' : '●')}
                                  </span>
                                </div>
                              );
                            })}
                            {Array.from({ length: hiddenTotal }).map((_, i) => {
                              const res = hiddenResults[i];
                              const outcome = res ? res.outcome : null;
                              const isPassed = outcome === 'passed';
                              const isFailed = outcome && outcome !== 'passed';
                              const num = visibleTotal + i + 1;
                              return (
                                <div
                                  key={`grid-hid-${i}`}
                                  className={`schematic-matrix-cell ${isPassed ? 'schematic-matrix-cell--passed' : (isFailed ? 'schematic-matrix-cell--failed' : '')}`}
                                >
                                  <span>Case {num} 🔒</span>
                                  <span style={{ color: isPassed ? '#22c55e' : (isFailed ? '#ef4444' : 'var(--color-muted)'), fontWeight: 'bold' }}>
                                    {isPassed ? '✓' : (isFailed ? '✗' : '●')}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        {/* STDOUT / Diagnostic Notes */}
                        <div className="schematic-terminal" style={{ marginTop: '8px' }}>
                          <div className="schematic-terminal-header">
                            <span>[ Sandbox Logs &amp; Diagnostics ]</span>
                            <span>[ STATUS: {sandboxStatus} ]</span>
                          </div>
                          {explanation && (
                            <p className={`schematic-terminal-line ${allPassed ? 'schematic-terminal-line--success' : 'schematic-terminal-line--error'}`}>
                              &gt; {explanation}
                            </p>
                          )}
                          {mistakeTags.length > 0 && (
                            <p className="schematic-terminal-line schematic-terminal-line--warn">
                              &gt; diagnostic tags: {mistakeTags.join(', ')}
                            </p>
                          )}
                          {limitHit && (
                            <p className="schematic-terminal-line schematic-terminal-line--error">
                              &gt; resource limit triggered: {limitHit} threshold exceeded
                            </p>
                          )}
                        </div>
                      </>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Blueprint Footer */}
        <div className="schematic-blueprint-footer">
          [ ARCHITECTURAL SCHEMATIC WIREFRAME ] · NOTEBOOK DRAWING SPECIFICATION COMPLIANT · CURSEDCODE BLUEPRINT SYSTEM // 2025
        </div>
      </main>

      <Footer />
    </div>
  );
}
