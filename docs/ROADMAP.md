# Roadmap de TopHouse

Actualizado: 21 de agosto de 2026.

## Fase 1 - Base de ingeniería

Estado: completada.

- Repositorio y flujo por ramas/PR.
- FastAPI y healthcheck.
- PostgreSQL 17 mediante Docker Compose.
- SQLAlchemy 2 y Alembic.
- Pytest, Black, Ruff, mypy y pre-commit.
- GitHub Actions con pruebas reales de PostgreSQL y round-trip de migraciones.

## Fase 2 - Backend inmobiliario

Estado: en ejecución.

- [x] Modelo `Propiedad` y dominio en español.
- [x] Dirección, coordenadas, privacidad y constraints geográficos (PR #5).
- [x] Schemas Pydantic de creación, actualización y respuesta.
- [x] Separación entre contratos públicos y administrativos.
- [x] Repository de propiedades.
- [x] Service con reglas de negocio, slug y transiciones de estado.
- [x] API administrativa con creación, consultas, PATCH y paginación.
- [x] Filtros públicos iniciales y paginación.
- [x] Respuestas públicas que protegen la ubicación exacta.
- [ ] Política de eliminación de propiedades.
- [x] Modelo de usuarios, roles y migración PostgreSQL.
- [x] Núcleo de autenticación: schemas, Argon2, Repository y Service.
- [x] Autenticación y sesiones administrativas con cookies seguras y CSRF.
- [ ] RBAC y auditoría.

## Fase 3 - Gestión de imágenes

- [ ] Definir límites de tamaño y cantidad por propiedad.
- [ ] Validación segura con Pillow.
- [ ] Normalización, limpieza de metadata, WebP y thumbnails.
- [ ] Integración con almacenamiento compatible con S3.
- [ ] Ordenamiento y selección de portada.

## Fase 4 - Frontend

- [ ] Aplicación React + TypeScript + Vite.
- [ ] Home, catálogo, filtros y detalle público.
- [ ] Galería, mapa y contacto por WhatsApp.
- [ ] Panel administrativo.
- [ ] Vitest y React Testing Library.
- [ ] Playwright E2E.

## Fase 5 - Producción

- [ ] Hardening de seguridad.
- [ ] Logging y observabilidad.
- [ ] Backups y procedimiento de recuperación de PostgreSQL.
- [ ] Contenedores y configuración de producción.
- [ ] HTTPS y despliegue.
- [ ] SEO y verificación responsive.

## Evolución posterior al MVP

Reservas, pagos, CRM avanzado, aplicación móvil, multi-sucursal,
automatizaciones externas e IA se evaluarán después de validar el MVP y solo
con requisitos de negocio concretos.
