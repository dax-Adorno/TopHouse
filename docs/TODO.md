# Próximos pasos de TopHouse

Actualizado: 21 de agosto de 2026.

## Siguiente bloque recomendado

1. Definir la API pública de Propiedades.
2. Listar únicamente propiedades publicadas.
3. Exponer detalle por slug sin dirección ni coordenadas exactas.
4. Agregar filtros públicos iniciales y paginación.
5. Agregar tests que demuestren que los datos geográficos privados no se
   filtran.
6. Ejecutar todos los quality gates y crear un Pull Request.

Los schemas ya fueron recuperados y adaptados a ubicación. El stash original se
mantiene temporalmente como copia de seguridad y solo debe eliminarse después de
que el PR de schemas esté integrado en `main`.

## Después de la API pública

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
