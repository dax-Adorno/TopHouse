import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { formatMoney, operationLabel } from "../lib/propertyFormat";
import { getCurrentUser, listAdminProperties, login, logout } from "../lib/api";
import type { AdminUser } from "../types/auth";
import type { AdminProperty, AdminPropertyPage } from "../types/property";

type AuthState = "checking" | "anonymous" | "authenticated";
type SubmitState = "idle" | "submitting" | "error";
type PropertyState = "idle" | "loading" | "ready" | "error";

const statusLabels: Record<AdminProperty["estado"], string> = {
  borrador: "Borrador",
  publicada: "Publicada",
  pausada: "Pausada",
  reservada: "Reservada",
  alquilada: "Alquilada",
  vendida: "Vendida",
  no_disponible: "No disponible",
};

export function AdminPage() {
  const [authState, setAuthState] = useState<AuthState>("checking");
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [propertyState, setPropertyState] = useState<PropertyState>("idle");
  const [propertyPage, setPropertyPage] = useState<AdminPropertyPage | null>(
    null,
  );
  const [user, setUser] = useState<AdminUser | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function loadProperties(signal?: AbortSignal) {
    setPropertyState("loading");
    try {
      const page = await listAdminProperties(signal);
      setPropertyPage(page);
      setPropertyState("ready");
    } catch {
      setPropertyState("error");
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    getCurrentUser(controller.signal)
      .then((currentUser) => {
        setUser(currentUser);
        setAuthState("authenticated");
        void loadProperties(controller.signal);
      })
      .catch(() => setAuthState("anonymous"));
    return () => controller.abort();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitState("submitting");
    try {
      const currentUser = await login({ email, contrasena: password });
      setUser(currentUser);
      setPassword("");
      setAuthState("authenticated");
      setSubmitState("idle");
      void loadProperties();
    } catch {
      setSubmitState("error");
    }
  }

  async function handleLogout() {
    await logout();
    setUser(null);
    setPropertyPage(null);
    setPropertyState("idle");
    setAuthState("anonymous");
  }

  if (authState === "checking") {
    return (
      <section className="admin-shell admin-state">
        <p>Validando sesión administrativa...</p>
      </section>
    );
  }

  if (authState === "authenticated" && user !== null) {
    const published = propertyPage?.items.filter(
      (property) => property.estado === "publicada",
    ).length;
    const featured = propertyPage?.items.filter(
      (property) => property.destacada,
    ).length;

    return (
      <section className="admin-shell admin-dashboard">
        <div className="admin-panel-heading">
          <p className="eyebrow">Administración</p>
          <h1>Panel de TopHouse</h1>
          <p>
            Sesión iniciada como <strong>{user.nombre}</strong>.
          </p>
        </div>
        <div className="admin-overview">
          <div className="admin-session-card">
            <dl>
              <div>
                <dt>Email</dt>
                <dd>{user.email}</dd>
              </div>
              <div>
                <dt>Rol</dt>
                <dd>{user.rol}</dd>
              </div>
              <div>
                <dt>Estado</dt>
                <dd>{user.activo ? "Activo" : "Inactivo"}</dd>
              </div>
            </dl>
            <button className="button button-secondary" onClick={handleLogout}>
              Cerrar sesión
            </button>
          </div>
          <div className="admin-metrics" aria-label="Resumen de propiedades">
            <div>
              <span>Total</span>
              <strong>{propertyPage?.total ?? "-"}</strong>
            </div>
            <div>
              <span>Publicadas</span>
              <strong>{published ?? "-"}</strong>
            </div>
            <div>
              <span>Destacadas</span>
              <strong>{featured ?? "-"}</strong>
            </div>
          </div>
        </div>
        <AdminPropertyTable
          page={propertyPage}
          state={propertyState}
          onRetry={() => void loadProperties()}
        />
      </section>
    );
  }

  return (
    <section className="admin-shell admin-login">
      <div className="admin-panel-heading">
        <p className="eyebrow">Administración</p>
        <h1>Acceso interno</h1>
      </div>
      <form className="admin-login-form" onSubmit={handleSubmit}>
        <label>
          Email
          <input
            autoComplete="email"
            name="email"
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
        </label>
        <label>
          Contraseña
          <input
            autoComplete="current-password"
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
        </label>
        {submitState === "error" ? (
          <p className="admin-error" role="alert">
            No pudimos iniciar sesión con esas credenciales.
          </p>
        ) : null}
        <button
          className="button button-primary"
          disabled={submitState === "submitting"}
          type="submit"
        >
          {submitState === "submitting" ? "Ingresando..." : "Ingresar"}
        </button>
      </form>
    </section>
  );
}

function AdminPropertyTable({
  page,
  state,
  onRetry,
}: {
  page: AdminPropertyPage | null;
  state: PropertyState;
  onRetry: () => void;
}) {
  if (state === "loading") {
    return (
      <div className="admin-table-state">
        <p>Cargando propiedades...</p>
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className="admin-table-state admin-table-error">
        <p>No pudimos cargar las propiedades administrativas.</p>
        <button className="button button-secondary" onClick={onRetry}>
          Reintentar
        </button>
      </div>
    );
  }

  if (page === null || page.items.length === 0) {
    return (
      <div className="admin-table-state">
        <p>No hay propiedades cargadas.</p>
      </div>
    );
  }

  return (
    <section
      className="admin-properties"
      aria-labelledby="admin-properties-title"
    >
      <div className="admin-section-heading">
        <div>
          <p className="eyebrow">Inventario</p>
          <h2 id="admin-properties-title">Propiedades</h2>
        </div>
        <button className="button button-primary" type="button">
          Nueva propiedad
        </button>
      </div>
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Propiedad</th>
              <th>Operación</th>
              <th>Precio</th>
              <th>Estado</th>
              <th>Destacada</th>
            </tr>
          </thead>
          <tbody>
            {page.items.map((property) => (
              <tr key={property.id}>
                <td>{property.codigo}</td>
                <td>
                  <strong>{property.titulo}</strong>
                  <span>
                    {property.localidad}
                    {property.zona ? `, ${property.zona}` : ""}
                  </span>
                </td>
                <td>{operationLabel(property.tipo_operacion)}</td>
                <td>{formatMoney(property)}</td>
                <td>
                  <span
                    className={`admin-status admin-status-${property.estado}`}
                  >
                    {statusLabels[property.estado]}
                  </span>
                </td>
                <td>{property.destacada ? "Sí" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
