import { Link, NavLink, Outlet } from "react-router-dom";
import { buildGeneralContactHref, contactActionLabel } from "../lib/contact";

export function SiteLayout() {
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
        <nav aria-label="Navegación principal">
          <NavLink to="/">Inicio</NavLink>
          <NavLink to="/propiedades">Propiedades</NavLink>
          <NavLink to="/admin">Admin</NavLink>
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
        <p>Merlo, San Luis</p>
      </footer>
    </div>
  );
}
