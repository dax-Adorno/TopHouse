import type { ReactNode } from "react";

export function SectionHeading({
  id,
  eyebrow,
  children,
  action,
}: {
  id: string;
  eyebrow?: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="section-heading">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2 id={id}>{children}</h2>
      </div>
      {action}
    </div>
  );
}
