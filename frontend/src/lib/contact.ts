import type { PublicProperty } from "../types/property";

const defaultContactEmail = "contacto@tophouse.com";

function getContactEmail(): string {
  return (
    (import.meta.env.VITE_CONTACT_EMAIL as string | undefined)?.trim() ||
    defaultContactEmail
  );
}

function getWhatsAppNumber(): string | null {
  const configured = (
    import.meta.env.VITE_WHATSAPP_NUMBER as string | undefined
  )
    ?.replace(/\D/g, "")
    .trim();
  return configured && configured.length >= 8 ? configured : null;
}

function publicOrigin(): string {
  return window.location.origin === "null" ? "" : window.location.origin;
}

export function buildGeneralContactHref(): string {
  const whatsappNumber = getWhatsAppNumber();
  const message =
    "Hola, quiero hablar con TopHouse por una consulta inmobiliaria en Merlo, San Luis.";
  if (whatsappNumber) {
    return `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;
  }
  return `mailto:${getContactEmail()}?subject=${encodeURIComponent(
    "Consulta inmobiliaria",
  )}&body=${encodeURIComponent(message)}`;
}

export function buildPropertyContactHref(property: PublicProperty): string {
  const whatsappNumber = getWhatsAppNumber();
  const url = `${publicOrigin()}/propiedades/${property.slug}`;
  const location = [property.localidad, property.zona]
    .filter(Boolean)
    .join(", ");
  const message = `Hola, quiero consultar por ${property.titulo} en ${location}. ${url}`;
  if (whatsappNumber) {
    return `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;
  }
  return `mailto:${getContactEmail()}?subject=${encodeURIComponent(
    `Consulta por ${property.titulo}`,
  )}&body=${encodeURIComponent(message)}`;
}

export function contactActionLabel(): string {
  return getWhatsAppNumber() ? "Contactar por WhatsApp" : "Contactar";
}
