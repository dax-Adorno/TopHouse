# Próximos pasos de TopHouse

Actualizado: 21 de agosto de 2026.

## Siguiente bloque recomendado

El núcleo de usuarios ya incluye schemas estrictos, hash y verificación con
Argon2, Repository, Service y pruebas de credenciales y usuarios inactivos.

1. Implementar login, logout y sesiones administrativas.
2. Incorporar cookies seguras y protección CSRF.
3. Agregar pruebas de ciclo de vida, expiración y revocación de sesiones.
4. Ejecutar todos los quality gates y crear un Pull Request.

Después de las sesiones se protegerán los endpoints administrativos con RBAC y
se incorporará el registro de auditoría.

## Después de autenticación y auditoría

- Diseñar e implementar imágenes con S3, Pillow, WebP y thumbnails.
- Iniciar frontend público y panel administrativo.

## Decisiones abiertas

- Taxonomía definitiva de `tipo_propiedad`.
- Restricción de `moneda` y posible uso de ISO 4217.
- Transiciones válidas de `estado` y permisos asociados.
- Política de dirección y coordenadas en la API pública.
- Borrado físico o lógico para propiedades e imágenes.
- Límites de uploads y tamaños derivados.
- Proveedor S3-compatible y hosting final.
- Roles mínimos y permisos granulares.
- Backups, recuperación y retención de PostgreSQL.
- Proveedor de mapas en frontend.

## Precauciones operativas

- No ejecutar `docker compose down -v` salvo que se quiera destruir el volumen.
- No aplicar migraciones autogeneradas sin revisión manual.
- Ejecutar Alembic desde `backend`.
- No exponer coordenadas exactas por conveniencia del frontend.
- No guardar secretos en Git ni en documentación.
- No agregar infraestructura o IA sin un requisito concreto.
- No mezclar cambios no relacionados en un mismo PR.
