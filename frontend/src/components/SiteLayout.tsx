import { Link, NavLink, Outlet } from "react-router-dom";

export function SiteLayout() {
  return (
    <div className="site-shell">
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
        <a className="header-contact" href="mailto:contacto@tophouse.com">
          Contactar
        </a>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="site-footer">
        <div>
          <strong>TopHouse</strong>
          <p>Propiedades elegidas con criterio.</p>
        </div>
        <p>Asunción, Paraguay</p>
      </footer>
    </div>
  );
}
