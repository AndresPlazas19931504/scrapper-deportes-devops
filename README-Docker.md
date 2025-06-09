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
cp .env.example .env  # Configurar variables de entorno
```

### 2. Ejecutar con Docker Compose
```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### 3. Usando Makefile (recomendado)
```bash
# Ver todos los comandos disponibles
make help

# Construir imagen
make build

# Ejecutar en producción
make run

# Ejecutar en desarrollo
make run-dev

# Ver logs
make logs

# Ejecutar tests
make test

# Limpiar sistema
make clean
```

## 🛠️ Comandos Útiles

### Gestión de contenedores
```bash
# Construir imagen
make build

# Ejecutar en background
make run

# Reiniciar servicios
make restart

# Ver estadísticas
make stats

# Acceder al shell
make shell
```

### Desarrollo
```bash
# Instalar dependencias localmente
make install

# Ejecutar tests con cobertura
make test-cov

# Formatear código
make format

# Linter
make lint

# Verificar código completo
make check
```

### Limpieza
```bash
# Limpiar imágenes no utilizadas
make clean

# Limpiar todo (¡cuidado!)
make clean-all
```

## 🔧 Configuración

### Variables de Entorno
Copia `.env.example` a `.env` y configura:

```bash
# Scraping
LOG_LEVEL=INFO
BASE_URL=https://tu-sitio-deportes.com
REQUEST_DELAY=1

# Base de datos (opcional)
DB_HOST=postgres
DB_NAME=scraper_db

# Notificaciones (opcional)
SLACK_WEBHOOK_URL=tu-webhook
```

### Desarrollo Local
Para desarrollo con hot-reload:

```bash
# Usar configuración de desarrollo
make run-dev

# O directamente
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 📊 Monitoreo

### Health Checks
```bash
# Verificar salud del contenedor
make health

# Ver estadísticas en tiempo real
make stats

# Inspeccionar logs
make logs
```

### Debugging
El contenedor de desarrollo incluye debugpy en el puerto 5678:

```bash
# Ejecutar en modo debug
make run-dev

# Conectar debugger a localhost:5678
```

## 🔄 CI/CD Pipeline

El pipeline incluye:

1. **Testing**: Ejecuta tests en Python 3.9, 3.10, 3.11
2. **Security Scan**: Análisis con Trivy
3. **Build & Push**: Construcción multi-arch y push a GHCR
4. **Deploy**: Configuración lista para despliegue

### Configurar GitHub Container Registry

```bash
# Dar permisos al repositorio
# Settings > Actions > General > Workflow permissions > Read and write

# Push manual
make push
```

## 🏗️ Arquitectura

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

## 🛡️ Seguridad

### Características implementadas:
- Usuario no-root en contenedor
- Análisis de vulnerabilidades con Trivy
- Imagen multi-stage para reducir superficie de ataque
- Variables de entorno para secretos

### Recomendaciones:
```bash
# Escanear vulnerabilidades localmente
docker run --rm -v $(pwd):/app aquasec/trivy fs /app

# Actualizar dependencias regularmente
pip-audit
```

## 📈 Optimización

### Cache de Docker
El Dockerfile está optimizado para:
- Cache de layers por separación de dependencias
- Multi-stage builds
- Imágenes slim

### Performance
```bash
# Limitar recursos en producción
docker-compose up -d --scale scraper=2

# Monitorear uso
docker stats
```

## 🐛 Troubleshooting

### Problemas comunes:

1. **Puerto ocupado**
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"
```

2. **Permisos de volúmenes**
```bash
# Crear directorios con permisos correctos
mkdir -p data logs
sudo chown -R 1000:1000 data logs
```

3. **Memoria insuficiente**
```bash
# Aumentar límites en docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
```

## 📝 Logs

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
