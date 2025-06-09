# Scraper Deportes - Docker Setup

## Estructura del Proyecto Dockerizado

scraper-deportes-devops/
├── Dockerfile
├── Dockerfile.dev
├── docker-compose.yml
├── docker-compose.dev.yml
├── .dockerignore
├── .env.example
├── Makefile
└── .github/workflows/ci-cd.yml

## Inicio Rápido

### 1. Clonar y configurar
```bash
git clone https://github.com/AndresPlazas19931504/scrapper-deportes-devops.git
cd scrapper-deportes-devops
cp .env.example .env
```

### 2. Ejecutar con Docker Compose
```bash

docker-compose up -d

docker-compose logs -f

docker-compose down
```

### 3. Usando Makefile (recomendado)
```bash
make help

make build

make run

make run-dev

make logs

make test

make clean
```

##Comandos Útiles

### Gestión de contenedores
```bash
make build

make run

make restart

make stats

make shell
```

### Desarrollo
```bash
make install

make test-cov

make format

make lint

make check
```

### Limpieza
```bash
make clean

make clean-all
```

## Configuración

### Variables de Entorno
Copia `.env.example` a `.env` y configura:

```bash

LOG_LEVEL=INFO
BASE_URL = https://tu-sitio-deportes.com
REQUEST_DELAY = 1

DB_HOST=postgres
DB_NAME=scraper_db

SLACK_WEBHOOK_URL=tu-webhook
```

### Desarrollo Local
Para desarrollo con hot-reload:

```bash
make run-dev

docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Monitoreo

### Health Checks
```bash
make health

make stats

make logs
```

### Debugging
El contenedor de desarrollo incluye debugpy en el puerto 5678:
```bash

make run-dev

# Conectar debugger a localhost:5678
```

##CI/CD Pipeline

El pipeline incluye:

1. **Testing**: Ejecuta tests en Python 3.9, 3.10, 3.11
2. **Security Scan**: Análisis con Trivy
3. **Build & Push**: Construcción multi-arch y push a GHCR
4. **Deploy**: Configuración lista para despliegue

### Configurar GitHub Container Registry

```bash

make push

```

## Arquitectura

### Imagen Base
- Python 3.11 slim
- Usuario no-root para seguridad
- Dependencias mínimas del sistema

### Volúmenes
- `./data:/app/data` - Datos persistentes
- `./logs:/app/logs` - Logs de aplicación

### Redes
- Red interna para comunicación entre servicios
- Puertos expuestos según necesidad

## Seguridad

### Características implementadas:
- Usuario no-root en contenedor
- Análisis de vulnerabilidades con Trivy
- Imagen multi-stage para reducir superficie de ataque
- Variables de entorno para secretos

### Recomendaciones:
```bash
docker run --rm -v $(pwd):/app aquasec/trivy fs /app

pip-audit
```

## Optimización

### Cache de Docker
El Dockerfile está optimizado para:
- Cache de layers por separación de dependencias
- Multi-stage builds
- Imágenes slim

### Performance
```bash
docker-compose up -d --scale scraper=2

docker stats
```

## Troubleshooting

### Problemas comunes:

1. **Puerto ocupado**
```bash

ports:
  - "8001:8000"
```

2. **Permisos de volúmenes**
```bash

mkdir -p data logs
sudo chown -R 1000:1000 data logs
```

3. **Memoria insuficiente**
```bash

deploy:
  resources:
    limits:
      memory: 1G
```

## Logs

### Ubicación de logs:
- Aplicación: `./logs/app.log`
- Docker: `docker-compose logs`
- Sistema: `journalctl -u docker`

### Configurar logging:
```bash
# Nivel de logs
export LOG_LEVEL=DEBUG

# Formato estructurado
export LOG_FORMAT=json
```
