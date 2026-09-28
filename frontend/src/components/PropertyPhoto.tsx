import { useState } from "react";
import type { PropertyImage } from "../types/property";

/** Shared media frame: real property photos, or an explicit branded fallback. */
export function PropertyPhoto({
  image,
  alt,
  thumbnail = false,
  priority = false,
}: {
  image?: PropertyImage;
  alt: string;
  thumbnail?: boolean;
  priority?: boolean;
}) {
  const [failedSource, setFailedSource] = useState<string>();
  const source = thumbnail ? image?.url_thumbnail || image?.url : image?.url;
  if (!source || source === failedSource) {
    return (
      <div
        className="property-photo-placeholder"
        role="img"
        aria-label={
          alt ? `${alt}: fotografía no disponible` : "Fotografía no disponible"
        }
      >
        <img
          src="/assets/tophouse-logo.webp"
          alt=""
          width="1774"
          height="887"
          loading="lazy"
        />
        <span>Fotografía no disponible</span>
      </div>
    );
  }
  return (
    <img
      className="property-photo"
      src={source}
      alt={alt}
      width={image?.ancho}
      height={image?.alto}
      loading={priority ? "eager" : "lazy"}
      decoding="async"
      fetchPriority={priority ? "high" : "auto"}
      onError={() => setFailedSource(source)}
    />
  );
}
