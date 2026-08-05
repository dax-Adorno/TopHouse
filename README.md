
# TopHouse

Plataforma web para la gestión y publicación de propiedades de Inmobiliaria Samanta.

## Objetivo

Centralizar la administración de propiedades, optimizar imágenes, publicar inmuebles y facilitar las consultas comerciales desde una aplicación web segura y escalable.

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
