import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        sslmode="require"
    )

def ejecutar_query(sql):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql)
    resultados = cursor.fetchall()

    columnas = [desc[0] for desc in cursor.description]

    conn.close()

    return columnas, resultados
