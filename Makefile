.PHONY: up down seed test build

up:
	docker compose up --build

down:
	docker compose down

seed:
	docker compose run --rm backend python -m app.services.producer

test:
	cd backend && pytest
	cd frontend && npm run build

build:
	docker compose build
