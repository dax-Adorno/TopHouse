# TopHouse

Plataforma web para la gestión y publicación de propiedades de Inmobiliaria Samanta.

## Documentación operativa

- [Contexto del proyecto](docs/PROJECT_CONTEXT.md)
- [Decisiones arquitectónicas](docs/ARCHITECTURE_DECISIONS.md)
- [Roadmap](docs/ROADMAP.md)
- [Próximos pasos](docs/TODO.md)

## Objetivo

Centralizar la administración de propiedades, optimizar imágenes, publicar inmuebles y facilitar las consultas comerciales desde una aplicación web segura y escalable.

## Requisitos de desarrollo

- Python 3.13
- Git
- Docker y Docker Compose
- Node.js, que se configurará al iniciar el frontend

## Stack tecnológico

### Frontend

- React
- TypeScript
- Vite
- Vitest
- React Testing Library
- Playwright

### Backend

- FastAPI
- Pydantic
- SQLAlchemy 2
- Alembic
- Pytest

### Infraestructura

- PostgreSQL
- Docker
- Docker Compose
- Object Storage compatible con S3
- GitHub Actions

## Arquitectura

El proyecto utilizará un monolito modular:

```text
TopHouse/
├── backend/
├── frontend/
├── docs/
├── infra/
├── .github/
│   └── workflows/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Backend

## Calidad de código

El proyecto utiliza pre-commit para ejecutar controles automáticos antes de cada commit.

Después de instalar las dependencias de desarrollo, instalar los hooks de Git:

```powershell
pre-commit install
```

El backend utiliza FastAPI y Python 3.13.

## Development Workflow

TopHouse follows a branch-based development workflow designed to keep `main` stable and production-ready.

```text
feature / fix / chore / test branch
              ↓
      Local quality gates
              ↓
            Commit
              ↓
             Push
              ↓
        Pull Request
              ↓
       GitHub Actions
              ↓
        CI validation
              ↓
        Merge to main
```

### Branch conventions

- `feat/*` — new functionality
- `fix/*` — bug fixes
- `chore/*` — tooling, maintenance and infrastructure
- `test/*` — automated testing work
- `docs/*` — documentation changes
- `refactor/*` — internal improvements without changing expected behavior

## Backend Quality Gates

The backend uses automated quality controls locally and in CI.

### Formatting

- **Black** is the official Python formatter.
- CI executes Black in `--check` mode and fails if formatting is inconsistent.

### Linting

- **Ruff** performs linting, import validation and static code-quality checks.

### Static typing

- **mypy** runs in strict mode.
- Pydantic's mypy plugin is enabled for settings and schema validation.

### Automated tests

- **Pytest** is used for backend automated tests.
- Integration tests validate the application against a real PostgreSQL database.
- Database tests verify the expected schema and Alembic revision.

### Database integration and migration testing

TopHouse validates the PostgreSQL schema against a real PostgreSQL 17
instance during Continuous Integration.

The backend integration tests verify:

- connectivity with PostgreSQL;
- existence of the expected `propiedades` table;
- expected property-domain columns;
- absence of the legacy `properties` table;
- synchronization between the database revision and Alembic `head`.

The CI pipeline also validates migration reversibility using:

```text
PostgreSQL clean database
        ↓
Alembic upgrade head
        ↓
Alembic downgrade base
        ↓
Alembic upgrade head
        ↓
Integration tests
        ↓
CI passed
```

### Crear el entorno virtual

Desde la raíz del proyecto:

```powershell
py -3.13 -m venv backend\.venv
```

### Cargar datos demo locales

Con la base de datos levantada y migrada, desde `backend`:

```powershell
.\.venv\Scripts\python.exe -m app.dev_seed
```

El seed es idempotente: crea o actualiza las propiedades demo sin duplicarlas.
También crea un administrador local de desarrollo:

```text
Email: admin.demo@tophouse.com
Contraseña: TopHouse-demo-2026
```

No ejecutar este seed con `APP_ENV=production`.

## Frontend local

El frontend se ejecuta con pnpm. Desde `frontend`, copiá `frontend/.env.example`
a `frontend/.env` si necesitás ajustar la API o el contacto comercial:

```text
VITE_API_URL=http://localhost:8000
VITE_CONTACT_EMAIL=contacto@tophouse.com
VITE_WHATSAPP_NUMBER=5492664000000
```

`VITE_WHATSAPP_NUMBER` debe cargarse en formato internacional, sólo números.

### Comandos de calidad frontend

Desde `frontend`:

```powershell
pnpm run format:check
pnpm run typecheck
pnpm run lint
pnpm run test
pnpm run build
pnpm run test:e2e
```

La primera vez que se ejecuten pruebas E2E localmente puede ser necesario
instalar el navegador de Playwright:

```powershell
pnpm exec playwright install chromium
```
