import os
import json
import re

from openai import OpenAI
from dotenv import load_dotenv


# =========================================================
# CONFIGURACIÓN
# =========================================================

# En LOCAL:
# utiliza las variables del archivo .env
#
# En RAILWAY:
# utiliza las variables configuradas en Railway

load_dotenv()

API_KEY = os.getenv("API_KEY")

print(
    "DEBUG API_KEY:",
    "OK" if API_KEY else "NO CARGADA"
)

if not API_KEY:
    raise ValueError(
        "❌ No se encontró la variable API_KEY"
    )


# =========================================================
# CLIENTE OPENAI
# =========================================================

client = OpenAI(
    api_key=API_KEY
)


# =========================================================
# ESQUEMA DE BASE DE DATOS SIBE
# =========================================================

SCHEMA = """

BASE DE DATOS POSTGRESQL - SIBE


TABLA: tarjetas_informativas

Columnas:

- clues
- datos
- updated_at


TABLA: directorio_unidades

Columnas:

- clues
- nombre_oficial
- entidad_id
- tipologia_id
- nivel_id
- municipio_oficial
- estatus_operacion_oficial


RELACIÓN:

directorio_unidades.clues =
tarjetas_informativas.clues


=========================================================
CAMPOS DEL JSON datos
=========================================================

datos->>'clues'

datos->>'nombreHospital'

datos->>'entidad'

datos->>'nivelAtencion'

datos->>'camasCensables'

datos->>'camasNoCensables'

datos->>'quirofanosFuncionales'

datos->>'quirofanosNoFuncionales'

datos->>'abastoMedicamentos'

datos->>'abastoMaterialCuracion'

datos->>'telemedicinaEspacioEquipo'

datos->>'telemedicinaEspecialidades'

datos->>'carteraServicios'

datos->>'equipamiento'

datos->>'datosContacto'

datos->>'contextoHistorico'

datos->>'serviciosGenerales'

datos->>'serviciosMedicoIntegrales'

datos->>'situacionActual'


=========================================================
RECURSOS HUMANOS
=========================================================

datos->'rrhh'->>'enfermeras'

datos->'rrhh'->>'paramedico'

datos->'rrhh'->>'deficitMedico'

datos->'rrhh'->>'cuerpoGobierno'

datos->'rrhh'->>'personalMedico'

datos->'rrhh'->>'administrativos'

datos->'rrhh'->>'deficitEnfermeras'

datos->'rrhh'->>'deficitParamedico'

datos->'rrhh'->>'deficitCuerpoGobierno'

datos->'rrhh'->>'deficitAdministrativos'


=========================================================
DETALLES DE CARTERA
=========================================================

datos->'detallesCartera'


=========================================================
ENTIDAD
=========================================================

La entidad se encuentra dentro del JSON:

datos->>'entidad'

Ejemplo para Veracruz:

unaccent(datos->>'entidad')
ILIKE unaccent('%Veracruz%')


NO utilizar:

entidad_id

para buscar el nombre de la entidad.


=========================================================
NIVEL DE ATENCIÓN
=========================================================

El nivel se encuentra dentro del JSON:

datos->>'nivelAtencion'


Segundo Nivel:

unaccent(datos->>'nivelAtencion')
ILIKE unaccent('%Segundo Nivel%')


Interpretar como Segundo Nivel:

- 2o nivel
- 2do nivel
- segundo nivel
- nivel 2
- 2 nivel


=========================================================
MUNICIPIO
=========================================================

El municipio se encuentra en:

directorio_unidades.municipio_oficial


NO utilizar una tabla externa de municipios.


=========================================================
ESTATUS
=========================================================

El estatus se encuentra en:

directorio_unidades.estatus_operacion_oficial


=========================================================
CLUES
=========================================================

Una CLUES se encuentra directamente en:

tarjetas_informativas.clues


Para buscar una CLUES:

UPPER(TRIM(clues)) =
UPPER(TRIM('CLUES'))


=========================================================
NOMBRE DEL HOSPITAL
=========================================================

El nombre se encuentra en:

datos->>'nombreHospital'


Para buscarlo:

unaccent(datos->>'nombreHospital')
ILIKE unaccent('%texto%')


Esto permite encontrar variaciones de acentos.


=========================================================
CAMAS CENSABLES
=========================================================

El campo es:

datos->>'camasCensables'


IMPORTANTE:

El valor es texto dentro del JSON.

Para realizar comparaciones numéricas utilizar:

CASE
    WHEN TRIM(datos->>'camasCensables') ~ '^[0-9]+$'
    THEN TRIM(datos->>'camasCensables')::INTEGER
    ELSE NULL
END


NO comparar directamente:

datos->>'camasCensables' > '30'


=========================================================
CONTEO DE UNIDADES
=========================================================

Una unidad se identifica mediante:

clues


Para contar unidades:

COUNT(DISTINCT clues)


=========================================================
CONTEO DE HOSPITALES
=========================================================

Para preguntas como:

¿Cuántos hospitales tenemos?

utilizar:

COUNT(DISTINCT clues)


=========================================================
HOSPITALES CON MÁS DE X CAMAS
=========================================================

Para:

más de 30 camas

utilizar:

CASE
    WHEN TRIM(datos->>'camasCensables') ~ '^[0-9]+$'
    THEN TRIM(datos->>'camasCensables')::INTEGER
    ELSE NULL
END > 30


=========================================================
HOSPITALES CON AL MENOS X CAMAS
=========================================================

Para:

al menos 30 camas

utilizar:

CASE
    WHEN TRIM(datos->>'camasCensables') ~ '^[0-9]+$'
    THEN TRIM(datos->>'camasCensables')::INTEGER
    ELSE NULL
END >= 30


=========================================================
HOSPITALES CON MENOS DE X CAMAS
=========================================================

Para:

menos de 30 camas

utilizar:

CASE
    WHEN TRIM(datos->>'camasCensables') ~ '^[0-9]+$'
    THEN TRIM(datos->>'camasCensables')::INTEGER
    ELSE NULL
END < 30


=========================================================
HOSPITALES ENTRE X Y Y CAMAS
=========================================================

Para:

entre 30 y 50 camas

utilizar:

CASE
    WHEN TRIM(datos->>'camasCensables') ~ '^[0-9]+$'
    THEN TRIM(datos->>'camasCensables')::INTEGER
    ELSE NULL
END BETWEEN 30 AND 50


=========================================================
TABLAS QUE NO EXISTEN
=========================================================

NO EXISTEN:

entidades
niveles
estados
municipios
hospitales


NO UTILIZAR NINGUNA DE ESTAS TABLAS.


=========================================================
SEGURIDAD
=========================================================

SOLO se permiten consultas SELECT.

NO utilizar:

INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
TRUNCATE
GRANT
REVOKE


NO inventar:

- tablas
- columnas
- relaciones


=========================================================
LISTADOS
=========================================================

Cuando el usuario solicite:

"cuáles"
"cuales"
"lista"
"listar"
"qué hospitales"
"que hospitales"

devolver registros.

Máximo:

LIMIT 50


=========================================================
CONTEOS
=========================================================

Cuando el usuario pregunte:

"cuántos hospitales"

o:

"cuántas unidades"

utilizar:

COUNT(DISTINCT clues)


=========================================================
JOIN
=========================================================

Cuando sea necesario utilizar información de ambas tablas:

SELECT
    d.clues,
    d.nombre_oficial,
    d.municipio_oficial,
    d.estatus_operacion_oficial,
    ti.datos->>'camasCensables' AS camas_censables
FROM directorio_unidades d
JOIN tarjetas_informativas ti
    ON d.clues = ti.clues


"""


# =========================================================
# LIMPIAR SQL
# =========================================================

def limpiar_sql(sql):

    if not sql:
        raise ValueError(
            "❌ OpenAI no devolvió SQL."
        )

    sql = sql.strip()

    # ---------------------------------------------
    # Eliminar Markdown
    # ---------------------------------------------

    sql = re.sub(
        r"^```(?:sql|postgresql)?",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"```$",
        "",
        sql
    )

    sql = sql.strip()

    # ---------------------------------------------
    # Si por alguna razón devolvió texto antes
    # del SELECT, tomar desde SELECT.
    # ---------------------------------------------

    match = re.search(
        r"\bSELECT\b",
        sql,
        flags=re.IGNORECASE
    )

    if match:
        sql = sql[match.start():]

    # ---------------------------------------------
    # Quitar ; finales
    # ---------------------------------------------

    sql = sql.strip()

    if sql.endswith(";"):
        sql = sql[:-1].strip()

    return sql


# =========================================================
# VALIDAR SQL
# =========================================================

def validar_sql(sql):

    sql_limpio = limpiar_sql(sql)

    sql_upper = sql_limpio.upper().strip()

    # ---------------------------------------------
    # Debe comenzar con SELECT
    # ---------------------------------------------

    if not sql_upper.startswith("SELECT"):

        raise ValueError(
            "❌ SQL BLOQUEADO: la consulta no comienza con SELECT."
        )

    # ---------------------------------------------
    # Palabras peligrosas
    # ---------------------------------------------

    palabras_prohibidas = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "GRANT",
        "REVOKE"
    ]

    for palabra in palabras_prohibidas:

        patron = rf"\b{palabra}\b"

        if re.search(
            patron,
            sql_upper
        ):

            raise ValueError(
                f"❌ SQL BLOQUEADO: contiene {palabra}."
            )

    # ---------------------------------------------
    # Tablas que NO existen
    # ---------------------------------------------

    tablas_prohibidas = [
        "entidades",
        "niveles",
        "estados",
        "municipios",
        "hospitales"
    ]

    for tabla in tablas_prohibidas:

        patron = rf"\b(?:FROM|JOIN)\s+{tabla}\b"

        if re.search(
            patron,
            sql_limpio,
            flags=re.IGNORECASE
        ):

            raise ValueError(
                f"❌ SQL BLOQUEADO: tabla inexistente '{tabla}'."
            )

    # ---------------------------------------------
    # Tablas permitidas
    # ---------------------------------------------

    tablas_permitidas = [
        "tarjetas_informativas",
        "directorio_unidades"
    ]

    # Buscar FROM y JOIN
    referencias = re.findall(
        r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql_limpio,
        flags=re.IGNORECASE
    )

    for tabla in referencias:

        if tabla.lower() not in tablas_permitidas:

            raise ValueError(
                f"❌ SQL BLOQUEADO: tabla no autorizada '{tabla}'."
            )

    # ---------------------------------------------
    # Evitar texto extraño conocido
    # ---------------------------------------------

    basura = [
        "PREGUNTA DEL USUARIO",
        "SQL GENERADO",
        "VALIDANDO SQL",
        "ANÁLISIS",
        "REGLAS",
        "SCHEMA",
        "RESPUESTA"
    ]

    for texto in basura:

        if texto in sql_upper:

            raise ValueError(
                f"❌ SQL BLOQUEADO: contiene texto extraño '{texto}'."
            )

    return sql_limpio


# =========================================================
# GENERAR SQL
# =========================================================

def generar_sql(pregunta):

    print("")
    print("========================================")
    print("GENERANDO SQL...")
    print("========================================")
    print("PREGUNTA:")
    print(pregunta)
    print("")


    prompt = f"""
Convierte la pregunta del usuario en una consulta
SQL PostgreSQL válida para la base de datos SIBE.

Utiliza exclusivamente el esquema proporcionado.

{SCHEMA}


PREGUNTA DEL USUARIO:

{pregunta}


REGLAS IMPORTANTES:

1. Devuelve SOLO un objeto JSON.

2. El JSON debe tener exactamente esta estructura:

{{
    "sql": "SELECT ..."
}}

3. La propiedad sql debe contener exclusivamente
la consulta SQL.

4. No escribas explicaciones.

5. No escribas Markdown.

6. No utilices bloques ```.

7. No escribas "PREGUNTA DEL USUARIO" dentro del SQL.

8. No escribas "SQL GENERADO" dentro del SQL.

9. No escribas el esquema dentro del SQL.

10. No inventes tablas.

11. No inventes columnas.

12. SOLO SELECT.

13. Para conteos utiliza COUNT(DISTINCT clues).

14. Para Veracruz utiliza datos->>'entidad'.

15. Para Segundo Nivel utiliza datos->>'nivelAtencion'.

16. Para comparaciones de camas convierte
    camasCensables a INTEGER mediante CASE.

17. Para listas utiliza LIMIT 50.
"""


    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres el generador SQL del "
                        "Asistente SIBE. "
                        "Devuelve exclusivamente "
                        "JSON válido con una propiedad "
                        "'sql'."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0,

            response_format={
                "type": "json_object"
            }
        )

    except Exception as e:

        print("")
        print("❌ ERROR OPENAI")
        print(str(e))
        print("")

        raise


    contenido = response.choices[0].message.content


    if not contenido:

        raise ValueError(
            "❌ OpenAI devolvió una respuesta vacía."
        )


    print("")
    print("========================================")
    print("RESPUESTA OPENAI:")
    print("========================================")
    print(contenido)
    print("========================================")
    print("")


    # =====================================================
    # LEER JSON
    # =====================================================

    try:

        data = json.loads(
            contenido
        )

    except json.JSONDecodeError as e:

        print("")
        print("❌ ERROR JSON OPENAI")
        print(contenido)
        print("")

        raise ValueError(
            "❌ OpenAI no devolvió JSON válido."
        ) from e


    # =====================================================
    # EXTRAER SQL
    # =====================================================

    sql = data.get("sql")


    if not sql:

        raise ValueError(
            "❌ El JSON de OpenAI no contiene 'sql'."
        )


    # =====================================================
    # VALIDAR
    # =====================================================

    sql = validar_sql(
        sql
    )


    # =====================================================
    # LOG SQL
    # =====================================================

    print("")
    print("========================================")
    print("SQL GENERADO:")
    print("========================================")
    print(sql)
    print("========================================")
    print("")


    return sql


# =========================================================
# GENERAR RESPUESTA HUMANA
# =========================================================

def generar_respuesta(
    pregunta,
    resultado
):

    prompt = f"""
Eres el Asistente Virtual institucional SIBE.

Responde al usuario utilizando ÚNICAMENTE
los resultados obtenidos de PostgreSQL.

NO inventes información.

NO agregues información externa.

NO cambies cantidades.

NO inventes hospitales.

NO inventes CLUES.

NO inventes fechas.

Responde siempre en español.

Sé claro, profesional y conciso.

Si la pregunta solicita un conteo,
muestra primero el total.

Si existe un único resultado,
responde directamente.

Si existen varios resultados,
utiliza una lista clara.

Puedes utilizar emojis moderadamente.


PREGUNTA DEL USUARIO:

{pregunta}


RESULTADO DE POSTGRESQL:

{resultado}


Genera únicamente la respuesta que verá
el usuario.
"""


    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres el Asistente Virtual "
                        "institucional del SIBE. "
                        "Solo puedes utilizar la "
                        "información proporcionada "
                        "por PostgreSQL."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2
        )

    except Exception as e:

        print("")
        print("❌ ERROR GENERANDO RESPUESTA")
        print(str(e))
        print("")

        raise


    respuesta = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )


    return respuesta