# scrapper-deportes-devops
# Scraper de Posiciones de la Premier League con CI/CD

Este proyecto implementa un scraper automatizado para extraer las tablas de posiciones de la Premier League desde [ESPN.com.co](https://www.espn.com.co/futbol/posiciones/_/liga/eng.1). Utiliza un robusto pipeline de DevOps con **GitHub Actions** para asegurar la calidad del código, la ejecución automatizada y el despliegue continuo de los datos.

## **Descripción General**

El scraper está diseñado para obtener información clave de la Premier League, incluyendo:

* **Detalles del Equipo**: Posición en la tabla, abreviatura y nombre completo del equipo.
* **Estadísticas de Partidos**: Número de partidos jugados, ganados, empatados y perdidos.
* **Detalles de Goles**: Goles a favor, goles en contra y diferencia de puntos.
* **Puntos Totales**.

El objetivo principal es proporcionar datos actualizados y confiables de la liga de fútbol más competitiva, garantizando la fiabilidad a través de pruebas automatizadas y la entrega continua de datos a través de GitHub Actions.

## **Tecnologías Utilizadas**

* **Python**: Lenguaje de programación principal.
* **`requests`**: Para realizar solicitudes HTTP a la página web.
* **`BeautifulSoup4`**: Para parsear el HTML y extraer los datos estructurados.
* **`pandas`**: Para la manipulación, organización y almacenamiento de datos en DataFrames (finalmente guardados en CSV).
* **Git**: Sistema de control de versiones para gestionar el historial del código.
* **GitHub**: Plataforma para alojar el repositorio, facilitar la colaboración y configurar GitHub Actions.
* **GitHub Actions**: Motor de automatización para el pipeline de Integración Continua (CI) y Despliegue Continuo (CD).
* **`pytest`**: Framework de pruebas para escribir y ejecutar pruebas unitarias automatizadas.

## **Estructura del Repositorio**

scraper-deportes-devops/
├── requirements.txt
├── Plazas__Andres_Analizando_EA1.ipynb
├── src/
│   ├── __init__.py
│   └── scraper.py
├── tests/
│   └── test_scraper.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── data/
├── .gitignore
└── README.md

### Prerrequisitos

- Docker & Docker Compose
- Git
- Python 3.9+ (para desarrollo local)

### Instalación Rápida

```bash

# 1. Clonar el repositorio

git clone https://github.com/AndresPlazas19931504/scrapper-deportes-devops.git
cd scrapper-deportes-devops

# 2. IMPORTANTE: Configurar credenciales personales

cp .env.example .env

# Editar .env con tus credenciales personales

# 3. Construir y ejecutar

make build
make up
```

## 🔐 Configuración de Credenciales: Personalizar Credenciales

**Antes de usar este proyecto, DEBES personalizar las siguientes credenciales en el archivo `.env`:**

```bash

# Copia el archivo de ejemplo
cp .env.example .env

# Edita el archivo .env y cambia:

SCRAPER_USER=Su_usuario_aqui
EMAIL_FROM=Su_email@dominio.com
EMAIL_PASSWORD=Su_contraseña_de_aplicacion
GITHUB_TOKEN=Su_token_de_github__personal
API_KEY=Su_api_key_persona
SECRET_KEY=Su_Key_Secreta

```
## Base de Datos SQLite3

Este proyecto utiliza **SQLite3** como base de datos principal:

```
📂 db/
├── deportes_andres.db
├── backups/
└── schema.sql
```

## Comandos Disponibles

```bash

# Construcción y ejecución

make build      # Construir imagen Docker
make up         # Levantar servicios
make down       # Detener servicios
make run        # Ejecutar solo el scraper

# Desarrollo

make logs       # Ver logs en tiempo real
make shell      # Acceso shell del contenedor
make test       # Ejecutar tests
make clean      # Limpiar contenedores e imágenes

# Utilidades
make rebuild    # Reconstruir sin cache

```

## Pipeline CI/CD

### GitHub Actions Automático

El pipeline se ejecuta automáticamente cuando:
- Push a rama `main`
- Pull Request a `main`
- Push a rama `develop`

### Etapas del Pipeline:

1. ** Tests** - Ejecuta pytest con coverage
2. ** Build** - Construye imagen Docker
3. ** Push** - Sube a GitHub Container Registry
4. ** Deploy** - Despliegue automático

## Estructura del Proyecto

scraper-deportes-devops/

├── Dockerfile                 # Imagen Docker optimizada
├── docker-compose.yml         # Orquestación
├── Makefile                   # Comandos automatizados
├── .env                       # Configuración personal
├── requirements.txt           # Dependencias Python
├── .github/workflows/         # Pipeline CI/CD
├── src/                       # Código fuente
├── tests/                     # Tests automatizados
├── db/                        # Base datos SQLite
└── data/                      # Datos procesados
```

## Desarrollo Local

### Configuración del Entorno

```bash

# 1. Crear entorno virtual

venv\Scripts\activate     # Windows

# 2. Instalar dependencias

pip install -r requirements.txt

# 3. Configurar BD SQLite

python src/database.py --init

# 4. Ejecutar tests

pytest tests/ -v
```
## Docker

### Imagen Optimizada

```dockerfile

# Características:

- Python 3.9 slim
- SQLite3 integrado
- Dependencias mínimas
- Usuario no-root
- Volúmenes persistentes

```

### Volúmenes Importantes

```yaml

volumes:
  - ./db:/app/db          # Base datos persistente
  - ./logs:/app/logs      # Logs persistentes
  - ./data:/app/data      # Datos procesados

```

## Monitoreo

### Logs Disponibles

```bash
# Ver todos los logs

make logs

# Logs específicos

docker-compose logs scraper-deportes-andres

# Logs de errores

tail -f logs/error.log
```

### Health Check

```bash
# Verificar estado del contenedor

docker-compose ps

# Ejecutar health check manual

python scripts/health_check.py
```
