import type { CSSProperties } from "react";

type BurstStyle = CSSProperties & {
  "--burst-angle": string;
  "--burst-delay": string;
  "--burst-distance": string;
  "--burst-duration": string;
  "--burst-size": string;
};

type PixelStyle = CSSProperties & {
  "--pixel-delay": string;
  "--pixel-drift": string;
  "--pixel-duration": string;
  "--pixel-left": string;
  "--pixel-size": string;
};

const PARTICLE_COUNT = 48;
const PIXEL_COUNT = 64;

const particles = Array.from({ length: PARTICLE_COUNT }, (_, index) => ({
  angle: `${(360 / PARTICLE_COUNT) * index + (index % 3) * 2.4}deg`,
  delay: `${-(index % 8) * 0.72}s`,
  distance: `${34 + (index % 6) * 8}vmax`,
  duration: `${5.8 + (index % 5) * 0.65}s`,
  size: `${2 + (index % 4)}px`,
}));

const pixels = Array.from({ length: PIXEL_COUNT }, (_, index) => ({
  delay: `${-(index % 16) * 0.38}s`,
  drift: `${((index * 17) % 72) - 36}px`,
  duration: `${3.4 + (index % 7) * 0.42}s`,
  left: `${45 + ((index * 29) % 54)}%`,
  size: `${2 + (index % 5)}px`,
}));

export function HeroStarBurst() {
  return (
    <div className="hero-star-burst" aria-hidden="true">
      <div className="hero-star-burst-core" />
      {particles.map((particle, index) => (
        <span
          className="hero-burst-ray"
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

export function HeroPixelRain() {
  return (
    <div className="hero-pixel-rain" aria-hidden="true">
      {pixels.map((pixel, index) => (
        <span
          key={index}
          style={
            {
              "--pixel-delay": pixel.delay,
              "--pixel-drift": pixel.drift,
              "--pixel-duration": pixel.duration,
              "--pixel-left": pixel.left,
              "--pixel-size": pixel.size,
            } as PixelStyle
          }
        />
      ))}
    </div>
  );
}
