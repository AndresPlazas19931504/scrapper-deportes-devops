# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para scraping y SQLite3
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/ ./src/
COPY data/ ./data/

# Crear directorios necesarios para SQLite
RUN mkdir -p /app/db /app/logs && chown -R root:root /app

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 scraper && chown -R scraper:scraper /app
USER scraper

# Exponer puerto (opcional, para APIs futuras)
EXPOSE 8000

# Comando por defecto
CMD ["python", "-m", "src.scraper"]
