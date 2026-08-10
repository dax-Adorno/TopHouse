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

El backend utiliza FastAPI y Python 3.13.

### Crear el entorno virtual

Desde la raíz del proyecto:

```powershell
py -3.13 -m venv backend\.venv
```
