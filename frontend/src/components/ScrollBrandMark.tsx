import { useEffect, useRef } from "react";

export function ScrollBrandMark() {
  const markRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const mark = markRef.current;
    if (!mark) return;

    const reduceMotion = window.matchMedia?.(
      "(prefers-reduced-motion: reduce)",
    );
    let animationFrame = 0;

    const updateProgress = () => {
      animationFrame = 0;
      const progress = reduceMotion?.matches
        ? 0
        : Math.min(window.scrollY / 520, 1);
      mark.style.setProperty("--brand-scrub", progress.toFixed(3));
      mark.dataset.scrubbed = progress > 0.72 ? "true" : "false";
    };

    const requestUpdate = () => {
      if (!animationFrame)
        animationFrame = requestAnimationFrame(updateProgress);
    };

    updateProgress();
    window.addEventListener("scroll", requestUpdate, { passive: true });
    reduceMotion?.addEventListener("change", requestUpdate);

    return () => {
      window.removeEventListener("scroll", requestUpdate);
      reduceMotion?.removeEventListener("change", requestUpdate);
      if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, []);

  return (
    <span ref={markRef} className="brand-mark" aria-hidden="true">
      <img src="/assets/tophouse-logo.webp" alt="" width="1774" height="887" />
      <span className="brand-mark-sheen" />
    </span>
  );
}
