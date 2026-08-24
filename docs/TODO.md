# Próximos pasos de TopHouse

Actualizado: 24 de agosto de 2026.

## Siguiente bloque recomendado

La API administrativa ya exige autenticación y CSRF. El RBAC reserva los
cambios de estado y destacado al rol `administrador`, y las mutaciones de
propiedades generan registros de auditoría.

1. Preparar hardening de seguridad y configuración de despliegue.
2. Documentar backups, recuperación y rollback operativo.

## Después de autenticación y auditoría

- Mantener pruebas E2E de frontend público y panel administrativo.
- Mantener pruebas específicas contra IDOR en recursos administrativos.

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
