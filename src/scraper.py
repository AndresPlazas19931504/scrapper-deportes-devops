import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys

ESPN_PREMIER_LEAGUE_URL = "https://www.espn.com.co/futbol/posiciones/_/liga/eng.1"

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
        response = requests.get(url, headers=HEADERS, timeout=10)
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
    soup = BeautifulSoup(html_content, 'html.parser')

    first_table = soup.find('table', class_='Table Table--align-right Table--fixed Table--fixed-left')
    if not first_table:
        raise ValueError("No se encontró la primera tabla de posiciones en el HTML.")

    second_table = soup.find('table', class_='Table Table--align-right')
    if not second_table:
        raise ValueError("No se encontró la segunda tabla de posiciones (estadísticas) en el HTML.")

    teams_data = []

    rows1 = first_table.find('tbody').find_all('tr', class_=['Table__TR', 'Table__TR--sm', 'Table__even', 'filled'])
    
    if not rows1:
        print("ADVERTENCIA: No se encontraron filas en la primera tabla de equipos.", file=sys.stderr)

    for row in rows1:
        position_span = row.find('span', class_='team-position ml2 pr3')
        full_name_span = row.find('span', class_='hide-mobile')
        abbreviation_span = row.find('span', class_='dn show-mobile')

        position = position_span.text.strip() if position_span else ''
        full_name = full_name_span.text.strip() if full_name_span else ''
        abbreviation = abbreviation_span.text.strip() if abbreviation_span else ''
        
        if position.isdigit(): # Para asegurar que solo se añaden filas de equipo válidas
            teams_data.append({
                'Posicion': int(position),
                'Abreviatura': abbreviation,
                'Equipo': full_name
            })
        else:
            print(f"DEBUG: Fila de equipo ignorada (posición no numérica): {row.prettify()}", file=sys.stderr)

    stats_data = []
    
    rows2 = second_table.find('tbody').find_all('tr', class_=['Table__TR', 'Table__TR--sm', 'Table__even', 'filled'])
    
    if not rows2:
        print("ADVERTENCIA: No se encontraron filas en la segunda tabla de estadísticas.", file=sys.stderr)

    for row in rows2:
    
        td_cells = row.find_all('td', class_='Table__TD')
        
        cells_text = []
        for td in td_cells:
            stat_span = td.find('span', class_='stat-cell')
            if stat_span:
                cells_text.append(stat_span.text.strip())

        if len(cells_text) == 8: 
            try:
                stats_data.append({
                    'Número de partidos jugados': int(cells_text[0]),
                    'El número de partidos ganados': int(cells_text[1]),
                    'Empate': int(cells_text[2]),
                    'Derrotas': int(cells_text[3]),
                    'Goles a favor': int(cells_text[4]),
                    'Goles en contra': int(cells_text[5]),
                    'Diferencia de puntos': int(cells_text[6].replace('+', '').replace('-', '')), # Limpiar signos
                    'Puntos': int(cells_text[7])
                })
            except ValueError as ve:
                print(f"ADVERTENCIA: Error al convertir estadísticas a entero en fila: {row.prettify()} - Error: {ve}", file=sys.stderr)
        else:

            print(f"DEBUG: Fila de estadísticas ignorada (no 8 elementos de texto stat-cell): {row.prettify()}", file=sys.stderr)

    if len(teams_data) != len(stats_data):
        print(f"ADVERTENCIA: Número de equipos y estadísticas no coinciden. Equipos: {len(teams_data)}, Estadísticas: {len(stats_data)}", file=sys.stderr)

        min_len = min(len(teams_data), len(stats_data))
        teams_data = teams_data[:min_len]
        stats_data = stats_data[:min_len]
        if not teams_data: # Si después de truncar no queda nada
            raise ValueError("No se pudieron extraer datos consistentes de las tablas.")


    df_teams = pd.DataFrame(teams_data)
    df_stats = pd.DataFrame(stats_data)

    df_final = pd.concat([df_teams, df_stats], axis=1)

    nuevos_nombres_columnas = {
        'Posicion': 'Posicion',
        'Abreviatura': 'Abreviatura',
        'Equipo': 'Equipo',
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

    num_cols = [
        'Posicion', 'Número de partidos jugados', 'El número de partidos ganados',
        'Empate', 'Derrotas', 'Goles a favor', 'Goles en contra',
        'Diferencia de puntos', 'Puntos'
    ]

    for col in num_cols:
        if col in df_final.columns:
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

    return df_final

def save_dataframe_to_csv(df: pd.DataFrame, output_path: str):
    """
    Guarda el DataFrame de posiciones en un archivo CSV.

    Args:
        df (pd.DataFrame): El DataFrame a guardar.
        output_path (str): La ruta completa del archivo CSV de salida.
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"DEBUG: Creado directorio: {output_dir}")

    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"DEBUG: Datos guardados exitosamente en {output_path}")

if __name__ == "__main__":
    print("Iniciando el scraper de la Premier League...")
    try:
        html_content = fetch_premier_league_html(ESPN_PREMIER_LEAGUE_URL)

        standings_df = parse_premier_league_standings(html_content)
        print("DEBUG: DataFrame de posiciones generado:")
        print(standings_df.head()) # Imprime las primeras filas para depuración

        output_path = os.path.join("data", "premier_league_standings.csv")
        save_dataframe_to_csv(standings_df, output_path)

        print("Scraping y guardado completados exitosamente.")

    except Exception as e:
        print(f"ERROR: Ha ocurrido un error crítico durante el scraping: {e}", file=sys.stderr)
        sys.exit(1) # Salir con un código de error
