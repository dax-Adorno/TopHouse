import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { buildGeneralContactHref, contactActionLabel } from "../lib/contact";

export function SiteLayout() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const closeMenu = () => setIsMenuOpen(false);

  return (
    <div className="site-shell">
      <a className="skip-link" href="#main-content">
        Saltar al contenido
      </a>
      <header className="site-header">
        <Link className="brand" to="/" aria-label="TopHouse, inicio">
          <span className="brand-compact-mark" aria-hidden="true">
            TH
          </span>
          <span>TopHouse</span>
        </Link>
        <button
          className="menu-toggle"
          type="button"
          aria-expanded={isMenuOpen}
          aria-controls="primary-navigation"
          onClick={() => setIsMenuOpen((current) => !current)}
        >
          <span aria-hidden="true" />
          <span className="sr-only">Menú principal</span>
        </button>
        <nav
          id="primary-navigation"
          aria-label="Navegación principal"
          data-open={isMenuOpen}
        >
          <NavLink to="/" onClick={closeMenu}>
            Inicio
          </NavLink>
          <NavLink to="/propiedades" onClick={closeMenu}>
            Propiedades
          </NavLink>
          <NavLink to="/admin" onClick={closeMenu}>
            Admin
          </NavLink>
          <a
            className="mobile-contact"
            href={buildGeneralContactHref()}
            onClick={closeMenu}
          >
            {contactActionLabel()}
          </a>
        </nav>
        <a className="header-contact" href={buildGeneralContactHref()}>
          {contactActionLabel()}
        </a>
      </header>
      <main id="main-content" tabIndex={-1}>
        <Outlet />
      </main>
      <footer className="site-footer">
        <div>
          <strong>TopHouse</strong>
          <p>Propiedades elegidas con criterio.</p>
        </div>
        <div className="footer-socials" aria-label="Redes sociales de TopHouse">
          <p>Seguinos</p>
          <div>
            <button
              type="button"
              disabled
              aria-label="Instagram, próximamente"
              title="Instagram · Próximamente"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="3" y="3" width="18" height="18" rx="5" />
                <circle cx="12" cy="12" r="4" />
                <circle cx="17.4" cy="6.7" r="1" className="social-dot" />
              </svg>
            </button>
            <button
              type="button"
              disabled
              aria-label="Facebook, próximamente"
              title="Facebook · Próximamente"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M14 21v-8h2.8l.4-3H14V8.1c0-.9.3-1.6 1.7-1.6H17V3.8c-.4-.1-1.3-.2-2.4-.2-2.4 0-4.1 1.5-4.1 4.2V10H8v3h2.5v8H14Z" />
              </svg>
            </button>
            <button
              type="button"
              disabled
              aria-label="TikTok, próximamente"
              title="TikTok · Próximamente"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M14.3 3c.3 2.2 1.5 3.6 3.7 3.8v3.1a8.4 8.4 0 0 1-3.7-1.1v5.7a6 6 0 1 1-5.2-5.9v3.2a2.9 2.9 0 1 0 2 2.7V3h3.2Z" />
              </svg>
            </button>
          </div>
          <small>Enlaces próximamente</small>
        </div>
        <div className="footer-meta">
          <p>Merlo, San Luis</p>
          <p className="footer-credit">
            <img
              src="/assets/logo.webp"
              alt="Logo de Dax"
              width="56"
              height="56"
            />
            <span>
              <small>Diseño y desarrollo web</small>
              <strong>por Dax Adorno</strong>
            </span>
          </p>
        </div>
      </footer>
    </div>
  );
}
