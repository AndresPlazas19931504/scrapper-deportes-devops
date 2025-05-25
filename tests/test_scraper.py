import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os
import requests # <--- ¡IMPORTA REQUESTS AQUI!

# Ajusta el path para importar el scraper desde src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from scraper import fetch_premier_league_html, parse_premier_league_standings, save_dataframe_to_csv, HEADERS, ESPN_PREMIER_LEAGUE_URL

# Mock HTML content for testing parse_premier_league_standings
# Asegúrate de que este HTML sea ASCII puro para evitar SyntaxError.
# Y que contenga 3 equipos completos en ambas tablas para la prueba de extracción.
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

# Test cases for fetch_premier_league_html
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
        # Asegúrate de que el mock_get.assert_called_once_with() incluya el argumento timeout
        mock_get.assert_called_once_with(url, headers=HEADERS, timeout=10)


def test_fetch_premier_league_html_http_error():
    """Verifica que fetch_premier_league_html lance una excepción para errores HTTP."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")

    with patch('requests.get', return_value=mock_response):
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_premier_league_html(ESPN_PREMIER_LEAGUE_URL)

def test_fetch_premier_league_html_connection_error():
    """Verifica que fetch_premier_league_html lance una excepción para errores de conexión."""
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError("No connection")):
        with pytest.raises(requests.exceptions.ConnectionError):
            fetch_premier_league_html(ESPN_PREMIER_LEAGUE_URL)

def test_fetch_premier_league_html_timeout_error():
    """Verifica que fetch_premier_league_html lance una excepción para errores de timeout."""
    with patch('requests.get', side_effect=requests.exceptions.Timeout("Request timed out")):
        with pytest.raises(requests.exceptions.Timeout):
            fetch_premier_league_html(ESPN_PREMIER_LEAGUE_URL)

# Test cases for parse_premier_league_standings
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
    assert df.loc[1, 'Número de partidos jugados'] == 38
    assert df.loc[1, 'El número de partidos ganados'] == 26
    assert df.loc[1, 'Empate'] == 6
    assert df.loc[1, 'Derrotas'] == 6
    assert df.loc[1, 'Goles a favor'] == 88
    assert df.loc[1, 'Goles en contra'] == 29
    assert df.loc[1, 'Diferencia de puntos'] == 59
    assert df.loc[1, 'Puntos'] == 84

    # Verifica los datos del tercer equipo (Liverpool) - Asegúrate de que el mock sea completo
    assert df.loc[2, 'Posicion'] == 3
    assert df.loc[2, 'Abreviatura'] == 'LIV'
    assert df.loc[2, 'Equipo'] == 'Liverpool'
    assert df.loc[2, 'Número de partidos jugados'] == 38
    assert df.loc[2, 'El número de partidos ganados'] == 25
    assert df.loc[2, 'Empate'] == 10
    assert df.loc[2, 'Derrotas'] == 3
    assert df.loc[2, 'Goles a favor'] == 86
    assert df.loc[2, 'Goles en contra'] == 41
    assert df.loc[2, 'Diferencia de puntos'] == 45
    assert df.loc[2, 'Puntos'] == 85


    # Verifica los tipos de datos de las columnas numéricas
    num_cols = [
        'Posicion', 'Número de partidos jugados', 'El número de partidos ganados',
        'Empate', 'Derrotas', 'Goles a favor', 'Goles en contra',
        'Diferencia de puntos', 'Puntos'
    ]
    for col in num_cols:
        assert pd.api.types.is_numeric_dtype(df[col]), f"Columna {col} no es numérica"

def test_parse_premier_league_standings_missing_tables():
    """Verifica que parse_premier_league_standings lance ValueError si faltan tablas."""
    # HTML sin ninguna tabla
    html_content_empty = b"<html><body><div>No tables here</div></body></html>"
    with pytest.raises(ValueError, match="No se encontró la primera tabla de posiciones"):
        parse_premier_league_standings(html_content_empty)

    # HTML con solo la primera tabla
    html_content_partial = b"""
    <html><body>
        <table class="Table Table--align-right Table--fixed Table--fixed-left"></table>
    </body></html>
    """
    with pytest.raises(ValueError, match="No se encontró la segunda tabla de posiciones"):
        parse_premier_league_standings(html_content_partial)

def test_parse_premier_league_standings_empty_html():
    """
    Verifica que parse_premier_league_standings lance ValueError cuando se le pasa HTML vacío,
    ya que no encontrará la primera tabla.
    """
    with pytest.raises(ValueError, match="No se encontró la primera tabla de posiciones en el HTML."): # <--- CAMBIO AQUI
        parse_premier_league_standings(b"")


# Test cases for save_dataframe_to_csv
@pytest.fixture
def sample_dataframe():
    """Fixture que proporciona un DataFrame de ejemplo para las pruebas."""
    data = {
        'Posicion': [1, 2],
        'Equipo': ['Equipo A', 'Equipo B'],
        'Puntos': [10, 8]
    }
    return pd.DataFrame(data)

def test_save_dataframe_to_csv_creates_file(tmp_path, sample_dataframe):
    """Verifica que save_dataframe_to_csv cree un archivo CSV."""
    output_file = tmp_path / "test_standings.csv"
    save_dataframe_to_csv(sample_dataframe, str(output_file))
    assert output_file.is_file()

def test_save_dataframe_to_csv_content(tmp_path, sample_dataframe):
    """Verifica que el contenido del CSV sea correcto."""
    output_file = tmp_path / "test_standings.csv"
    save_dataframe_to_csv(sample_dataframe, str(output_file))
    
    loaded_df = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(loaded_df, sample_dataframe)

def test_save_dataframe_to_csv_creates_directory(tmp_path, sample_dataframe):
    """Verifica que save_dataframe_to_csv cree el directorio si no existe."""
    output_dir = tmp_path / "subfolder"
    output_file = output_dir / "test_standings.csv"
    save_dataframe_to_csv(sample_dataframe, str(output_file))
    assert output_dir.is_dir()
    assert output_file.is_file()
