# Próximos pasos de TopHouse

Actualizado: 21 de agosto de 2026.

## Siguiente bloque recomendado

1. Implementar Repository de Propiedad con SQLAlchemy.
2. Definir operaciones de creación, consulta por ID, consulta por slug,
   actualización y listado paginado.
3. Manejar de forma explícita códigos y slugs duplicados.
4. Agregar tests de integración contra PostgreSQL.
5. Ejecutar todos los quality gates y crear un Pull Request.

Los schemas ya fueron recuperados y adaptados a ubicación. El stash original se
mantiene temporalmente como copia de seguridad y solo debe eliminarse después de
que el PR de schemas esté integrado en `main`.

## Después del Repository

- Implementar Service con generación de slug y transiciones de estado.
- Exponer CRUD, filtros y paginación en `/api/v1/propiedades`.
- Definir y probar la respuesta pública sin coordenadas exactas.
- Implementar autenticación segura, RBAC y audit log.
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
