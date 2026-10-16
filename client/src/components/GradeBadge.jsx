export default function GradeBadge({ grade, difficulty, showDifficulty = true, size = 'md' }) {
  const tooltipText = "Grade 4 is the starting level. Special Grade is the highest.";

  return (
    <span 
      className={`grade-badge grade-badge--${size}`} 
      title={tooltipText}
      tabIndex={0}
      aria-label={`${grade}${difficulty ? `, ${difficulty}` : ''}. ${tooltipText}`}
    >
      <span className="grade-badge__rank">{grade}</span>
      {showDifficulty && difficulty && (
        <span className="grade-badge__diff">· {difficulty}</span>
      )}
    </span>
  );
}
