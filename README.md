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
