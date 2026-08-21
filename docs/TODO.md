# Próximos pasos de TopHouse

Actualizado: 21 de agosto de 2026.

## Siguiente bloque recomendado

1. Crear una rama `feat/property-schemas` desde `main` actualizado.
2. Confirmar que `stash@{0}` sigue disponible y revisar su contenido sin
   eliminarlo.
3. Aplicar el stash y adaptar los schemas a `direccion`, `latitud`, `longitud`
   y `mostrar_ubicacion_exacta`.
4. Separar los contratos públicos y administrativos para evitar filtraciones de
   ubicación.
5. Agregar pruebas de enums inválidos, números negativos, campos extra,
   coordenadas, PATCH parcial y mass assignment.
6. Ejecutar todos los quality gates y crear un Pull Request.

No eliminar el stash hasta confirmar que sus cambios fueron recuperados,
probados, comprometidos y publicados correctamente.

## Después de schemas

- Implementar Repository de Propiedad con SQLAlchemy.
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
