import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { formatMoney, operationLabel } from "../lib/propertyFormat";
import {
  archiveAdminProperty,
  createAdminProperty,
  getCurrentUser,
  listAdminProperties,
  login,
  logout,
  updateAdminPropertyDetails,
  updateAdminProperty,
} from "../lib/api";
import type { AdminUser } from "../types/auth";
import type {
  AdminProperty,
  AdminPropertyCreate,
  AdminPropertyDetailsUpdate,
  AdminPropertyPage,
  AdminPropertyUpdate,
  PublicProperty,
} from "../types/property";

type AuthState = "checking" | "anonymous" | "authenticated";
type SubmitState = "idle" | "submitting" | "error";
type PropertyState = "idle" | "loading" | "ready" | "error";
type CreateState = "idle" | "submitting" | "success" | "error";
type EditState = "idle" | "submitting" | "success" | "error";
type RowUpdateState = "idle" | "submitting" | "error";
type RowArchiveState = "idle" | "submitting" | "error";

const statusLabels: Record<AdminProperty["estado"], string> = {
  borrador: "Borrador",
  publicada: "Publicada",
  pausada: "Pausada",
  reservada: "Reservada",
  alquilada: "Alquilada",
  vendida: "Vendida",
  no_disponible: "No disponible",
};

const statusTransitions: Record<
  AdminProperty["estado"],
  AdminProperty["estado"][]
> = {
  borrador: ["publicada", "no_disponible"],
  publicada: ["pausada", "reservada", "alquilada", "vendida", "no_disponible"],
  pausada: ["publicada", "no_disponible"],
  reservada: ["publicada", "alquilada", "vendida", "no_disponible"],
  alquilada: ["publicada", "no_disponible"],
  vendida: ["no_disponible"],
  no_disponible: ["borrador"],
};

export function AdminPage() {
  const [authState, setAuthState] = useState<AuthState>("checking");
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [propertyState, setPropertyState] = useState<PropertyState>("idle");
  const [createState, setCreateState] = useState<CreateState>("idle");
  const [editState, setEditState] = useState<EditState>("idle");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingProperty, setEditingProperty] = useState<AdminProperty | null>(
    null,
  );
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
    setEditState("idle");
    setShowCreateForm(false);
    setEditingProperty(null);
    setAuthState("anonymous");
  }

  async function handleCreateProperty(datos: AdminPropertyCreate) {
    setCreateState("submitting");
    try {
      await createAdminProperty(datos);
      setCreateState("success");
      setShowCreateForm(false);
      setEditingProperty(null);
      await loadProperties();
    } catch {
      setCreateState("error");
    }
  }

  async function handleEditProperty(
    propertyId: number,
    cambios: AdminPropertyDetailsUpdate,
  ) {
    setEditState("submitting");
    try {
      await updateAdminPropertyDetails(propertyId, cambios);
      setEditState("success");
      setEditingProperty(null);
      await loadProperties();
    } catch {
      setEditState("error");
    }
  }

  async function handleUpdateProperty(
    propertyId: number,
    cambios: AdminPropertyUpdate,
  ) {
    await updateAdminProperty(propertyId, cambios);
    await loadProperties();
  }

  async function handleArchiveProperty(propertyId: number) {
    await archiveAdminProperty(propertyId);
    await loadProperties();
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
          editState={editState}
          editingProperty={editingProperty}
          onCancelEdit={() => {
            setEditState("idle");
            setEditingProperty(null);
          }}
          onCreate={handleCreateProperty}
          onEdit={handleEditProperty}
          onOpenCreate={() => {
            setCreateState("idle");
            setEditState("idle");
            setEditingProperty(null);
            setShowCreateForm(true);
          }}
          onOpenEdit={(property) => {
            setCreateState("idle");
            setEditState("idle");
            setShowCreateForm(false);
            setEditingProperty(property);
          }}
          onArchive={handleArchiveProperty}
          onRetry={() => void loadProperties()}
          onUpdate={handleUpdateProperty}
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
  editState,
  editingProperty,
  showCreateForm,
  onCancelEdit,
  onCancelCreate,
  onArchive,
  onCreate,
  onEdit,
  onOpenCreate,
  onOpenEdit,
  onRetry,
  onUpdate,
}: {
  page: AdminPropertyPage | null;
  state: PropertyState;
  createState: CreateState;
  editState: EditState;
  editingProperty: AdminProperty | null;
  showCreateForm: boolean;
  onCancelEdit: () => void;
  onCancelCreate: () => void;
  onArchive: (propertyId: number) => Promise<void>;
  onCreate: (datos: AdminPropertyCreate) => Promise<void>;
  onEdit: (
    propertyId: number,
    cambios: AdminPropertyDetailsUpdate,
  ) => Promise<void>;
  onOpenCreate: () => void;
  onOpenEdit: (property: AdminProperty) => void;
  onRetry: () => void;
  onUpdate: (propertyId: number, cambios: AdminPropertyUpdate) => Promise<void>;
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
      {editingProperty !== null ? (
        <AdminPropertyDetailsForm
          property={editingProperty}
          state={editState}
          onCancel={onCancelEdit}
          onSubmit={onEdit}
        />
      ) : null}
      {createState === "success" && !showCreateForm ? (
        <p className="admin-success" role="status">
          Propiedad creada como borrador.
        </p>
      ) : null}
      {editState === "success" && editingProperty === null ? (
        <p className="admin-success" role="status">
          Datos de propiedad actualizados.
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
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {page.items.map((property) => (
              <AdminPropertyRow
                key={`${property.id}-${property.estado}-${property.destacada}`}
                onArchive={onArchive}
                onEdit={onOpenEdit}
                property={property}
                onUpdate={onUpdate}
              />
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function AdminPropertyRow({
  onArchive,
  onEdit,
  property,
  onUpdate,
}: {
  onArchive: (propertyId: number) => Promise<void>;
  onEdit: (property: AdminProperty) => void;
  property: AdminProperty;
  onUpdate: (propertyId: number, cambios: AdminPropertyUpdate) => Promise<void>;
}) {
  const [estado, setEstado] = useState(property.estado);
  const [destacada, setDestacada] = useState(property.destacada);
  const [archiveState, setArchiveState] = useState<RowArchiveState>("idle");
  const [updateState, setUpdateState] = useState<RowUpdateState>("idle");
  const stateOptions = [property.estado, ...statusTransitions[property.estado]];
  const hasChanges =
    estado !== property.estado || destacada !== property.destacada;

  async function handleSave() {
    if (!hasChanges) return;
    setUpdateState("submitting");
    try {
      await onUpdate(property.id, { estado, destacada });
      setUpdateState("idle");
    } catch {
      setUpdateState("error");
    }
  }

  async function handleArchive() {
    const confirmed = window.confirm(
      `Archivar ${property.codigo} y quitarla del catálogo público?`,
    );
    if (!confirmed) return;

    setArchiveState("submitting");
    try {
      await onArchive(property.id);
      setArchiveState("idle");
    } catch {
      setArchiveState("error");
    }
  }

  return (
    <tr>
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
        <label className="admin-row-control">
          <span>Estado</span>
          <select
            aria-label={`Estado de ${property.codigo}`}
            onChange={(event) =>
              setEstado(event.target.value as AdminProperty["estado"])
            }
            value={estado}
          >
            {stateOptions.map((option) => (
              <option key={option} value={option}>
                {statusLabels[option]}
              </option>
            ))}
          </select>
        </label>
      </td>
      <td>
        <label className="admin-checkbox">
          <input
            aria-label={`Destacada ${property.codigo}`}
            checked={destacada}
            onChange={(event) => setDestacada(event.target.checked)}
            type="checkbox"
          />
          <span>{destacada ? "Sí" : "No"}</span>
        </label>
      </td>
      <td>
        <div className="admin-row-actions">
          <button
            className="button button-secondary"
            onClick={() => onEdit(property)}
            type="button"
          >
            Editar datos
          </button>
          <button
            className="button button-secondary"
            disabled={!hasChanges || updateState === "submitting"}
            onClick={handleSave}
            type="button"
          >
            {updateState === "submitting" ? "Guardando..." : "Guardar"}
          </button>
          <button
            className="button button-danger"
            disabled={archiveState === "submitting"}
            onClick={handleArchive}
            type="button"
          >
            {archiveState === "submitting" ? "Archivando..." : "Archivar"}
          </button>
          {updateState === "error" ? (
            <span role="alert">No se pudo guardar.</span>
          ) : null}
          {archiveState === "error" ? (
            <span role="alert">No se pudo archivar.</span>
          ) : null}
        </div>
      </td>
    </tr>
  );
}

function AdminPropertyDetailsForm({
  property,
  state,
  onCancel,
  onSubmit,
}: {
  property: AdminProperty;
  state: EditState;
  onCancel: () => void;
  onSubmit: (
    propertyId: number,
    cambios: AdminPropertyDetailsUpdate,
  ) => Promise<void>;
}) {
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await onSubmit(property.id, {
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
      <div className="admin-form-title">
        <h3>Editar {property.codigo}</h3>
        <p>Actualizá los datos descriptivos sin cambiar estado ni destacada.</p>
      </div>
      <AdminPropertyFields property={property} />
      {state === "error" ? (
        <p className="admin-error" role="alert">
          No pudimos actualizar la propiedad. Revisá los datos e intentá
          nuevamente.
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
          {state === "submitting" ? "Guardando..." : "Guardar datos"}
        </button>
      </div>
    </form>
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
      <AdminPropertyFields />
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

function AdminPropertyFields({ property }: { property?: AdminProperty }) {
  return (
    <div className="admin-form-grid">
      <label>
        Código
        <input defaultValue={property?.codigo} name="codigo" required />
      </label>
      <label>
        Título
        <input defaultValue={property?.titulo} name="titulo" required />
      </label>
      <label className="admin-form-wide">
        Descripción
        <textarea
          defaultValue={property?.descripcion}
          name="descripcion"
          required
          rows={4}
        />
      </label>
      <label>
        Operación
        <select
          defaultValue={property?.tipo_operacion ?? "venta"}
          name="tipo_operacion"
          required
        >
          <option value="venta">Venta</option>
          <option value="alquiler">Alquiler</option>
          <option value="temporario">Temporario</option>
        </select>
      </label>
      <label>
        Tipo
        <input
          defaultValue={property?.tipo_propiedad ?? "casa"}
          name="tipo_propiedad"
          required
        />
      </label>
      <label>
        Precio
        <input
          defaultValue={property?.precio ?? ""}
          inputMode="decimal"
          name="precio"
        />
      </label>
      <label>
        Moneda
        <input
          defaultValue={property?.moneda ?? "USD"}
          maxLength={3}
          name="moneda"
        />
      </label>
      <label>
        Localidad
        <input
          defaultValue={property?.localidad ?? "Merlo"}
          name="localidad"
          required
        />
      </label>
      <label>
        Zona
        <input defaultValue={property?.zona ?? ""} name="zona" />
      </label>
      <label className="admin-form-wide">
        Dirección
        <input defaultValue={property?.direccion ?? ""} name="direccion" />
      </label>
      <label>
        Dormitorios
        <input
          defaultValue={property?.dormitorios ?? ""}
          inputMode="numeric"
          name="dormitorios"
        />
      </label>
      <label>
        Baños
        <input
          defaultValue={property?.banios ?? ""}
          inputMode="numeric"
          name="banios"
        />
      </label>
      <label>
        Sup. cubierta
        <input
          defaultValue={property?.superficie_cubierta ?? ""}
          inputMode="decimal"
          name="superficie_cubierta"
        />
      </label>
      <label>
        Sup. total
        <input
          defaultValue={property?.superficie_total ?? ""}
          inputMode="decimal"
          name="superficie_total"
        />
      </label>
    </div>
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
