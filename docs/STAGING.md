# Ambiente de staging

Staging permite que el cliente pruebe TopHouse con datos y archivos separados
de producción. Incluye frontend, API, PostgreSQL 17 y almacenamiento MinIO
compatible con S3. Solo el proxy web publica un puerto hacia el host.

## Preparación

1. Copiar `.env.staging.example` como `.env.staging`.
2. Reemplazar contraseñas, dominio, correo y WhatsApp.
3. Configurar HTTPS en el balanceador o proxy externo del proveedor.
4. Ejecutar:

```bash
docker compose --env-file .env.staging -f compose.staging.yml up -d --build
```

Las migraciones se aplican en un contenedor de una sola ejecución antes de que
arranque la API. El bucket también se crea antes del backend y permite lectura
pública solamente de objetos; las cargas y eliminaciones requieren las
credenciales privadas usadas por la API.

## Verificación

```bash
docker compose --env-file .env.staging -f compose.staging.yml ps
docker compose --env-file .env.staging -f compose.staging.yml logs migrate
curl --fail https://staging.tophouse.example/health
```

Después se debe crear un usuario administrativo de prueba y ejecutar la lista
de aceptación con el cliente: catálogo, filtros, detalle, creación y edición de
propiedades, carga, portada, orden y eliminación de imágenes.

## Operación segura

- Staging nunca comparte base de datos, bucket ni contraseñas con producción.
- `.env.staging` no se agrega a Git.
- Antes de actualizar, realizar backup de PostgreSQL y del volumen de objetos.
- No usar `docker compose down -v`: elimina ambos volúmenes de staging.
- Para detener sin borrar datos, usar `docker compose ... stop`.
- La consola de MinIO no se publica; solo `/media/` expone lectura de imágenes.

El proxy incluido sirve HTTP dentro del host. La terminación TLS y la
redirección HTTP a HTTPS pertenecen al balanceador o proxy externo, como se
define en `PRODUCTION_SECURITY.md`.
