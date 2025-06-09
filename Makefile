# Makefile para el proyecto scraper-deportes

.PHONY: help build run test clean logs shell

# Variables

IMAGE_NAME = scraper-deportes
CONTAINER_NAME = scraper-deportes
DOCKER_COMPOSE = docker-compose

# Ayuda

help:
	@echo "Comandos disponibles:"
	@echo "  build      - Construir la imagen Docker"
	@echo "  run        - Ejecutar el scraper"
	@echo "  up         - Levantar todos los servicios"
	@echo "  down       - Detener todos los servicios"
	@echo "  test       - Ejecutar tests"
	@echo "  logs       - Ver logs del contenedor"
	@echo "  shell      - Abrir shell en el contenedor"
	@echo "  clean      - Limpiar imágenes y contenedores"

# Construir imagen

build:
	$(DOCKER_COMPOSE) build

# Ejecutar solo el scraper

run:
	$(DOCKER_COMPOSE) up scraper-deportes

# Levantar todos los servicios

up:
	$(DOCKER_COMPOSE) up -d

# Detener servicios

down:
	$(DOCKER_COMPOSE) down

# Ejecutar tests

test:
	docker run --rm -v $(PWD):/app -w /app python:3.9-slim sh -c "pip install -r requirements.txt && python -m pytest tests/ -v"

# Ver logs

logs:
	$(DOCKER_COMPOSE) logs -f scraper-deportes

# Shell interactivo

shell:
	$(DOCKER_COMPOSE) exec scraper-deportes /bin/bash

# Limpiar

clean:
	$(DOCKER_COMPOSE) down -v
	docker system prune -f
	docker volume prune -f

# Reinstalar dependencias

rebuild:
	$(DOCKER_COMPOSE) build --no-cache
