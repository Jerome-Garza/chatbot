from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from ai import generar_sql
from db import ejecutar_query
from security import validar_sql, limpiar_sql

import unicodedata

app = FastAPI()

# 🌐 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📥 Modelo
class Pregunta(BaseModel):
    mensaje: str


# 🔥 LIMPIAR TEXTO (acentos)
def limpiar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto


# 🧠 MAPEO ENTIDADES
MAPEO_ENTIDADES = {
    "aguascalientes": 1,
    "baja california": 2,
    "baja california sur": 3,
    "campeche": 4,
    "coahuila": 5,
    "colima": 6,
    "chiapas": 7,
    "chihuahua": 8,
    "cdmx": 9,
    "ciudad de mexico": 9,
    "durango": 10,
    "guanajuato": 11,
    "guerrero": 12,
    "hidalgo": 13,
    "jalisco": 14,
    "mexico": 15,
    "michoacan": 16,
    "morelos": 17,
    "nayarit": 18,
    "nuevo leon": 19,
    "oaxaca": 20,
    "puebla": 21,
    "queretaro": 22,
    "quintana roo": 23,
    "san luis potosi": 24,
    "sinaloa": 25,
    "sonora": 26,
    "tabasco": 27,
    "tamaulipas": 28,
    "tlaxcala": 29,
    "veracruz": 30,
    "yucatan": 31,
    "zacatecas": 32
}

# 🧠 MAPEO NIVEL
MAPEO_NIVEL = {
    "segundo nivel": "2",
    "nivel 2": "2",
    "tercer nivel": "3",
    "nivel 3": "3"
}


# 🔍 Detectores
def detectar_entidad(texto):
    for nombre, clave in MAPEO_ENTIDADES.items():
        if nombre in texto:
            return str(clave).zfill(2)
    return None


def detectar_nivel(texto):
    for clave, valor in MAPEO_NIVEL.items():
        if clave in texto:
            return valor
    return None


# 🔥 DETECTOR STATUS SIN AMBIGÜEDAD
def detectar_status(texto):
    if "fuera" in texto:
        return "fuera"

    if "pendiente" in texto:
        return "pendiente"

    if "operacion" in texto or "activo" in texto:
        return "en_operacion"

    return None


def detectar_municipio(texto):
    if "municipio de" in texto:
        return texto.split("municipio de")[1].strip()
    return None


# 🧾 Formatear resultados
def formatear(columnas, resultados):
    if not resultados:
        return "Sin resultados"

    texto = ""
    for fila in resultados:
        fila_txt = ", ".join([f"{col}: {val}" for col, val in zip(columnas, fila)])
        texto += fila_txt + "\n"

    return texto


# 🤖 Endpoint
@app.post("/chat")
def chat(pregunta: Pregunta):
    try:
        texto = limpiar_texto(pregunta.mensaje)

        entidad = detectar_entidad(texto)
        nivel = detectar_nivel(texto)
        status = detectar_status(texto)
        municipio = detectar_municipio(texto)

        print("DEBUG:", entidad, nivel, status, municipio)

        condiciones = []

        if entidad:
            condiciones.append(f"entidad_id = '{entidad}'")

        if nivel:
            condiciones.append(f"nivel_id = '{nivel}'")

        if municipio:
            condiciones.append(f"municipio_oficial ILIKE '%{municipio}%'")

        # 🔥 CONSULTA DINÁMICA AL CATÁLOGO (SIN AMBIGÜEDAD)
        if status:
            if status == "en_operacion":
                filtro = "en operación"
            elif status == "fuera":
                filtro = "fuera de operación"
            elif status == "pendiente":
                filtro = "pendiente"
            else:
                filtro = status

            sql_estatus = f"""
            SELECT estatus_id 
            FROM cat_estatus_unidades
            WHERE LOWER(estatus_nombre) LIKE '%{filtro}%'
            LIMIT 1;
            """

            print("SQL CATÁLOGO:", sql_estatus)

            _, res_estatus = ejecutar_query(sql_estatus)

            print("RESULTADO CATÁLOGO:", res_estatus)

            if res_estatus:
                estatus_id = res_estatus[0][0]
                condiciones.append(f"estatus_operacion_oficial = '{estatus_id}'")

        # 🔥 SQL dinámico final
        if condiciones:
            where = " AND ".join(condiciones)

            sql = f"""
            SELECT COUNT(*) 
            FROM directorio_unidades 
            WHERE {where};
            """
        else:
            sql = generar_sql(texto)
            sql = limpiar_sql(sql) 

        print("SQL FINAL:\n", sql)

        # 🔐 Validación
        if not validar_sql(sql):
            return {"respuesta": "Consulta no permitida"}

        columnas, resultados = ejecutar_query(sql)

        return {
            "sql": sql,
            "respuesta": formatear(columnas, resultados)
        }

    except Exception as e:
        
        return {"respuesta": f"Error: {str(e)}"}