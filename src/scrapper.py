# src/scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Headers para la solicitud HTTP
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}

def fetch_premier_league_html(url: str) -> str:
    """
    Realiza una solicitud HTTP a la URL de la Premier League y retorna el contenido HTML.
    Lanza una excepción si la solicitud no es exitosa.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Lanza HTTPError para códigos de estado 4xx/5xx
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página de la Premier League: {e}")
        raise # Vuelve a lanzar la excepción para que pueda ser capturada en un nivel superior o en las pruebas

def parse_premier_league_standings(html_content: bytes) -> pd.DataFrame:
    """
    Parsea el contenido HTML de la página de posiciones de la Premier League
    y retorna un DataFrame de pandas con los datos combinados.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Tabla 1: Posición, Abreviatura, Nombre
    tabla_posiciones1 = soup.find("table", {"class": "Table Table--align-right Table--fixed Table--fixed-left"})
    if not tabla_posiciones1:
        raise ValueError("No se encontró la primera tabla de posiciones en el HTML.")

    filas1 = tabla_posiciones1.find_all("tr", {"class": ["Table__TR Table__TR--sm Table__even", "filled Table__TR Table__TR--sm Table__even"]})
    posiciones = []
    abreviaturas = []
    nombres = []
    for fila in filas1:
        # Usamos .get_text(strip=True) para limpiar espacios en blanco
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

    # Convertir a DataFrame y transponer, manejando caso de datos vacíos
    if not datos_por_idx:
        df2 = pd.DataFrame()
    else:
        df2 = pd.DataFrame(datos_por_idx).T

    # Asegurarse de que ambos DataFrames tengan el mismo número de filas para la concatenación
    # Esto puede ser un punto de fallo si la estructura HTML no es consistente
    if len(df1) != len(df2):
        print(f"Advertencia: El número de filas de las tablas no coincide. df1: {len(df1)}, df2: {len(df2)}")
        # Aquí podrías implementar una lógica para alinear los DataFrames,
        # como un merge por alguna clave común si existiera, o simplemente un manejo de error.
        # Por ahora, simplemente reseteamos el índice y concatenamos.

    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)

    df_final = pd.concat([df1, df2], axis=1)

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
    # Esto es crucial para análisis o futuras operaciones de DB
    num_cols = [
        'Posicion', 'Número de partidos jugados', 'El número de partidos ganados',
        'Empate', 'Derrotas', 'Goles a favor', 'Goles en contra',
        'Diferencia de puntos', 'Puntos'
    ]
    for col in num_cols:
        if col in df_final.columns:
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce') # 'coerce' convierte errores a NaN

    return df_final

def run_scraper(url: str) -> pd.DataFrame:
    """
    Función principal para ejecutar el scraper, obtener, parsear y retornar los datos.
    """
    html_content = fetch_premier_league_html(url)
    df_standings = parse_premier_league_standings(html_content)
    return df_standings

if __name__ == "__main__":
    # Este bloque solo se ejecutará cuando el script sea llamado directamente (ej. python src/scraper.py)
    # No se ejecutará cuando se importen las funciones para pruebas.
    PREMIER_LEAGUE_URL = "https://www.espn.com.co/futbol/posiciones/_/liga/eng.1"
    try:
        final_df = run_scraper(PREMIER_LEAGUE_URL)
        print("Scraping completado. DataFrame obtenido:")
        print(final_df.head()) # Muestra las primeras filas del DataFrame

        # Aquí es donde podrías agregar la lógica para guardar a CSV o DB si se ejecuta manualmente,
        # pero para el pipeline, el job de despliegue se encargará de esto.
        output_dir = "data"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "premier_league_standings.csv")
        final_df.to_csv(output_path, index=False)
        print(f"Datos guardados en: {output_path}")

    except Exception as e:
        print(f"Ha ocurrido un error durante la ejecución del scraper: {e}")

# Dentro de src/scraper.py, al final
def save_dataframe_to_csv(df: pd.DataFrame, filepath: str):
    """Guarda un DataFrame de pandas en un archivo CSV."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True) # Asegura que el directorio exista
        df.to_csv(filepath, index=False)
        print(f"Datos guardados exitosamente en {filepath}")
    except Exception as e:
        print(f"Error al guardar los datos en CSV: {e}")
        raise # Vuelve a lanzar la excepción

# Y en tu `if __name__ == "__main__":` de src/scraper.py, úsala:
if __name__ == "__main__":
    PREMIER_LEAGUE_URL = "https://www.espn.com.co/futbol/posiciones/_/liga/eng.1"
    output_path = os.path.join("data", "premier_league_standings.csv") # O donde quieras que se guarde
    try:
        final_df = run_scraper(PREMIER_LEAGUE_URL)
        print("Scraping completado. DataFrame obtenido:")
        print(final_df.head())
        save_dataframe_to_csv(final_df, output_path)
    except Exception as e:
        print(f"Ha ocurrido un error durante la ejecución del scraper: {e}")
