# tests/test_scraper.py

import pytest
import requests
import pandas as pd
from unittest.mock import patch, MagicMock
import os

# Importa las funciones que vamos a probar de tu script refactorizado
from src.scraper import fetch_premier_league_html, parse_premier_league_standings, HEADERS

# --- Datos Mock para las Pruebas ---
# Este HTML es CRÍTICO. Debe reflejar la estructura de la tabla de posiciones de ESPN.
# Lo ideal es copiar el HTML relevante de una página real y simplificarlo.
# Este es un ejemplo basado en tu lógica de scraper.
MOCK_ESPN_PREMIER_LEAGUE_HTML = b"""
<!DOCTYPE html>
<html>
<head><title>ESPN Premier League Standings</title></head>
<body>
    <div id="wrapper">
        <table class="Table Table--align-right Table--fixed Table--fixed-left">
            <thead></thead>
            <tbody>
                <tr class="Table__TR Table__TR--sm Table__even">
                    <td><span class="team-position ml2 pr3">1</span></td>
                    <td><div class="team-info">
                        <span class="hide-mobile">Manchester City</span>
                        <span class="dn show-mobile">MCI</span>
                    </div></td>
                </tr>
                <tr class="Table__TR Table__TR--sm Table__even filled">
                    <td><span class="team-position ml2 pr3">2</span></td>
                    <td><div class="team-info">
                        <span class="hide-mobile">Arsenal</span>
                        <span class="dn show-mobile">ARS</span>
                    </div></td>
                </tr>
                 <tr class="Table__TR Table__TR--sm Table__even">
                    <td><span class="team-position ml2 pr3">3</span></td>
                    <td><div class="team-info">
                        <span class="hide-mobile">Liverpool</span>
                        <span class="dn show-mobile">LIV</span>
                    </div></td>
                </tr>
            </tbody>
        </table>

        <table class="Table Table--align-right">
            <thead></thead>
            <tbody class="Table__TBODY">
                <tr class="Table__TR Table__TR--sm Table__even" data-idx="0">
                    <td class="stat-cell">38</td>
                    <td class="stat-cell">28</td>
                    <td class="stat-cell">7</td>
                    <td class="stat-cell">3</td>
                    <td class="stat-cell">96</td>
                    <td class="stat-cell">34</td>
                    <td class="stat-cell">62</td>
                    <td class="stat-cell">91</td>
                </tr>
                <tr class="Table__TR Table__TR--sm Table__even filled" data-idx="1">
                    <td class="stat-cell">38</td>
                    <td class="stat-cell">26</td>
                    <td class="stat-cell">6</td>
                    <td class="stat-cell">6</td>
                    <td class="stat-cell">88</td>
                    <td class="stat-cell">29</td>
                    <td class="stat-cell">59</td>
                    <td class="stat-cell">84</td>
                </tr>
                 <tr class="Table__TR Table__TR--sm Table__even" data-idx="2">
                    <td class="stat-cell">38</td>
                    <td class="stat-cell">25</td>
                    <td class="stat-cell">10</td>
                    <td class="stat-cell">3</td>
                    <td class="stat-cell">86</td>
                    <td class="stat-cell">41</td>
                    <td class="stat-cell">45</td>
                    <td class="stat-cell">85</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# --- Pruebas para fetch_premier_league_html ---

def test_fetch_premier_league_html_success():
    """Verifica que la función fetch_premier_league_html retorne el contenido HTML correcto."""
    mock_response = MagicMock()
    mock_response.content = MOCK_ESPN_PREMIER_LEAGUE_HTML
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None # Simula un 200 OK

    with patch('requests.get', return_value=mock_response) as mock_get:
        url = "https://www.espn.com.co/futbol/posiciones/_/liga/eng.1"
        html = fetch_premier_league_html(url)
        assert html == MOCK_ESPN_PREMIER_LEAGUE_HTML
        mock_get.assert_called_once_with(url, headers=HEADERS)

def test_fetch_premier_league_html_http_error():
    """Verifica que fetch_premier_league_html lance HTTPError en caso de error HTTP."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")

    with patch('requests.get', return_value=mock_response):
        url = "https://www.espn.com.co/futbol/posiciones/_/liga/nonexistent"
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_premier_league_html(url)

def test_fetch_premier_league_html_connection_error():
    """Verifica que fetch_premier_league_html lance ConnectionError en caso de fallo de conexión."""
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError("Network error")):
        url = "https://www.espn.com.co/futbol/posiciones/_/liga/eng.1"
        with pytest.raises(requests.exceptions.ConnectionError):
            fetch_premier_league_html(url)

# --- Pruebas para parse_premier_league_standings ---

def test_parse_premier_league_standings_success():
    """Verifica que parse_premier_league_standings extraiga y combine los datos correctamente."""
    df = parse_premier_league_standings(MOCK_ESPN_PREMIER_LEAGUE_HTML)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3 # Esperamos 3 equipos en el mock HTML
    
    # Comprueba los nombres de las columnas
    expected_columns = [
        'Posicion', 'Abreviatura', 'Equipo', 'Número de partidos jugados',
        'El número de partidos ganados', 'Empate', 'Derrotas', 'Goles a favor',
        'Goles en contra', 'Diferencia de puntos', 'Puntos'
    ]
    assert list(df.columns) == expected_columns

    # Verifica los datos del primer equipo
    assert df.loc[0, 'Posicion'] == 1
    assert df.loc[0, 'Abreviatura'] == 'MCI'
    assert df.loc[0, 'Equipo'] == 'Manchester City'
    assert df.loc[0, 'Puntos'] == 91
    assert df.loc[0, 'Goles a favor'] == 96

    # Verifica los datos del segundo equipo
    assert df.loc[1, 'Posicion'] == 2
    assert df.loc[1, 'Abreviatura'] == 'ARS'
    assert df.loc[1, 'Equipo'] == 'Arsenal'
    assert df.loc[1, 'Puntos'] == 84
    assert df.loc[1, 'Derrotas'] == 6

    # Verifica los tipos de datos de las columnas numéricas
    for col in [
        'Posicion', 'Número de partidos jugados', 'El número de partidos ganados',
        'Empate', 'Derrotas', 'Goles a favor', 'Goles en contra',
        'Diferencia de puntos', 'Puntos'
    ]:
        assert pd.api.types.is_numeric_dtype(df[col]), f"Columna {col} no es numérica"

def test_parse_premier_league_standings_empty_html():
    """Verifica el comportamiento con HTML vacío o sin tablas relevantes."""
    empty_html = b"<html><body><h1>Empty Page</h1></body></html>"
    with pytest.raises(ValueError, match="No se encontró la primera tabla de posiciones"):
        parse_premier_league_standings(empty_html)

def test_parse_premier_league_standings_missing_second_table():
    """Verifica el comportamiento si falta la segunda tabla."""
    html_with_only_first_table = b"""
    <html>
    <body>
        <table class="Table Table--align-right Table--fixed Table--fixed-left">
            <thead></thead>
            <tbody>
                <tr class="Table__TR Table__TR--sm Table__even">
                    <td><span class="team-position ml2 pr3">1</span></td>
                    <td><div class="team-info">
                        <span class="hide-mobile">Team A</span>
                        <span class="dn show-mobile">TMA</span>
                    </div></td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    with pytest.raises(ValueError, match="No se encontró la segunda tabla de posiciones"):
        parse_premier_league_standings(html_with_only_first_table)

def test_parse_premier_league_standings_mismatched_rows():
    """
    Verifica el comportamiento si el número de filas en las tablas no coincide.
    Aquí el scraper actual concatena, por lo que una prueba podría verificar esto.
    """
    mismatched_html = b"""
    <html>
    <body>
        <table class="Table Table--align-right Table--fixed Table--fixed-left">
            <thead></thead>
            <tbody>
                <tr class="Table__TR Table__TR--sm Table__even">
                    <td><span class="team-position ml2 pr3">1</span></td>
                    <td><div class="team-info">
                        <span class="hide-mobile">Team A</span>
                        <span class="dn show-mobile">TMA</span>
                    </div></td>
                </tr>
                <tr class="Table__TR Table__TR--sm Table__even">
                    <td><span class="team-position ml2 pr3">2</span></td>
                    <td><div class="team-info">
                        <span class="hide-mobile">Team B</span>
                        <span class="dn show-mobile">TMB</span>
                    </div></td>
                </tr>
            </tbody>
        </table>

        <table class="Table Table--align-right">
            <thead></thead>
            <tbody class="Table__TBODY">
                <tr class="Table__TR Table__TR--sm Table__even" data-idx="0">
                    <td class="stat-cell">10</td><td class="stat-cell">5</td><td class="stat-cell">3</td><td class="stat-cell">2</td>
                    <td class="stat-cell">15</td><td class="stat-cell">10</td><td class="stat-cell">5</td><td class="stat-cell">18</td>
                </tr>
                </tbody>
        </table>
    </body>
    </html>
    """
    # Tu scraper actual va a concatenar, y Pandas llenará con NaN si hay un desajuste.
    # Esta prueba verificará que el DataFrame resultante tenga la forma esperada.
    df = parse_premier_league_standings(mismatched_html)
    assert len(df) == 2 # Esperamos 2 filas de df1
    assert df.shape[1] == len(expected_columns) # Mismas columnas esperadas
    # Podrías verificar que haya NaNs en las filas donde faltan datos de df2

# --- Pruebas para la función de guardado (ej. a CSV) ---
# Aunque tu scraper.py refactorizado ahora guarda a CSV, esta prueba
# debe hacerse si se crea una función 'save_data_to_csv' separada.
# Por ahora, si solo el main guarda, puedes probar la ejecución completa
# o añadir una función específica de guardado si quieres probarla unitariamente.

@pytest.fixture
def temp_csv_path(tmp_path):
    """Fixture para crear una ruta de archivo temporal y limpiarla."""
    return tmp_path / "premier_league_standings.csv"

def test_run_scraper_saves_csv(temp_csv_path):
    """
    Esta prueba verifica que la ejecución completa del scraper (simulada)
    genera un archivo CSV con el contenido esperado.
    """
    mock_response = MagicMock()
    mock_response.content = MOCK_ESPN_PREMIER_LEAGUE_HTML
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None

    # Parcheamos requests.get para evitar la llamada de red real
    with patch('requests.get', return_value=mock_response):
        # Parcheamos la salida de print para que no se imprima durante la prueba
        with patch('builtins.print'):
            # Ejecutamos la lógica del bloque __main__ directamente.
            # Normalmente, llamarías a una función como `save_data_to_csv(df, path)`
            # si tuvieras esa función separada del `if __name__ == "__main__":`
            # Como tu scraper actual tiene la lógica de guardado en `if __name__ == "__main__":`,
            # necesitamos simular esa ejecución o mover la lógica a una función.

            # Para propósitos de esta demostración, simularemos la ejecución del scraper y la guardado.
            # En un caso real, la función `run_scraper` retorna el DataFrame, y una función
            # `save_dataframe_to_csv(df, path)` lo guardaría.

            # Ejemplo de cómo se probaría si tuvieras una función `save_dataframe_to_csv`:
            # from src.scraper import run_scraper, save_dataframe_to_csv
            # df = run_scraper("http://fake-url.com")
            # save_dataframe_to_csv(df, str(temp_csv_path))

            # Dado tu `if __name__ == "__main__":` actual, esta prueba es un poco más compleja,
            # pero podemos simular la ejecución. Lo mejor sería mover la lógica de guardado
            # a una función `save_data_to_csv(df, path)` fuera del `if __name__ == "__main__":`.

            # PARA ESTA DEMO, ASUMO QUE run_scraper ya está disponible y retorna un DF.
            # Si quieres probar el guardado a CSV, la forma más limpia es tener una función
            # `save_dataframe_to_csv(df, filepath)` en `src/scraper.py`
            # y llamarla en tu `if __name__ == "__main__":` y aquí en la prueba.

            # VOY A ASUMIR UNA FUNCIÓN DE GUARDADO PARA LA PRUEBA, DEBERÍAS AÑADIRLA A `src/scraper.py`
            # Ejemplo de función a añadir en src/scraper.py:
            # def save_dataframe_to_csv(df: pd.DataFrame, filename: str):
            #     df.to_csv(filename, index=False)
            #
            # Luego, en el test:
            # from src.scraper import run_scraper, save_dataframe_to_csv
            # df = run_scraper("http://fake-url.com")
            # save_dataframe_to_csv(df, str(temp_csv_path))
            
            # --- Temporalmente, recreo la lógica del main para el test ---
            url_to_scrape = "http://fake-url-for-scraper.com"
            html_content = fetch_premier_league_html(url_to_scrape)
            df_standings = parse_premier_league_standings(html_content)

            # Lógica de guardado que iría en una función aparte
            output_dir = temp_csv_path.parent # Usamos el directorio temporal del fixture
            output_path = temp_csv_path
            os.makedirs(output_dir, exist_ok=True)
            df_standings.to_csv(output_path, index=False)
            # --- Fin de la recreación temporal ---

            assert os.path.exists(temp_csv_path)
            read_df = pd.read_csv(temp_csv_path)
            assert not read_df.empty
            assert len(read_df) == 3 # Verifica que se guardaron los 3 equipos mock
            assert read_df.loc[0, 'Equipo'] == 'Manchester City'
