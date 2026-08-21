# Próximos pasos de TopHouse

Actualizado: 21 de agosto de 2026.

## Siguiente bloque recomendado

1. Diseñar usuarios, roles y sesiones administrativas.
2. Crear migraciones para usuarios y auditoría.
3. Implementar hash de contraseñas con Argon2.
4. Proteger endpoints administrativos con autenticación y RBAC.
5. Incorporar protección CSRF para operaciones autenticadas por cookie.
6. Registrar acciones administrativas relevantes.
7. Agregar pruebas de autenticación, autorización e IDOR.
8. Ejecutar todos los quality gates y crear Pull Requests cohesivos.

Los schemas ya fueron recuperados y adaptados a ubicación. El stash original se
mantiene temporalmente como copia de seguridad y solo debe eliminarse después de
que el PR de schemas esté integrado en `main`.

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
