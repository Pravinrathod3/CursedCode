import { useState, useEffect, useRef } from 'react';
import Header from '../components/Header.jsx';
import Footer from '../components/Footer.jsx';
import GradeBadge from '../components/GradeBadge.jsx';
import { CHALLENGES } from '../data/challenges.js';
import { getChallenge, submitCode, getHint } from '../services/api.js';
import botAvatarImg from '../assets/hint_bot.webp';

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

function detectSuspectLine(codeText, mistakeTags = [], visibleResults = [], explanation = '') {
  const lines = (codeText || '').split('\n');
  if (lines.length <= 1) return 1;

  // 1. Try to find explicit line number from explanation or traceback
  const lineMatch = (explanation || '').match(/line\s+(\d+)/i);
  if (lineMatch) {
    const parsed = parseInt(lineMatch[1], 10);
    if (!isNaN(parsed) && parsed >= 1 && parsed <= lines.length) {
      return parsed;
    }
  }

  // 2. Check mistake tags
  if (mistakeTags.includes('print_not_return')) {
    const printIdx = lines.findIndex((l) => /print\s*\(/.test(l));
    if (printIdx !== -1) return printIdx + 1;
  }

  if (mistakeTags.includes('mutates_input')) {
    const mutIdx = lines.findIndex((l) => /\.(sort|append|extend|insert|remove|pop|clear|reverse)\s*\(|del\s+/.test(l));
    if (mutIdx !== -1) return mutIdx + 1;
  }

  if (mistakeTags.includes('unhandled_short_input')) {
    const sliceIdx = lines.findIndex((l) => /\[.*\]/.test(l) && !l.trim().startsWith('def '));
    if (sliceIdx !== -1) return sliceIdx + 1;
  }

  if (mistakeTags.includes('boundary_comparison') || mistakeTags.includes('off_by_one')) {
    const loopOrCompIdx = lines.findIndex((l) => /(for|while|if)\s+.*(range|<=|>=|<|>|==)/.test(l));
    if (loopOrCompIdx !== -1) return loopOrCompIdx + 1;
  }

  // 3. Check for return statement
  const returnIdx = lines.findIndex((l) => /^\s*return\b/.test(l));
  if (returnIdx !== -1) return returnIdx + 1;

  // 4. Default to line 2 (first line of function body) if exists
  return lines.length > 1 ? 2 : 1;
}

function getNaturalLanguageDiagnostic({ mistakeTags, visibleResults, explanation, targetLine, codeText }) {
  const lines = (codeText || '').split('\n');
  const codeLine = lines[targetLine - 1] || '';
  const failedTest = (visibleResults || []).find((r) => r.outcome && r.outcome !== 'passed');

  if (failedTest?.outcome === 'runtime_error') {
    return {
      title: 'RUNTIME ERROR',
      intro: 'There is something wrong here...',
      detail: 'A runtime error occurred when executing this line or block. Check for variable naming typos, missing attributes, or invalid type operations.',
      lineSnippet: codeLine
    };
  }

  if (failedTest?.outcome === 'timeout') {
    return {
      title: 'TIMEOUT / LOOP DETECTED',
      intro: 'There is something wrong here...',
      detail: 'Execution timed out. Check if a loop or condition on this line fails to terminate or update its state.',
      lineSnippet: codeLine
    };
  }

  if (mistakeTags.includes('print_not_return')) {
    return {
      title: 'PRINT VS RETURN',
      intro: 'There is something wrong here...',
      detail: 'Your function appears to be printing the output instead of returning it. The evaluator checks the returned value.',
      lineSnippet: codeLine
    };
  }

  if (mistakeTags.includes('mutates_input')) {
    return {
      title: 'MUTATED INPUT ARGUMENT',
      intro: 'There is something wrong here...',
      detail: 'This line mutates the input argument directly. In algorithmic challenges, avoid modifying the caller\'s original collection unless asked.',
      lineSnippet: codeLine
    };
  }

  if (mistakeTags.includes('unhandled_short_input')) {
    return {
      title: 'UNHANDLED EDGE CASE',
      intro: 'There is something wrong here...',
      detail: 'This code seems to stumble on short or boundary inputs (like an empty list or single element). Add a guard condition before indexing.',
      lineSnippet: codeLine
    };
  }

  if (mistakeTags.includes('boundary_comparison') || mistakeTags.includes('off_by_one')) {
    return {
      title: 'BOUNDARY CHECK / OFF BY ONE',
      intro: 'There is something wrong here...',
      detail: 'The boundary comparison or loop range condition seems slightly off here. Verify if it should be inclusive or exclusive (e.g. < vs <=).',
      lineSnippet: codeLine
    };
  }

  if (failedTest && failedTest.got !== undefined && failedTest.expected !== undefined) {
    return {
      title: 'OUTPUT DISCREPANCY',
      intro: 'There is something wrong here...',
      detail: `Your code returned "${failedTest.got}" instead of "${failedTest.expected}" on test call "${failedTest.call || 'input'}". Re-check this line's computation.`,
      lineSnippet: codeLine
    };
  }

  return {
    title: 'LOGICAL DISCREPANCY',
    intro: 'There is something wrong here...',
    detail: explanation || 'The test runner encountered an unexpected result. Check your logic and variable updates on this line.',
    lineSnippet: codeLine
  };
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
  const [patchApplied, setPatchApplied] = useState(false);

  // Line tracking and floating bot state
  const [activeLine, setActiveLine] = useState(1);
  const [targetLine, setTargetLine] = useState(1);
  const [botActive, setBotActive] = useState(false);
  const [botMode, setBotMode] = useState('hint'); // 'hint' | 'error'
  const [scrollTop, setScrollTop] = useState(0);

  const textareaRef = useRef(null);
  const gutterRef = useRef(null);

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
        setPatchApplied(false);
        setBotActive(false);
        setActiveLine(1);
        setTargetLine(1);
        setScrollTop(0);
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
    setPatchApplied(false);
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
    if (isFetchingHint) return;
    setIsFetchingHint(true);

    try {
      let currentSubId = submissionId;
      if (!currentSubId) {
        setSandboxStatus('Evaluating code for hints…');
        const submitRes = await submitCode(learnerName, challenge.id, code);
        currentSubId = submitRes.submission_id;
        setSubmissionId(currentSubId);
        setVisibleResults(submitRes.visible || []);
        setHiddenResults(submitRes.hidden || []);
        setExplanation(submitRes.explanation || '');
        setMistakeTags(submitRes.mistake_tags || []);
        setLimitHit(submitRes.limit || null);
        setHasRun(true);
        setSandboxStatus('Code evaluated');
      }

      const res = await getHint(currentSubId);
      setRevealedHints((prev) => {
        if (prev.some((h) => h.index === res.hint_index)) return prev;
        return [...prev, { index: res.hint_index, text: res.hint, code_patch: res.code_patch }];
      });
      if (res.code_patch) {
        setPatchApplied(false);
      }
      if (res.remaining !== undefined) {
        setRemainingHints(res.remaining);
      } else {
        setRemainingHints((prev) => Math.max(0, prev - 1));
      }
    } catch (err) {
      console.error('Failed to get hint:', err);
      setSandboxStatus('Could not fetch hint. Please verify connection and try again.');
    } finally {
      setIsFetchingHint(false);
    }
  };

  const handleApplyCodePatch = (patch) => {
    if (!patch) return;
    const patched = patch.patched_code || (
      code.split('\n').map((line, idx) => (idx + 1 === patch.target_line ? patch.replacement_snippet : line)).join('\n')
    );
    setCode(patched);
    if (patch.target_line) {
      setTargetLine(patch.target_line);
    }
    setPatchApplied(true);
    if (textareaRef.current && patch.target_line) {
      const targetScrollTop = Math.max(0, (patch.target_line - 1) * 24 - 80);
      textareaRef.current.scrollTo({ top: targetScrollTop, behavior: 'smooth' });
    }
  };

  // Compute test tallies
  const visibleTotal = challenge.visibleTests ? challenge.visibleTests.length : 0;
  const visiblePassed = visibleResults.filter((r) => r.outcome === 'passed').length;
  const hiddenTotal = challenge.hiddenTestCount || (hiddenResults.length ? hiddenResults.length : 5);
  const hiddenPassed = hiddenResults.filter((r) => r.outcome === 'passed').length;
  const allPassed = hasRun && (visiblePassed === visibleTotal && hiddenPassed === hiddenTotal);
  const hasFailedTests = hasRun && !allPassed;

  // Diagnostic calculations
  const suspectErrorLine = detectSuspectLine(code, mistakeTags, visibleResults, explanation);
  const botDiagnostic = getNaturalLanguageDiagnostic({
    mistakeTags,
    visibleResults,
    explanation,
    targetLine,
    codeText: code,
  });

  const latestHint = revealedHints.length > 0 ? revealedHints[revealedHints.length - 1] : null;
  const codeLines = code.split('\n');
  const lineCount = Math.max(1, codeLines.length);

  // Deploy bot: animate to error line or active line
  const handleDeployBot = (forcedMode) => {
    const mode = forcedMode || (hasFailedTests ? 'error' : 'hint');
    setBotMode(mode);

    let target = 1;
    if (mode === 'error') {
      target = suspectErrorLine;
    } else {
      target = activeLine || (codeLines.length > 1 ? 2 : 1);
      // Automatically unlock first hint if available and none unlocked yet
      if (revealedHints.length === 0 && !isFetchingHint) {
        handleGetHint();
      }
    }

    setTargetLine(target);
    setBotActive(true);

    // Smooth scroll the code editor so the target line and hovering bot are in view
    if (textareaRef.current) {
      const targetScrollTop = Math.max(0, (target - 1) * 24 - 80);
      textareaRef.current.scrollTo({ top: targetScrollTop, behavior: 'smooth' });
    }
  };

  const handleCursorChange = (e) => {
    const el = e.target;
    const pos = el.selectionStart || 0;
    const linesBefore = el.value.substring(0, pos).split('\n');
    const lineNum = Math.max(1, linesBefore.length);
    setActiveLine(lineNum);
  };

  const handleScroll = (e) => {
    const st = e.target.scrollTop;
    setScrollTop(st);
    if (gutterRef.current) {
      gutterRef.current.scrollTop = st;
    }
  };

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
              {challenge.constraints && (
                <div style={{ marginTop: '12px', padding: '10px', background: 'rgba(224, 36, 58, 0.06)', border: '1px dashed rgba(224, 36, 58, 0.25)', borderRadius: '6px', fontSize: '12px' }}>
                  <div style={{ display: 'flex', gap: '12px', marginBottom: '8px', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', color: 'rgba(224, 36, 58, 0.7)' }}>
                    {challenge.constraints.time_limit_ms && <span><span aria-hidden="true">⏱</span> Time Limit: {challenge.constraints.time_limit_ms}ms</span>}
                    {challenge.constraints.memory_limit_mb && <span><span aria-hidden="true">💾</span> Memory: {challenge.constraints.memory_limit_mb}MB</span>}
                    {challenge.constraints.time_complexity && <span><span aria-hidden="true">⚡</span> Complexity: {challenge.constraints.time_complexity}</span>}
                  </div>
                  {challenge.constraints.input_constraints && (
                    <div style={{ fontSize: '12px', color: 'var(--color-muted)', lineHeight: 1.5 }}>
                      <span style={{ fontWeight: 'bold', color: 'rgba(224, 36, 58, 0.9)' }}>Input Constraints:</span> {challenge.constraints.input_constraints}
                    </div>
                  )}
                </div>
              )}
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

            {/* Box 3: Interactive Hint Assistant Station */}
            <article className="schematic-card">
              <div className="schematic-card-header">
                <h2 className="schematic-card-header__title">
                  <span aria-hidden="true">▶</span> [ HINT ASSISTANT ]
                </h2>
                <span className="schematic-card-header__tag">
                  {botActive
                    ? `[ HOVERING AT LN ${targetLine} ]`
                    : hasFailedTests
                    ? '[ ERROR SUSPECT DETECTED ]'
                    : revealedHints.length > 0
                    ? `[ HINT ${revealedHints.length}/4 UNLOCKED ]`
                    : '[ READY ]'}
                </span>
              </div>

              <div className="schematic-bot-station">
                <button
                  type="button"
                  className={`bot-station-deploy-btn ${botActive ? 'bot-station-deploy-btn--active' : ''} ${hasFailedTests ? 'bot-station-deploy-btn--error' : ''}`}
                  onClick={() => {
                    if (botActive) {
                      setBotActive(false);
                    } else {
                      handleDeployBot();
                    }
                  }}
                >
                  <div className="bot-station-avatar-wrap">
                    <img src={botAvatarImg} alt="Bot Avatar" className="bot-station-img" />
                    <span className="bot-station-avatar-beacon" />
                  </div>
                  <div className="bot-station-info">
                    <span className="bot-station-title">
                      {botActive
                        ? `[ DISMISS BOT FROM LINE ${targetLine} ]`
                        : hasFailedTests
                        ? `[ ⚠ HOVER BOT TO ERROR LINE (${suspectErrorLine}) ]`
                        : `[ 💡 HOVER BOT TO ACTIVE LINE (${activeLine}) ]`}
                    </span>
                    <span className="bot-station-subtitle">
                      {botActive
                        ? 'Click to dock assistant back to station'
                        : hasFailedTests
                        ? 'Inspect failure: Hover bot to the suspect error line'
                        : 'Deploy assistant to cursor line for step-by-step guidance'}
                    </span>
                  </div>
                  <span className="bot-station-arrow">{botActive ? '✕' : '➔'}</span>
                </button>

                {/* Progressive Hint Ladders & Pills */}
                <div className="bot-station-ladder">
                  <div className="bot-hints-pill-bar">
                    {[1, 2, 3, 4].map((step) => {
                      const isUnlocked = revealedHints.some((h) => h.index === step);
                      return (
                        <div
                          key={`hint-step-${step}`}
                          className={`bot-hint-pill ${isUnlocked ? 'bot-hint-pill--unlocked' : ''}`}
                        >
                          HINT {step} {isUnlocked ? '✓' : '🔒'}
                        </div>
                      );
                    })}
                  </div>

                  {revealedHints.length > 0 ? (
                    <div style={{ marginTop: '4px' }}>
                      {revealedHints.map((h) => (
                        <div key={`hist-hint-${h.index}`} style={{ marginBottom: '8px' }}>
                          <span className="step-badge" style={{ marginRight: '8px' }}>Hint {h.index}</span>
                          <span className="schematic-text" style={{ fontSize: '12.5px' }}>{h.text}</span>
                          {h.code_patch && (
                            <div className="bot-patch-box" style={{ marginTop: '6px' }}>
                              <div className="bot-patch-header">
                                <span className="bot-patch-tag">⚡ GUARDRAILED FIX (LINE {h.code_patch.target_line})</span>
                              </div>
                              <div className="bot-patch-diff">
                                {h.code_patch.original_snippet && (
                                  <div className="bot-diff-line bot-diff-line--del">
                                    <span className="diff-sign">-</span>
                                    <code>{h.code_patch.original_snippet}</code>
                                  </div>
                                )}
                                <div className="bot-diff-line bot-diff-line--add">
                                  <span className="diff-sign">+</span>
                                  <code>{h.code_patch.replacement_snippet}</code>
                                </div>
                              </div>
                              {patchApplied ? (
                                <div className="bot-patch-success">✓ Patch applied! Press RUN to test.</div>
                              ) : (
                                <button
                                  type="button"
                                  className="bot-patch-apply-btn"
                                  onClick={() => handleApplyCodePatch(h.code_patch)}
                                >
                                  ⚡ Apply Bot Fix to Line {h.code_patch.target_line}
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="schematic-text" style={{ fontSize: '12px', margin: '4px 0 0' }}>
                      {hasRun
                        ? (hasFailedTests
                            ? 'Error detected. Press the button above to float the bot directly to the error line.'
                            : 'All tests passed. You can still inspect any line with the assistant.')
                        : 'Run code in the sandbox to calibrate test results, or position your cursor and press the button for hints.'}
                    </p>
                  )}

                  {remainingHints > 0 && revealedHints.length < 4 && (
                    <button
                      type="button"
                      className="secondary-btn hint-btn"
                      style={{ alignSelf: 'flex-start', padding: '6px 14px', fontSize: '12px', marginTop: '6px' }}
                      disabled={isFetchingHint}
                      onClick={() => {
                        handleGetHint();
                        handleDeployBot('hint');
                      }}
                    >
                      {isFetchingHint ? 'Fetching hint…' : `Ask bot for next hint (${remainingHints} remaining)`}
                    </button>
                  )}
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
                    className={`schematic-bot-quick-btn ${botActive ? 'schematic-bot-quick-btn--active' : ''} ${hasFailedTests ? 'schematic-bot-quick-btn--error' : ''}`}
                    onClick={() => {
                      if (botActive) {
                        setBotActive(false);
                      } else {
                        handleDeployBot();
                      }
                    }}
                    title={botActive ? "Dock bot back" : (hasFailedTests ? `Hover bot to error line ${suspectErrorLine}` : `Hover bot to line ${activeLine}`)}
                  >
                    <img src={botAvatarImg} alt="Bot" className="bot-quick-img" />
                    <span>
                      {botActive
                        ? `DISMISS (LN ${targetLine})`
                        : hasFailedTests
                        ? `INSPECT ERROR (LN ${suspectErrorLine})`
                        : `ASK BOT (LN ${activeLine})`}
                    </span>
                  </button>

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

              <div className="schematic-editor-body-wrapper">
                {/* Line numbers gutter */}
                <div className="schematic-gutter" ref={gutterRef}>
                  {codeLines.map((_, i) => {
                    const lineNum = i + 1;
                    const isTarget = botActive && targetLine === lineNum;
                    const isCursor = activeLine === lineNum;
                    return (
                      <div
                        key={`gutter-${lineNum}`}
                        className={`schematic-gutter-line ${isTarget ? 'schematic-gutter-line--active' : ''} ${isCursor ? 'schematic-gutter-line--cursor' : ''}`}
                      >
                        {lineNum}
                      </div>
                    );
                  })}
                </div>

                {/* Editor surface with line highlight beam & hovering bot */}
                <div className="schematic-editor-surface">
                  {/* Active/Target line highlight beam */}
                  {botActive && targetLine && (
                    <div
                      className={`editor-line-highlight ${patchApplied ? 'editor-line-highlight--patched' : (botMode === 'error' ? 'editor-line-highlight--error' : 'editor-line-highlight--hint')}`}
                      style={{
                        top: `${(targetLine - 1) * 24 + 14 - scrollTop}px`
                      }}
                    />
                  )}

                  {/* Code Textarea */}
                  <textarea
                    ref={textareaRef}
                    className="code-textarea"
                    style={{ minHeight: '320px', height: '340px', borderRadius: 0, border: 'none' }}
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    onClick={handleCursorChange}
                    onKeyUp={handleCursorChange}
                    onSelect={handleCursorChange}
                    onScroll={handleScroll}
                    aria-label="Python code editor"
                    spellCheck={false}
                  />

                  {/* Floating Bot & Pop-up Speech Bubble */}
                  {botActive && targetLine && (
                    <div
                      className={`editor-floating-bot ${botMode === 'error' ? 'editor-floating-bot--error' : 'editor-floating-bot--hint'}`}
                      style={{
                        top: `${Math.max(6, (targetLine - 1) * 24 + 14 - 12 - scrollTop)}px`
                      }}
                    >
                      <div
                        className="floating-bot-avatar"
                        onClick={() => setBotActive(false)}
                        title="Click to dismiss bot"
                      >
                        <img src={botAvatarImg} alt="Cursed Shikigami Bot" className="floating-bot-img" />
                      </div>

                      <div className="bot-speech-bubble" role="dialog" aria-label="Bot diagnostic speech bubble">
                        <div className="bot-speech-bubble-arrow" />

                        <div className="bot-speech-bubble-header">
                          <span className="bot-bubble-tag">
                            {botMode === 'error' ? `⚠ BOT DIAGNOSTIC // LINE ${targetLine}` : `💡 BOT HINT // LINE ${targetLine}`}
                          </span>
                          <button
                            type="button"
                            className="bot-bubble-close-btn"
                            onClick={() => setBotActive(false)}
                            aria-label="Close speech bubble"
                          >
                            ✕
                          </button>
                        </div>

                        <div className="bot-speech-bubble-content">
                          {botMode === 'error' ? (
                            <>
                              <p className="bot-speech-intro">There is something wrong here...</p>
                              <p className="bot-speech-detail">{botDiagnostic.detail}</p>
                              {botDiagnostic.lineSnippet && (
                                <div className="bot-code-snippet">
                                  <code>LN {targetLine}: {botDiagnostic.lineSnippet}</code>
                                </div>
                              )}
                            </>
                          ) : (
                            <>
                              <p className="bot-speech-intro">
                                {latestHint ? `💡 Hint ${latestHint.index} of 4:` : '💡 Code Inspection Tip:'}
                              </p>
                              <p className="bot-speech-detail">
                                {latestHint
                                  ? latestHint.text
                                  : (hasRun
                                      ? 'Click unlock below to generate diagnostic hints for this challenge.'
                                      : 'Examine this line carefully. Run tests to calibrate progressive hints.')}
                              </p>

                              {latestHint?.code_patch && (
                                <div className="bot-patch-box">
                                  <div className="bot-patch-header">
                                    <span className="bot-patch-tag">⚡ GUARDRAILED FIX (LINE {latestHint.code_patch.target_line})</span>
                                  </div>
                                  <div className="bot-patch-diff">
                                    {latestHint.code_patch.original_snippet && (
                                      <div className="bot-diff-line bot-diff-line--del">
                                        <span className="diff-sign">-</span>
                                        <code>{latestHint.code_patch.original_snippet}</code>
                                      </div>
                                    )}
                                    <div className="bot-diff-line bot-diff-line--add">
                                      <span className="diff-sign">+</span>
                                      <code>{latestHint.code_patch.replacement_snippet}</code>
                                    </div>
                                  </div>
                                  {patchApplied ? (
                                    <div className="bot-patch-success">
                                      ✓ Patch applied to line {latestHint.code_patch.target_line}! Press RUN to verify.
                                    </div>
                                  ) : (
                                    <button
                                      type="button"
                                      className="bot-patch-apply-btn"
                                      onClick={() => handleApplyCodePatch(latestHint.code_patch)}
                                    >
                                      <span>⚡ Apply Bot Fix to Line {latestHint.code_patch.target_line}</span>
                                    </button>
                                  )}
                                </div>
                              )}
                            </>
                          )}
                        </div>

                        <div className="bot-speech-bubble-actions">
                          {botMode === 'hint' && remainingHints > 0 && revealedHints.length < 4 && (
                            <button
                              type="button"
                              className="secondary-btn bot-bubble-btn"
                              onClick={handleGetHint}
                              disabled={isFetchingHint}
                            >
                              {isFetchingHint ? 'Fetching hint…' : `Next Hint (${remainingHints} left)`}
                            </button>
                          )}
                          {botMode === 'error' && remainingHints > 0 && (
                            <button
                              type="button"
                              className="secondary-btn bot-bubble-btn"
                              onClick={() => {
                                setBotMode('hint');
                                handleGetHint();
                              }}
                              disabled={isFetchingHint}
                            >
                              {isFetchingHint ? 'Fetching hint…' : '💡 Give me a hint'}
                            </button>
                          )}
                          <button
                            type="button"
                            className="secondary-btn bot-bubble-btn bot-bubble-btn--dismiss"
                            onClick={() => setBotActive(false)}
                          >
                            Got it
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="schematic-editor-footer">
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span className="chip-dot" aria-hidden="true">●</span>
                  <span>[ STATUS: {sandboxStatus.toUpperCase()} ]</span>
                </div>
                <span>LN {activeLine} OF {lineCount} · UTF-8</span>
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
