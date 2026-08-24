import type { CSSProperties } from "react";

type BurstStyle = CSSProperties & {
  "--burst-angle": string;
  "--burst-delay": string;
  "--burst-distance": string;
  "--burst-duration": string;
  "--burst-size": string;
};

const PARTICLE_COUNT = 32;

const particles = Array.from({ length: PARTICLE_COUNT }, (_, index) => ({
  angle: `${(360 / PARTICLE_COUNT) * index + (index % 3) * 2.4}deg`,
  delay: `${-(index % 8) * 0.72}s`,
  distance: `${34 + (index % 6) * 8}vmax`,
  duration: `${5.8 + (index % 5) * 0.65}s`,
  size: `${2 + (index % 4)}px`,
}));

export function HeroStarBurst() {
  return (
    <div className="hero-star-burst" aria-hidden="true">
      <div className="hero-star-burst-core" />
      {particles.map((particle, index) => (
        <span
          key={index}
          style={
            {
              "--burst-angle": particle.angle,
              "--burst-delay": particle.delay,
              "--burst-distance": particle.distance,
              "--burst-duration": particle.duration,
              "--burst-size": particle.size,
            } as BurstStyle
          }
        />
      ))}
    </div>
  );
}
