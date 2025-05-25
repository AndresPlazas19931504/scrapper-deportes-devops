# src/scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os # Necesario para crear directorios si se guarda el CSV

# Headers para la solicitud HTTP
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}

def fetch_premier_league_html(url: str) -> bytes:
    """
    Realiza una solicitud HTTP a la URL de la Premier League y retorna el contenido HTML como bytes.
    Lanza una excepción si la solicitud no es exitosa.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Lanza HTTPError para códigos de estado 4xx/5xx
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página de la Premier League: {e}")
        raise # Re-lanza la excepción para manejo en un nivel superior o en las pruebas

def parse_premier_league_standings(html_content: bytes) -> pd.DataFrame:
    """
    Parsea el contenido HTML de la página de posiciones de la Premier League
    y retorna un DataFrame de pandas con los datos combinados.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Tabla 1: Posición, Abreviatura, Nombre del equipo
    tabla_posiciones1 = soup.find("table", {"class": "Table Table--align-right Table--fixed Table--fixed-left"})
    if not tabla_posiciones1:
        raise ValueError("No se encontró la primera tabla de posiciones en el HTML.")

    filas1 = tabla_posiciones1.find_all("tr", {"class": ["Table__TR Table__TR--sm Table__even", "filled Table__TR Table__TR--sm Table__even"]})
    posiciones = []
    abreviaturas = []
    nombres = []
    for fila in filas1:
        posicion_tag = fila.find("span", {"class": "team-position ml2 pr3"})
        nombre_equipo_tag = fila.find("span", {"class": "hide-mobile"})
        abreviatura_equipo_tag = fila.find("span", {"class": "dn show-mobile"})

        posiciones.append(posicion_tag.get_text(strip=True) if posicion_tag else None)
        nombres.append(nombre_equipo_tag.get_text(strip=True) if nombre_equipo_tag else None)
        abreviaturas.append(abreviatura_equipo_tag.get_text(strip=True) if abreviatura_equipo_tag else None)

    df1 = pd.DataFrame({"Posición": posiciones, "Avr": abreviaturas, "Nombre": nombres})

    # Tabla 2: Estadísticas detalladas
    tabla_posiciones2 = soup.find("table", {"class": "Table Table--align-right"})
    if not tabla_posiciones2:
        raise ValueError("No se encontró la segunda tabla de posiciones en el HTML.")

    tbody = tabla_posiciones2.find("tbody", {"class": "Table__TBODY"})
    if not tbody:
        raise ValueError("No se encontró el cuerpo de la segunda tabla.")

    filas2 = tbody.find_all("tr", {"class": ["Table__TR Table__TR--sm Table__even", "filled Table__TR Table__TR--sm Table__even"]})
    datos_por_idx = {}
    for fila in filas2:
        data_idx = fila.get("data-idx")
        if data_idx is None:
            continue
        stat_cells = fila.find_all("span", {"class": "stat-cell"})
        if data_idx not in datos_por_idx:
            datos_por_idx[data_idx] = []
        datos_por_idx[data_idx].extend([cell.get_text(strip=True) for cell in stat_cells])

    # Convertir a DataFrame y transponer
    if not datos_por_idx:
        df2 = pd.DataFrame()
    else:
        # Crea df2 a partir del diccionario, transpone y resetea el índice para poder concatenar.
        df2 = pd.DataFrame.from_dict(datos_por_idx, orient='index')
        df2 = df2.reset_index(drop=True)

    # Asegurarse de que ambos DataFrames tengan el mismo número de filas para la concatenación
    # Si hay un desajuste, Pandas puede llenar con NaN. Es importante que la lógica de tu scraper
    # asuma que las filas de ambas tablas corresponden.
    if len(df1) != len(df2):
        print(f"Advertencia: El número de filas de las tablas no coincide. df1: {len(df1)}, df2: {len(df2)}")
        # Para evitar errores en la concatenación si las filas no coinciden perfectamente,
        # se puede optar por un merge si hubiera una clave común, o forzar una alineación.
        # Aquí, simplemente concatenamos por índice, y Pandas manejará los NaNs.

    # Concatenar los DataFrames
    df_final = pd.concat([df1, df2], axis=1)

    # Renombrar columnas
    nuevos_nombres_columnas = {
        'Posición': 'Posicion',
        'Avr': 'Abreviatura',
        'Nombre': 'Equipo',
        0: 'Número de partidos jugados',
        1: 'El número de partidos ganados',
        2: 'Empate',
        3: 'Derrotas',
        4: 'Goles a favor',
        5: 'Goles en contra',
        6: 'Diferencia de puntos',
        7: 'Puntos'
    }
    df_final = df_final.rename(columns=nuevos_nombres_columnas)

    # Convertir columnas numéricas a tipo numérico
    num_cols = [
        'Posicion', 'Número de partidos jugados', 'El número de partidos ganados',
        'Empate', 'Derrotas', 'Goles a favor', 'Goles en contra',
        'Diferencia de puntos', 'Puntos'
    ]
    for col in num_cols:
        if col in df_final.columns:
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce') # 'coerce' convierte errores a NaN

    return df_final

def save_dataframe_to_csv(df: pd.DataFrame, filepath: str):
    """Guarda un DataFrame de pandas en un archivo CSV."""
    try:
        # Asegura que el directorio exista antes de intentar guardar el archivo
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False)
        print(f"Datos guardados exitosamente en {filepath}")
    except Exception as e:
        print(f"Error al guardar los datos en CSV: {e}")
        raise # Re-lanza la excepción

if __name__ == "__main__":
    # Este bloque solo se ejecutará cuando el script sea llamado directamente (ej. python src/scraper.py)
    # y NO cuando sus funciones sean importadas por otros scripts (como los de prueba).
    PREMIER_LEAGUE_URL = "https://www.espn.com.co/futbol/posiciones/_/liga/eng.1"
    output_path = os.path.join("data", "premier_league_standings.csv") # La ruta donde se guardará el CSV

    try:
        print(f"Iniciando scraping de la Premier League desde: {PREMIER_LEAGUE_URL}")
        html_content = fetch_premier_league_html(PREMIER_LEAGUE_URL)
        df_standings = parse_premier_league_standings(html_content)

        print("\nScraping completado. Previsualización del DataFrame:")
        print(df_standings.head()) # Muestra las primeras filas del DataFrame

        save_dataframe_to_csv(df_standings, output_path)
        print(f"\nProceso finalizado. Datos disponibles en: {output_path}")

    except Exception as e:
        print(f"\nHa ocurrido un error durante la ejecución del scraper: {e}")
        # Aquí puedes añadir un logging más detallado si es necesario
        import traceback
        traceback.print_exc() # Imprime el stack trace completo del error
