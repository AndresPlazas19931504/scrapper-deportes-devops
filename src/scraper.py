import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys

# La URL de la página de la Premier League de ESPN
ESPN_PREMIER_LEAGUE_URL = "https://www.espn.com.co/futbol/posiciones/_/liga/eng.1"

# Headers para simular una petición de navegador. Esencial para evitar bloqueos.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_premier_league_html(url: str) -> bytes:
    """
    Realiza una petición HTTP GET a la URL de la Premier League de ESPN
    y retorna el contenido HTML en bytes.

    Args:
        url (str): La URL de la página a la que hacer la petición.

    Returns:
        bytes: El contenido HTML de la página en bytes.

    Raises:
        requests.exceptions.RequestException: Si la petición falla (ej. error HTTP, error de conexión).
    """
    try:
        # Realiza la petición GET con los headers definidos
        response = requests.get(url, headers=HEADERS, timeout=10)
        # Lanza una excepción para códigos de estado HTTP erróneos (4xx o 5xx)
        response.raise_for_status()
        print(f"DEBUG: Petición exitosa a {url}")
        return response.content
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: Error HTTP al acceder a {url}: {e}", file=sys.stderr)
        raise
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Error de conexión al acceder a {url}: {e}", file=sys.stderr)
        raise
    except requests.exceptions.Timeout as e:
        print(f"ERROR: Tiempo de espera agotado al acceder a {url}: {e}", file=sys.stderr)
        raise
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error inesperado al acceder a {url}: {e}", file=sys.stderr)
        raise

def parse_premier_league_standings(html_content: bytes) -> pd.DataFrame:
    """
    Parsea el contenido HTML de la página de la Premier League de ESPN
    y extrae la tabla de posiciones en un DataFrame de pandas.

    Args:
        html_content (bytes): El contenido HTML de la página en bytes.

    Returns:
        pd.DataFrame: Un DataFrame de pandas con la tabla de posiciones.

    Raises:
        ValueError: Si no se encuentran las tablas esperadas en el HTML.
    """
    # Crea un objeto BeautifulSoup para parsear el HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # La página de ESPN usa dos tablas separadas para las posiciones y las estadísticas.
    # La primera tabla contiene la posición, el nombre y la abreviatura del equipo.
    # La segunda tabla contiene las estadísticas detalladas (GP, W, D, L, GF, GA, GD, PTS).

    # Intenta encontrar la primera tabla (posiciones y nombre del equipo)
    # Ajustar selectores CSS si la estructura de la página cambia.
    first_table = soup.find('table', class_='Table Table--align-right Table--fixed Table--fixed-left')
    if not first_table:
        raise ValueError("No se encontró la primera tabla de posiciones en el HTML.")

    # Intenta encontrar la segunda tabla (estadísticas detalladas)
    second_table = soup.find('table', class_='Table Table--align-right')
    if not second_table:
        raise ValueError("No se encontró la segunda tabla de posiciones (estadísticas) en el HTML.")

    # Extraer datos de la primera tabla (esta parte ya funciona bien)
    teams_data = []
    rows1 = first_table.find('tbody').find_all('tr', class_='Table__TR') # También acepta múltiples clases
    for row in rows1:
        position = row.find('span', class_='team-position ml2 pr3').text.strip()
        full_name = row.find('span', class_='hide-mobile').text.strip()
        abbreviation = row.find('span', class_='dn show-mobile').text.strip()
        
        teams_data.append({
            'Posicion': int(position),
            'Abreviatura': abbreviation,
            'Equipo': full_name
        })
		
    # Extraer datos de la segunda tabla
    stats_data = []
    rows2 = second_table.find('tbody').find_all('tr', class_='Table__TR') # También acepta múltiples clases
    for row in rows2:
        # CORRECCIÓN CLAVE AQUÍ: Buscar 'td' con la clase 'stat-cell'
        cells = row.find_all('td', class_='stat-cell') 
        
        # OJO: Si la clase 'stat-cell' está en un SPAN dentro del TD, y tú quieres el texto del TD,
        # asegúrate de extraerlo correctamente. El `.text.strip()` aplicado a `cell` (que ahora será el td)
        # extraerá todo el texto dentro de ese td, incluyendo el del span.
        
        if len(cells) == 8: # Asegura que haya 8 celdas de estadísticas
            stats_data.append({
                'Número de partidos jugados': int(cells[0].text.strip()),
                'El número de partidos ganados': int(cells[1].text.strip()),
                'Empate': int(cells[2].text.strip()),
                'Derrotas': int(cells[3].text.strip()),
                'Goles a favor': int(cells[4].text.strip()),
                'Goles en contra': int(cells[5].text.strip()),
                'Diferencia de puntos': int(cells[6].text.strip()),
                'Puntos': int(cells[7].text.strip())
            })
    # Verifica que ambas listas tengan el mismo número de elementos para poder unirlos.
    if len(teams_data) != len(stats_data):
        print(f"ADVERTENCIA: Número de equipos y estadísticas no coinciden. Equipos: {len(teams_data)}, Estadísticas: {len(stats_data)}", file=sys.stderr)
        # Aquí podrías decidir cómo manejar esto: truncar, rellenar, o lanzar un error.
        # Para evitar errores en la unión, truncamos a la lista más corta.
        min_len = min(len(teams_data), len(stats_data))
        teams_data = teams_data[:min_len]
        stats_data = stats_data[:min_len]
        if not teams_data: # Si después de truncar no queda nada
            raise ValueError("No se pudieron extraer datos consistentes de las tablas.")


    # Combina los datos en un solo DataFrame
    df_teams = pd.DataFrame(teams_data)
    df_stats = pd.DataFrame(stats_data)

    # Une los DataFrames. Asumimos que el orden de las filas es consistente en ambas tablas.
    df_final = pd.concat([df_teams, df_stats], axis=1)

    # Definir las columnas numéricas para futuras validaciones
    num_cols = [
        'Posicion', 'Número de partidos jugados', 'El número de partidos ganados',
        'Empate', 'Derrotas', 'Goles a favor', 'Goles en contra',
        'Diferencia de puntos', 'Puntos'
    ]

    # Asegurarse de que las columnas numéricas sean del tipo correcto
    for col in num_cols:
        if col in df_final.columns:
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce')
            # Si hay valores NaN después de la conversión (por errores), podrías manejarlos
            # df_final[col] = df_final[col].fillna(0) # Ejemplo: rellenar con 0

    return df_final

def save_dataframe_to_csv(df: pd.DataFrame, output_path: str):
    """
    Guarda el DataFrame de posiciones en un archivo CSV.

    Args:
        df (pd.DataFrame): El DataFrame a guardar.
        output_path (str): La ruta completa del archivo CSV de salida.
    """
    # Asegura que el directorio de salida exista
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"DEBUG: Creado directorio: {output_dir}")

    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"DEBUG: Datos guardados exitosamente en {output_path}")

if __name__ == "__main__":
    print("Iniciando el scraper de la Premier League...")
    try:
        # 1. Obtener el contenido HTML
        html_content = fetch_premier_league_html(ESPN_PREMIER_LEAGUE_URL)

        # 2. Parsear el HTML y obtener el DataFrame
        standings_df = parse_premier_league_standings(html_content)
        print("DEBUG: DataFrame de posiciones generado:")
        print(standings_df.head()) # Imprime las primeras filas para depuración

        # 3. Guardar el DataFrame en un archivo CSV
        # La ruta 'data/premier_league_standings.csv' es relativa a la raíz del repositorio
        output_path = os.path.join("data", "premier_league_standings.csv")
        save_dataframe_to_csv(standings_df, output_path)

        print("Scraping y guardado completados exitosamente.")

    except Exception as e:
        print(f"ERROR: Ha ocurrido un error crítico durante el scraping: {e}", file=sys.stderr)
        sys.exit(1) # Salir con un código de error
