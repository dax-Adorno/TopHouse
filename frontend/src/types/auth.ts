export type UserRole = "administrador" | "operador";

export type AdminUser = {
  id: number;
  email: string;
  nombre: string;
  rol: UserRole;
  activo: boolean;
  ultimo_acceso_en: string | null;
  creado_en: string;
  actualizado_en: string;
};

export type LoginCredentials = {
  email: string;
  contrasena: string;
};
