# Entrega y caché de imágenes

TopHouse genera WebP y thumbnails con claves inmutables basadas en UUID. Cada
objeto se guarda con `Cache-Control: public, max-age=31536000, immutable`, por
lo que el navegador y una CDN pueden conservarlo durante un año sin purgas.

## Producción con CDN

Configurar `S3_PUBLIC_BASE_URL` con el origen público de imágenes, sin incluir
el bucket ni una barra final. Por ejemplo:

```dotenv
S3_PUBLIC_BASE_URL=https://imagenes.tophouse.com
```

La CDN debe usar el bucket S3-compatible como origen y restringir el acceso
directo al bucket cuando el proveedor permita una identidad de origen. Las
rutas `propiedades/{id}/{uuid}.webp` y sus thumbnails pueden cachearse sin
invalidación porque una edición siempre crea una clave nueva.

## Desarrollo o almacenamiento privado

Si `S3_PUBLIC_BASE_URL` queda vacío, el backend conserva el comportamiento
privado y genera URLs firmadas de S3 con vencimiento. Este modo permite usar
MinIO u otro proveedor compatible sin configurar una CDN.

Al eliminar una imagen, TopHouse borra tanto el original como el thumbnail. La
CDN puede conservar temporalmente una copia inaccesible por su URL anterior;
como las claves nunca se reutilizan, esa copia no puede reemplazar otra imagen.
