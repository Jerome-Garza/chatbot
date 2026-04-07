import os
from openai import OpenAI

# 🔥 Leer .env manualmente (sin dotenv)
def leer_env(ruta):
    variables = {}
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            if "=" in linea:
                clave, valor = linea.strip().split("=", 1)
                variables[clave] = valor
    return variables

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

env = leer_env(ENV_PATH)

if not env.api_key:
    raise ValueError("❌ No se encontró la API Key")

client = OpenAI(api_key=env.api_key)

SCHEMA = """
Tabla disponible:

directorio_unidades(
    clues,
    nombre_oficial,
    entidad_id,
    tipologia_id,
    nivel_id,
    municipio_oficial,
    estatus_operacion_oficial
)
"""

def generar_sql(pregunta):
    prompt = f"""
Eres un experto en PostgreSQL.

IMPORTANTE:
- SOLO existe una tabla: directorio_unidades
- NO existen otras tablas
- NO existen relaciones
- NO inventes columnas
- NO uses JOIN
- SOLO usa las columnas listadas abajo

Columnas disponibles:
- clues
- nombre_oficial,
- entidad_id,
- tipologia_id,
- nivel_id,
- municipio_oficial,
- estatus_operacion_oficial

Reglas:
- SOLO SELECT
- Máximo 10 resultados
- Sin explicación

Pregunta:
{pregunta}
"""

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

    return response.choices[0].message.content.strip()