# Contexto del proyecto TopHouse

Actualizado: 21 de agosto de 2026.

## Propósito

TopHouse es una aplicación web inmobiliaria de producción para Inmobiliaria
Samanta. Busca centralizar el inventario, facilitar la publicación y búsqueda de
propiedades, reducir el trabajo manual del equipo administrativo y ofrecer una
base técnica mantenible, auditable y desplegable.

No es una web estática ni una demostración de portafolio. El producto debe
soportar aproximadamente 100 propiedades inicialmente, con unas 5 a 10 imágenes
por propiedad y operaciones de venta, alquiler y alquiler temporario.

## Alcance del MVP

### Sitio público

- Home, catálogo, propiedades destacadas y detalle del inmueble.
- Filtros por operación y características.
- Galería, mapa, enlace a WhatsApp y URLs compartibles.
- Diseño responsive y SEO básico.

### Administración

- Autenticación y roles básicos.
- CRUD de propiedades y gestión de su estado.
- Gestión de destacados, búsqueda y acciones auditables.
- Carga y ordenamiento de imágenes con portada configurable.

### Imágenes

- Validación real de formato, tamaño y dimensiones.
- Normalización, eliminación de metadata, resize y compresión.
- WebP, thumbnails y almacenamiento compatible con S3.

## Fuera del MVP

- IA generativa, chatbot y búsqueda semántica.
- Reservas, pagos y CRM avanzado.
- Aplicación móvil y multi-sucursal.
- Automatización completa de publicaciones externas.
- Microservicios, Redis, colas o base vectorial sin un requisito concreto.

## Estado verificado

- Fase 1, base de ingeniería: completada.
- Fase 2, backend inmobiliario: en ejecución.
- Modelo `Propiedad`: implementado en español.
- Ubicación geográfica: integrada en `main` mediante PR #5, commit `801f943`.
- Migración Alembic vigente: `72e21657338a`.
- Schemas Pydantic: trabajo preliminar conservado en `stash@{0}` al momento de
  este traspaso; debe verificarse antes de recuperarlo.
- Repository, Service y API REST de propiedades: pendientes.
- Frontend React: pendiente.

El estado de Git es evidencia temporal. Antes de continuar, verificar siempre:

```powershell
git branch --show-current
git status
git log -5 --oneline
git stash list
```

## Stack

- Python 3.13, FastAPI, Pydantic y Pydantic Settings.
- SQLAlchemy 2, Alembic y PostgreSQL 17.
- Pytest, Black, Ruff, mypy estricto y pre-commit.
- Docker Compose para PostgreSQL local.
- GitHub Actions para calidad, migraciones y tests.
- React, TypeScript, Vite y Tailwind para el frontend planificado.
- Vitest, React Testing Library y Playwright para pruebas futuras.
- Pillow y almacenamiento S3-compatible para imágenes futuras.

## Arquitectura resumida

Se utiliza un monolito modular. FastAPI expondrá `/api/v1`; los módulos de
propiedades, autenticación y auditoría compartirán una capa de persistencia
SQLAlchemy sobre PostgreSQL. El frontend será una aplicación React separada.

Los mapas y las imágenes se integran mediante abstracciones externas: la base
guarda datos geográficos neutrales y referencias a objetos, no iframes de mapas
ni archivos locales persistentes en producción.

## Reglas del dominio ya fijadas

- `tipo_operacion`: `venta`, `alquiler`, `temporario`.
- `estado`: `borrador`, `publicada`, `pausada`, `reservada`, `alquilada`,
  `vendida`, `no_disponible`.
- Una propiedad nueva nace en `borrador` y con `destacada=false`.
- Latitud válida: `[-90, 90]`; longitud válida: `[-180, 180]`.
- Latitud y longitud están ambas presentes o ambas ausentes.
- `mostrar_ubicacion_exacta=false` por defecto.
- La futura API pública nunca debe revelar coordenadas exactas cuando la
  ubicación exacta esté deshabilitada.

## Flujo de trabajo

Todo cambio se desarrolla en una rama específica y se integra exclusivamente
mediante Pull Request:

```text
rama -> quality gates -> commit -> push -> PR -> CI -> revisión -> squash merge
```

Convenciones: `feat/*`, `fix/*`, `chore/*`, `test/*`, `docs/*` y
`refactor/*`. Se deben stagear únicamente los archivos correspondientes al
cambio; nunca mezclar trabajo no relacionado.

## Ejecución local

```powershell
docker compose up -d
Set-Location backend
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m pytest -q
```

Alembic y los quality gates del backend deben ejecutarse desde `backend`.

## Quality gates

```powershell
# Desde backend
.\.venv\Scripts\python.exe -m black --check .
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy app tests
.\.venv\Scripts\python.exe -m pytest -q

# Desde la raíz
Set-Location ..
.\backend\.venv\Scripts\python.exe -m pre_commit run --all-files
git diff --check
git status
```

CI utiliza PostgreSQL 17 y valida `upgrade head -> downgrade base -> upgrade
head` antes de ejecutar las pruebas.

## Documentación relacionada

- [Decisiones arquitectónicas](ARCHITECTURE_DECISIONS.md)
- [Roadmap](ROADMAP.md)
- [Próximos pasos](TODO.md)
