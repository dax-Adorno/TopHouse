export type PropertyImage = {
  id: number;
  url: string;
  url_thumbnail: string;
  ancho: number;
  alto: number;
  orden: number;
  es_portada: boolean;
};
export type PublicProperty = {
  id: number;
  codigo: string;
  slug: string;
  titulo: string;
  descripcion: string;
  tipo_operacion: "venta" | "alquiler" | "temporario";
  tipo_propiedad: string;
  precio: string | null;
  moneda: string | null;
  localidad: string;
  zona: string | null;
  dormitorios: number | null;
  banios: number | null;
  superficie_cubierta: string | null;
  superficie_total: string | null;
  estado: "publicada";
  destacada: boolean;
  imagenes: PropertyImage[];
  creado_en: string;
  actualizado_en: string;
};
export type AdminProperty = Omit<PublicProperty, "estado" | "imagenes"> & {
  direccion: string | null;
  latitud: string | null;
  longitud: string | null;
  mostrar_ubicacion_exacta: boolean;
  estado:
    | "borrador"
    | "publicada"
    | "pausada"
    | "reservada"
    | "alquilada"
    | "vendida"
    | "no_disponible";
};
export type PropertyPage = {
  items: PublicProperty[];
  total: number;
  offset: number;
  limit: number;
};
export type AdminPropertyPage = {
  items: AdminProperty[];
  total: number;
  offset: number;
  limit: number;
};
export type PublicPropertyFilters = {
  offset?: number;
  limit?: number;
  tipo_operacion?: PublicProperty["tipo_operacion"] | "";
  tipo_propiedad?: string;
  localidad?: string;
  precio_min?: string;
  precio_max?: string;
  dormitorios_min?: string;
  destacada?: boolean;
};
