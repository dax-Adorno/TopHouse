import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { getCurrentUser, login, logout } from "../lib/api";
import type { AdminUser } from "../types/auth";

type AuthState = "checking" | "anonymous" | "authenticated";
type SubmitState = "idle" | "submitting" | "error";

export function AdminPage() {
  const [authState, setAuthState] = useState<AuthState>("checking");
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [user, setUser] = useState<AdminUser | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    getCurrentUser(controller.signal)
      .then((currentUser) => {
        setUser(currentUser);
        setAuthState("authenticated");
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
    } catch {
      setSubmitState("error");
    }
  }

  async function handleLogout() {
    await logout();
    setUser(null);
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
    return (
      <section className="admin-shell admin-dashboard">
        <div className="admin-panel-heading">
          <p className="eyebrow">Administración</p>
          <h1>Panel de TopHouse</h1>
          <p>
            Sesión iniciada como <strong>{user.nombre}</strong>.
          </p>
        </div>
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
