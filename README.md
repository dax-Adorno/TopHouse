
# TopHouse

Plataforma web para la gestión y publicación de propiedades de Inmobiliaria Samanta.

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

Branch conventions
feat/* — new functionality
fix/* — bug fixes
chore/* — tooling, maintenance and infrastructure
test/* — automated testing work
docs/* — documentation changes
refactor/* — internal improvements without changing expected behavior
Backend Quality Gates

The backend uses automated quality controls locally and in CI.

Formatting
Black is the official Python formatter.
CI executes Black in --check mode and fails if formatting is inconsistent.
Linting
Ruff performs linting, import validation and static code-quality checks.
Static typing
mypy runs in strict mode.
Pydantic's mypy plugin is enabled for settings and schema validation.
Automated tests
Pytest is used for backend tests.
Integration coverage will include PostgreSQL and database migrations.
Database validation
PostgreSQL 17 runs as an isolated service inside GitHub Actions.
Alembic applies all database migrations up to head.
CI verifies that a clean PostgreSQL instance can reproduce the current schema.
Local pre-commit checks

Before a commit is accepted, pre-commit validates:

trailing whitespace
end-of-file consistency
YAML and TOML syntax
merge-conflict markers
large files
accidental private keys
Ruff
Black
Continuous Integration

GitHub Actions automatically validates backend changes using:

Python 3.13
    ↓
Install dependencies
    ↓
Black --check
    ↓
Ruff
    ↓
mypy
    ↓
PostgreSQL 17
    ↓
Alembic upgrade head
    ↓
Pytest
    ↓
CI passed

A change is considered ready for main only after its required quality gates pass.
### Crear el entorno virtual

Desde la raíz del proyecto:

```powershell
py -3.13 -m venv backend\.venv
```
