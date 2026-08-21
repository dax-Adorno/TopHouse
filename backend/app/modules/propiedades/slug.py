import re
import unicodedata


def normalizar_slug(texto: str, *, max_length: int = 180) -> str:
    """Convierte un título en un slug ASCII apto para URL."""

    normalizado = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(
        caracter for caracter in normalizado if not unicodedata.combining(caracter)
    )
    slug = re.sub(r"[^a-z0-9]+", "-", sin_acentos.lower()).strip("-")
    slug = slug[:max_length].rstrip("-")
    return slug or "propiedad"


def slug_con_sufijo(base: str, numero: int, *, max_length: int = 180) -> str:
    sufijo = f"-{numero}"
    prefijo = base[: max_length - len(sufijo)].rstrip("-")
    return f"{prefijo}{sufijo}"
