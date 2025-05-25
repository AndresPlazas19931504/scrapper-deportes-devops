# tests/test_scraper.py

import pytest
import requests
import pandas as pd
from unittest.mock import patch, MagicMock
import os

# Importa las funciones que vamos a probar de tu script refactorizado
from src.scraper import fetch_premier_league_html, parse_premier_league_standings, save_dataframe_to_csv, HEADERS

# --- Datos Mock para las Pruebas ---
# ESTE HTML ES CRÍTICO. DEBE REFLEJAR LA ESTRUCTURA DE LA PÁGINA REAL DE ESPN.
# Cópialo de la página web (inspecciona el elemento) y simplifícalo para que solo contenga
# la información relevante que tu scraper busca. Esto asegura que las pruebas sean estables.

MOCK_ESPN_PREMIER_LEAGUE_HTML = b"""
<!DOCTYPE html>
<html>
<head><title>ESPN Premier League Standings Mock</title></head>
<body>
    <div id="wrapper">
        <table class="Table Table--align-right Table--fixed Table--fixed-left">
            <thead>
                <tr><th></th><th></th></tr>
            </thead>
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
            <thead>
                <tr><th>GP</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>PTS</th></tr>
            </thead>
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
    """Verifica que la función fetch_premier_league_html retorne el contenido HTML esperado en caso de éxito."""
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
    """Verifica que fetch_premier_league_html lance HTTPError en caso de error HTTP (ej. 404)."""
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

def test_parse_premier_league_standings_correct_extraction():
    """Verifica que parse_premier_league_standings extraiga los datos correctos del HTML mock."""
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

    # Verifica los datos del primer equipo (Manchester City)
    assert df.loc[0, 'Posicion'] == 1
    assert df.loc[0, 'Abreviatura'] == 'MCI'
    assert df.loc[0, 'Equipo'] == 'Manchester City'
    assert df.loc[0, 'Número de partidos jugados'] == 38
    assert df.loc[0, 'El número de partidos ganados'] == 28
    assert df.loc[0, 'Empate'] == 7
    assert df.loc[0, 'Derrotas'] == 3
    assert df.loc[0, 'Goles a favor'] == 96
    assert df.loc[0, 'Goles en contra'] == 34
    assert df.loc[0, 'Diferencia de puntos'] == 62
    assert df.loc[0, 'Puntos'] == 91

    # Verifica los datos del segundo equipo (Arsenal)
    assert df.loc[1, 'Posicion'] == 2
    assert df.loc[1, 'Abreviatura'] == 'ARS'
    assert df.loc[1, 'Equipo'] == 'Arsenal'
    assert df.loc[1, 'Puntos'] == 84 # Solo un ejemplo, verifica más si quieres

    # Verifica los tipos de datos de las columnas numéricas
    for col in num_cols: # Asumiendo num_cols está definido globalmente en scraper.py o aquí.
        # Definir num_cols localmente si no está importado de scraper.py:
        num_cols = [
            'Posicion', 'Número de partidos jugados', 'El número de partidos ganados',
            'Empate', 'Derrotas', 'Goles a favor', 'Goles en contra',
            'Diferencia de puntos', 'Puntos'
        ]
        assert pd.api.types.is_numeric_dtype(df[col]), f"Columna {col} no es numérica"


def test_parse_premier_league_standings_empty_html():
    """Verifica que la función lance un ValueError si no se encuentra la primera tabla."""
    empty_html = b"<html><body><h1>Empty Page</h1></body></html>"
    with pytest.raises(ValueError, match="No se encontró la primera tabla de posiciones"):
        parse_premier_league_standings(empty_html)

def test_parse_premier_league_standings_missing_second_table():
    """Verifica que la función lance un ValueError si falta la segunda tabla."""
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

# --- Pruebas para save_dataframe_to_csv ---

@pytest.fixture
def temp_csv_path(tmp_path):
    """Fixture de pytest para crear una ruta de archivo temporal y limpiarla."""
    # tmp_path es un fixture de pytest que proporciona una ruta a un directorio temporal único.
    return tmp_path / "test_premier_league_standings.csv"

def test_save_dataframe_to_csv_creates_file(temp_csv_path):
    """Verifica que save_dataframe_to_csv cree el archivo CSV."""
    test_data = pd.DataFrame([
        {'Posicion': 1, 'Equipo': 'Test Team', 'Puntos': 10, 'Abreviatura': 'TST',
         'Número de partidos jugados': 5, 'El número de partidos ganados': 3,
         'Empate': 1, 'Derrotas': 1, 'Goles a favor': 8, 'Goles en contra': 5,
         'Diferencia de puntos': 3}
    ])
    save_dataframe_to_csv(test_data, str(temp_csv_path))
    assert os.path.exists(temp_csv_path)

def test_save_dataframe_to_csv_correct_content(temp_csv_path):
    """Verifica que save_dataframe_to_csv escriba el contenido correcto en el CSV."""
    test_data = pd.DataFrame([
        {'Posicion': 1, 'Equipo': 'Team X', 'Puntos': 20, 'Abreviatura': 'TMX',
         'Número de partidos jugados': 10, 'El número de partidos ganados': 6,
         'Empate': 2, 'Derrotas': 2, 'Goles a favor': 20, 'Goles en contra': 10,
         'Diferencia de puntos': 10}
    ])
    save_dataframe_to_csv(test_data, str(temp_csv_path))

    df_read = pd.read_csv(temp_csv_path)
    pd.testing.assert_frame_equal(df_read, test_data) # Compara DataFrames directamente
    assert df_read.loc[0, 'Equipo'] == 'Team X'

def test_save_dataframe_to_csv_empty_data(temp_csv_path):
    """Verifica que save_dataframe_to_csv maneje DataFrames vacíos sin errores."""
    empty_data = pd.DataFrame(columns=[
        'Posicion', 'Abreviatura', 'Equipo', 'Número de partidos jugados',
        'El número de partidos ganados', 'Empate', 'Derrotas', 'Goles a favor',
        'Goles en contra', 'Diferencia de puntos', 'Puntos'
    ])
    save_dataframe_to_csv(empty_data, str(temp_csv_path))
    assert os.path.exists(temp_csv_path)
    df_read = pd.read_csv(temp_csv_path)
    assert df_read.empty
    assert list(df_read.columns) == list(empty_data.columns) # Asegura que las columnas se mantengan
