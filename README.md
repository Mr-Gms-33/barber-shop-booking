<div align="center">

# Barber Shop Booking

**Full-stack online booking product**

Booking flows for a single barber shop — clean API, modern frontend, and production-minded packaging.

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Portfolio](https://img.shields.io/badge/Portfolio-mounir--gmamsi-1b3550?style=for-the-badge&logo=netlify&logoColor=white)](https://mounir-gmamsi.netlify.app/)

</div>

---

## Overview

Barber Shop Booking is a full-stack application for online appointments. It separates backend API concerns from the React UI and includes Docker-based local delivery, authentication-related backend components, and observability hooks.

---

## What the product delivers

| Capability | Description |
|------------|-------------|
| Booking flows | Create and manage appointments for a single shop |
| API layer | Structured REST API with validated models |
| Frontend UX | React SPA for customer / shop interaction |
| Persistence | Relational storage with migrations |
| Local ops | Docker Compose for end-to-end startup |
| Quality | Tests and observability instrumentation |

---

## Technology stack

### Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square)
![Alembic](https://img.shields.io/badge/Alembic-7A7A7A?style=flat-square)

### Frontend

![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)
![Vitest](https://img.shields.io/badge/Vitest-6E9F18?style=flat-square&logo=vitest&logoColor=white)

### Platform

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat-square&logo=nginx&logoColor=white)
![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-000000?style=flat-square&logo=opentelemetry&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)

| Layer | Technologies |
|-------|----------------|
| API | FastAPI, Uvicorn, Pydantic, SQLAlchemy, Alembic, PostgreSQL |
| UI | React, TypeScript, Vite |
| Security | python-jose, passlib / bcrypt |
| Ops | Docker Compose, Nginx, OpenTelemetry, Prometheus client |

---

## Solution flow

| Step | Stage | Technologies |
|:----:|-------|--------------|
| 1 | User opens booking UI | React, Vite |
| 2 | API validates request | FastAPI, Pydantic |
| 3 | Persist booking data | SQLAlchemy, PostgreSQL |
| 4 | Return confirmation to UI | REST JSON |
| 5 | Observe system health | OpenTelemetry / metrics |

```mermaid
flowchart TD
  A[1. Booking UI] --> B[2. FastAPI request]
  B --> C[3. Database write or read]
  C --> D[4. Response to UI]
  B --> E[5. Telemetry]
```

---

## Repository structure

| Path | Purpose |
|------|---------|
| `backend/` | FastAPI application, migrations, tests |
| `frontend/` | React + Vite client |
| `docker-compose.yml` | Local multi-service stack |
| `docs/` | Project documentation |
| `observability/` | Observability configuration |

---

## Run locally

```bash
copy .env.example .env
docker compose up --build
```

See `Makefile` and `docs/` for additional development commands.

---

## Author

**Mounir Gmamsi**  
[Portfolio](https://mounir-gmamsi.netlify.app/) · [GitHub](https://github.com/Mr-Gms-33) · [LinkedIn](https://www.linkedin.com/in/mounir-gmamsi-1595951b3)
