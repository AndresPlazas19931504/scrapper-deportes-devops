import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}
     

def web_scraping_espn_combinado():
    try:
        url = "https://www.espn.com.co/futbol/posiciones/_/liga/eng.1"
        response = requests.get(url, headers=headers)

        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        tabla_posiciones1 = soup.find("table", {"class": "Table Table--align-right Table--fixed Table--fixed-left"})
        filas1 = tabla_posiciones1.find_all("tr", {"class": ["Table__TR Table__TR--sm Table__even", "filled Table__TR Table__TR--sm Table__even"]})
        posiciones = []
        abreviaturas = []
        nombres = []
        for fila in filas1:
            posicion = fila.find("span", {"class": "team-position ml2 pr3"}).text
            nombre_equipo = fila.find("span", {"class": "hide-mobile"}).text
            abreviatura_equipo = fila.find("span", {"class": "dn show-mobile"}).text
            posiciones.append(posicion)
            abreviaturas.append(abreviatura_equipo)
            nombres.append(nombre_equipo)
        df1 = pd.DataFrame({"Posición": posiciones, "Avr": abreviaturas, "Nombre": nombres})

        tabla_posiciones2 = soup.find("table", {"class": "Table Table--align-right"})
        tbody = tabla_posiciones2.find("tbody", {"class": "Table__TBODY"})
        filas2 = tbody.find_all("tr", {"class": ["Table__TR Table__TR--sm Table__even", "filled Table__TR Table__TR--sm Table__even"]})
        datos_por_idx = {}
        for fila in filas2:
            data_idx = fila.get("data-idx")
            if data_idx is None:
                continue
            stat_cells = fila.find_all("span", {"class": "stat-cell"})
            if data_idx not in datos_por_idx:
                datos_por_idx[data_idx] = []
            datos_por_idx[data_idx].extend([cell.text for cell in stat_cells])
        df2 = pd.DataFrame(datos_por_idx).T

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


        return df_final

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")

    except Exception as e:
        print(f"Error inesperado: {e}")

web_scraping_espn_combinado()
     

from google.colab import drive
import sqlite3

drive.mount('/content/drive')

database_path = '/content/drive/MyDrive/Pad2025/Actividad_pad.db'

try:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute("SELECT SQLITE_VERSION()")
    version = cursor.fetchone()[0]
    print(f"Versión de SQLite: {version}")

    conn.close()

except sqlite3.Error as e:
    print(f"Error al conectar a SQLite: {e}")
     

try:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PremierLeague (
            Posicion INTEGER,
            Abreviatura TEXT,
            Equipo TEXT,
            "Número de partidos jugados" INTEGER,
            "El número de partidos ganados" INTEGER,
            Empate INTEGER,
            Derrotas INTEGER,
            "Goles a favor" INTEGER,
            "Goles en contra" INTEGER,
            "Diferencia de puntos" INTEGER,
            Puntos INTEGER
        )
    ''')

    conn.commit()
    conn.close()

    print("Tabla 'PremierLeague' creada exitosamente en la base de datos.")

except sqlite3.Error as e:
    print(f"Error al crear la tabla: {e}")
     

try:
    conn = sqlite3.connect(database_path)

    df_final = web_scraping_espn_combinado()
    df_final.to_sql('PremierLeague', conn, if_exists='replace', index=False)

    conn.close()

    print("Datos insertados correctamente en la tabla 'PremierLeague'.")

except sqlite3.Error as e:
    print(f"Error al insertar los datos: {e}")
     

try:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM PremierLeague")

    results = cursor.fetchall()

    for row in results:
        print(row)

    df = pd.DataFrame(results, columns=[description[0] for description in cursor.description])

    conn.close()

except sqlite3.Error as e:
    print(f"Error al consultar los datos: {e}")
