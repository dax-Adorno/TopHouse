import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { formatMoney, operationLabel } from "../lib/propertyFormat";
import {
  createAdminProperty,
  getCurrentUser,
  listAdminProperties,
  login,
  logout,
} from "../lib/api";
import type { AdminUser } from "../types/auth";
import type {
  AdminProperty,
  AdminPropertyCreate,
  AdminPropertyPage,
  PublicProperty,
} from "../types/property";

type AuthState = "checking" | "anonymous" | "authenticated";
type SubmitState = "idle" | "submitting" | "error";
type PropertyState = "idle" | "loading" | "ready" | "error";
type CreateState = "idle" | "submitting" | "success" | "error";

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
  const [createState, setCreateState] = useState<CreateState>("idle");
  const [showCreateForm, setShowCreateForm] = useState(false);
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
    setCreateState("idle");
    setShowCreateForm(false);
    setAuthState("anonymous");
  }

  async function handleCreateProperty(datos: AdminPropertyCreate) {
    setCreateState("submitting");
    try {
      await createAdminProperty(datos);
      setCreateState("success");
      setShowCreateForm(false);
      await loadProperties();
    } catch {
      setCreateState("error");
    }
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
          createState={createState}
          showCreateForm={showCreateForm}
          onCancelCreate={() => {
            setCreateState("idle");
            setShowCreateForm(false);
          }}
          onCreate={handleCreateProperty}
          onOpenCreate={() => {
            setCreateState("idle");
            setShowCreateForm(true);
          }}
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
  createState,
  showCreateForm,
  onCancelCreate,
  onCreate,
  onOpenCreate,
  onRetry,
}: {
  page: AdminPropertyPage | null;
  state: PropertyState;
  createState: CreateState;
  showCreateForm: boolean;
  onCancelCreate: () => void;
  onCreate: (datos: AdminPropertyCreate) => Promise<void>;
  onOpenCreate: () => void;
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
        <button
          className="button button-primary"
          onClick={onOpenCreate}
          type="button"
        >
          Nueva propiedad
        </button>
      </div>
      {showCreateForm ? (
        <AdminPropertyCreateForm
          state={createState}
          onCancel={onCancelCreate}
          onSubmit={onCreate}
        />
      ) : null}
      {createState === "success" && !showCreateForm ? (
        <p className="admin-success" role="status">
          Propiedad creada como borrador.
        </p>
      ) : null}
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

function AdminPropertyCreateForm({
  state,
  onCancel,
  onSubmit,
}: {
  state: CreateState;
  onCancel: () => void;
  onSubmit: (datos: AdminPropertyCreate) => Promise<void>;
}) {
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await onSubmit({
      codigo: requiredText(form, "codigo"),
      titulo: requiredText(form, "titulo"),
      descripcion: requiredText(form, "descripcion"),
      tipo_operacion: requiredText(
        form,
        "tipo_operacion",
      ) as PublicProperty["tipo_operacion"],
      tipo_propiedad: requiredText(form, "tipo_propiedad"),
      ...optionalText(form, "precio"),
      ...optionalText(form, "moneda"),
      localidad: requiredText(form, "localidad"),
      ...optionalText(form, "zona"),
      ...optionalText(form, "direccion"),
      ...optionalText(form, "dormitorios"),
      ...optionalText(form, "banios"),
      ...optionalText(form, "superficie_cubierta"),
      ...optionalText(form, "superficie_total"),
    });
  }

  return (
    <form className="admin-create-form" onSubmit={handleSubmit}>
      <div className="admin-form-grid">
        <label>
          Código
          <input name="codigo" required />
        </label>
        <label>
          Título
          <input name="titulo" required />
        </label>
        <label className="admin-form-wide">
          Descripción
          <textarea name="descripcion" required rows={4} />
        </label>
        <label>
          Operación
          <select defaultValue="venta" name="tipo_operacion" required>
            <option value="venta">Venta</option>
            <option value="alquiler">Alquiler</option>
            <option value="temporario">Temporario</option>
          </select>
        </label>
        <label>
          Tipo
          <input defaultValue="casa" name="tipo_propiedad" required />
        </label>
        <label>
          Precio
          <input inputMode="decimal" name="precio" />
        </label>
        <label>
          Moneda
          <input defaultValue="USD" maxLength={3} name="moneda" />
        </label>
        <label>
          Localidad
          <input defaultValue="Merlo" name="localidad" required />
        </label>
        <label>
          Zona
          <input name="zona" />
        </label>
        <label className="admin-form-wide">
          Dirección
          <input name="direccion" />
        </label>
        <label>
          Dormitorios
          <input inputMode="numeric" name="dormitorios" />
        </label>
        <label>
          Baños
          <input inputMode="numeric" name="banios" />
        </label>
        <label>
          Sup. cubierta
          <input inputMode="decimal" name="superficie_cubierta" />
        </label>
        <label>
          Sup. total
          <input inputMode="decimal" name="superficie_total" />
        </label>
      </div>
      {state === "error" ? (
        <p className="admin-error" role="alert">
          No pudimos crear la propiedad. Revisá los datos e intentá nuevamente.
        </p>
      ) : null}
      <div className="admin-form-actions">
        <button
          className="button button-secondary"
          onClick={onCancel}
          type="button"
        >
          Cancelar
        </button>
        <button
          className="button button-primary"
          disabled={state === "submitting"}
          type="submit"
        >
          {state === "submitting" ? "Guardando..." : "Guardar borrador"}
        </button>
      </div>
    </form>
  );
}

function requiredText(form: FormData, name: string): string {
  return String(form.get(name) ?? "").trim();
}

function optionalText(
  form: FormData,
  name: keyof AdminPropertyCreate,
): Partial<AdminPropertyCreate> {
  const value = String(form.get(name) ?? "").trim();
  return value === "" ? {} : { [name]: value };
}
