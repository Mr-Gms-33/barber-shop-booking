.PHONY: test migrate up

test:
	cd backend && pytest -q
	cd frontend && npm test -- --run

migrate:
	cd backend && alembic upgrade head

up:
	docker compose up --build
