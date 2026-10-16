export default function SkeletonCard() {
  return (
    <article className="challenge-card challenge-card--skeleton" aria-hidden="true">
      <div className="challenge-card__top">
        <div className="skeleton-bar skeleton-bar--badge"></div>
        <div className="skeleton-bar skeleton-bar--status"></div>
      </div>
      <div className="skeleton-bar skeleton-bar--title"></div>
      <div className="skeleton-bar skeleton-bar--text"></div>
      <div className="skeleton-bar skeleton-bar--text-short"></div>
      <div className="challenge-card__tags">
        <div className="skeleton-bar skeleton-bar--tag"></div>
        <div className="skeleton-bar skeleton-bar--tag"></div>
      </div>
      <div className="challenge-card__action">
        <div className="skeleton-bar skeleton-bar--button"></div>
      </div>
    </article>
  );
}
