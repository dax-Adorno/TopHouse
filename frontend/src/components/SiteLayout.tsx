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
          <span className="brand-mark">TH</span>
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
        <div className="footer-meta">
          <p>Merlo, San Luis</p>
          <p className="footer-credit">
            <img
              src="/assets/logo.webp"
              alt="Logo de Dax"
              width="56"
              height="56"
            />
            <span>Sitio elaborado por Dax</span>
          </p>
        </div>
      </footer>
    </div>
  );
}
