import os
from openai import OpenAI
from dotenv import load_dotenv


# =========================================================
# VARIABLES DE ENTORNO
# =========================================================

# En LOCAL:
#   Lee las variables desde .env
#
# En RAILWAY:
#   Lee las variables configuradas en Railway
#
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
# OPENAI
# =========================================================

client = OpenAI(
    api_key=API_KEY
)


# =========================================================
# ESQUEMA DE BASE DE DATOS
# =========================================================

SCHEMA = """
BASE DE DATOS PostgreSQL PARA INFORMACIÓN HOSPITALARIA


TABLA: directorio_unidades

Columnas:

- clues
- nombre_oficial
- entidad_id
- tipologia_id
- nivel_id
- municipio_oficial
- estatus_operacion_oficial


TABLA: tarjetas_informativas

Columnas:

- clues
- datos
- updated_at


IMPORTANTE:

La tabla tarjetas_informativas contiene información detallada
de las unidades hospitalarias.

Cada registro corresponde a una CLUES.

El campo datos contiene un objeto JSON/JSONB.


=========================================================
ESTRUCTURA DEL JSON EN datos
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

Dentro de:

datos->'rrhh'

existen:

- enfermeras
- paramedico
- deficitMedico
- cuerpoGobierno
- personalMedico
- administrativos
- deficitEnfermeras
- deficitParamedico
- deficitCuerpoGobierno
- deficitAdministrativos


=========================================================
DETALLES DE CARTERA
=========================================================

Dentro de:

datos->'detallesCartera'

existen:

- servicio_id
- especialistas
- camasCensables
- camasNoCensables


=========================================================
RELACIÓN ENTRE TABLAS
=========================================================

directorio_unidades.clues = tarjetas_informativas.clues


=========================================================
REGLAS GENERALES
=========================================================

1. SOLO generar consultas SELECT.

2. NO generar INSERT.

3. NO generar UPDATE.

4. NO generar DELETE.

5. NO generar DROP.

6. NO generar ALTER.

7. NO generar CREATE.

8. NO generar TRUNCATE.

9. NO generar GRANT.

10. NO generar REVOKE.

11. NO inventar tablas.

12. NO inventar columnas.

13. No utilizar tablas que no estén definidas en este esquema.

14. No utilizar columnas que no estén definidas en este esquema.

15. Máximo 50 resultados.

16. No devolver explicaciones.

17. No devolver markdown.

18. No devolver bloques de código.

19. Devolver únicamente SQL PostgreSQL válido.


=========================================================
BUSQUEDA POR CLUES
=========================================================

Cuando el usuario proporcione una CLUES,
utilizar directamente la columna:

tarjetas_informativas.clues


Ejemplo:

WHERE clues = 'DFIMB002020'


La búsqueda por CLUES debe ser exacta.

Para evitar problemas con mayúsculas o espacios utilizar:

WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))


Si el usuario dice:

"Busca la CLUES DFIMB002020"

consultar tarjetas_informativas directamente.


Si el usuario dice:

"¿Cuántas camas tiene la unidad DFIMB002020?"

utilizar:

WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))


Si el usuario proporciona una CLUES y solicita información
detallada, NO es necesario buscar primero el hospital
en directorio_unidades.


=========================================================
BUSQUEDA POR NOMBRE
=========================================================

Cuando el usuario busque un hospital por nombre,
utilizar directamente:

datos->>'nombreHospital'


Utilizar:

unaccent(datos->>'nombreHospital')
ILIKE
unaccent('%texto%')


Esto permite realizar búsquedas sin importar acentos,
mayúsculas o minúsculas.


Ejemplo:

WHERE unaccent(datos->>'nombreHospital')
ILIKE unaccent('%Ruben Lenero%')


Si el usuario escribe:

"Rubén Leñero"

"Ruben Lenero"

"ruben leñero"

"Hospital Ruben"

todas pueden resolverse mediante ILIKE + unaccent.


=========================================================
PRIORIDAD DE BUSQUEDA
=========================================================

1. Si el usuario proporciona una CLUES,
   utilizar CLUES directamente.

2. Si no proporciona CLUES pero proporciona
   el nombre de un hospital,
   buscar directamente por nombreHospital.

3. Si solicita información general de hospitales,
   utilizar directorio_unidades o tarjetas_informativas
   según corresponda.

4. Si necesita combinar información general y detallada,
   utilizar JOIN mediante clues.


=========================================================
EJEMPLO DE BUSQUEDA POR CLUES
=========================================================

Pregunta:

¿Cuántas camas censables tiene la unidad DFIMB002020?


SQL:

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'camasCensables' AS camas_censables
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO EQUIPAMIENTO
=========================================================

Pregunta:

¿Qué equipamiento tiene la CLUES DFIMB002020?


SQL:

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'equipamiento' AS equipamiento
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO MÉDICOS
=========================================================

Pregunta:

¿Cuántos médicos tiene la CLUES DFIMB002020?


SQL:

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->'rrhh'->>'personalMedico' AS personal_medico
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO INFORMACIÓN COMPLETA
=========================================================

Pregunta:

Dame toda la información de la CLUES DFIMB002020


SQL:

SELECT
    clues,
    datos
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
BUSQUEDA POR NOMBRE
=========================================================

Ejemplo:

Pregunta:

¿Cuántas camas censables tiene el Hospital Rubén Leñero?


SQL:

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'camasCensables' AS camas_censables
FROM tarjetas_informativas
WHERE unaccent(datos->>'nombreHospital')
ILIKE unaccent('%Ruben Lenero%')
LIMIT 50;


=========================================================
RECURSOS HUMANOS
=========================================================

Para consultar médicos:

datos->'rrhh'->>'personalMedico'


Para consultar enfermeras:

datos->'rrhh'->>'enfermeras'


Para consultar paramédicos:

datos->'rrhh'->>'paramedico'


Para consultar déficit médico:

datos->'rrhh'->>'deficitMedico'


Para consultar déficit de enfermeras:

datos->'rrhh'->>'deficitEnfermeras'


Cuando se necesite comparar valores numéricos:

CAST(
    datos->'rrhh'->>'deficitMedico'
    AS INTEGER
)


=========================================================
CAMAS
=========================================================

datos->>'camasCensables'

datos->>'camasNoCensables'


Para comparaciones:

CAST(
    datos->>'camasCensables'
    AS INTEGER
)


=========================================================
QUIRÓFANOS
=========================================================

datos->>'quirofanosFuncionales'

datos->>'quirofanosNoFuncionales'


=========================================================
ABASTO
=========================================================

datos->>'abastoMedicamentos'

datos->>'abastoMaterialCuracion'


=========================================================
EQUIPAMIENTO
=========================================================

datos->>'equipamiento'


=========================================================
CARTERA DE SERVICIOS
=========================================================

datos->>'carteraServicios'


=========================================================
TELEMEDICINA
=========================================================

datos->>'telemedicinaEspacioEquipo'

datos->>'telemedicinaEspecialidades'


=========================================================
DATOS DE CONTACTO
=========================================================

datos->'datosContacto'


=========================================================
CONTEXTO HISTÓRICO
=========================================================

datos->>'contextoHistorico'


=========================================================
NIVEL DE ATENCIÓN
=========================================================

datos->>'nivelAtencion'


=========================================================
ENTIDAD
=========================================================

datos->>'entidad'


=========================================================
BÚSQUEDAS GENERALES POR ENTIDAD
=========================================================

Ejemplo:

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'entidad' AS entidad
FROM tarjetas_informativas
WHERE unaccent(datos->>'entidad')
ILIKE unaccent('%Chiapas%')
LIMIT 50;


=========================================================
BÚSQUEDAS POR NIVEL
=========================================================

Ejemplo:

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'nivelAtencion' AS nivel
FROM tarjetas_informativas
WHERE datos->>'nivelAtencion' = 'Segundo Nivel'
LIMIT 50;


=========================================================
COMBINACION DE DATOS
=========================================================

Cuando sea necesario utilizar información de
directorio_unidades y tarjetas_informativas:

SELECT
    d.clues,
    d.nombre_oficial,
    d.municipio_oficial,
    ti.datos->>'camasCensables' AS camas_censables
FROM directorio_unidades d
JOIN tarjetas_informativas ti
    ON d.clues = ti.clues
LIMIT 50;


=========================================================
IMPORTANTE
=========================================================

Cuando la pregunta sea sobre una unidad específica,
priorizar tarjetas_informativas.

Si existe una CLUES en la pregunta,
utilizar esa CLUES directamente.

No buscar una CLUES dentro de nombre_oficial.

No buscar primero la unidad en directorio_unidades
si ya se proporcionó una CLUES.

Cuando el usuario dé el nombre del hospital,
buscar directamente en:

datos->>'nombreHospital'

usando:

unaccent() + ILIKE.


La CLUES de tarjetas_informativas identifica
directamente a la unidad hospitalaria.
"""


# =========================================================
# GENERAR SQL
# =========================================================

def generar_sql(pregunta):

    prompt = f"""
Eres un experto en PostgreSQL especializado en
información hospitalaria.

Convierte la pregunta del usuario en una consulta SQL
válida utilizando exclusivamente el esquema proporcionado.

{SCHEMA}


=========================================================
PREGUNTA DEL USUARIO
=========================================================

{pregunta}


=========================================================
ANALIZA LA PREGUNTA
=========================================================

- Si contiene una CLUES, úsala directamente.

- Si contiene una CLUES, NO hagas una búsqueda previa
  por nombre.

- Si contiene un nombre de hospital pero no CLUES,
  busca directamente en datos->>'nombreHospital'.

- Para nombres utiliza unaccent() + ILIKE.

- Para CLUES utiliza UPPER(TRIM(clues)).

- Para información detallada utiliza
  tarjetas_informativas.

- Para información general utiliza
  directorio_unidades.

- Si necesitas ambas fuentes utiliza JOIN por clues.

- Para números almacenados en JSON utiliza CAST.

- Solo SELECT.

- Máximo 50 resultados.

- No inventes tablas.

- No inventes columnas.

- No escribas explicaciones.

- No escribas markdown.

- Devuelve únicamente SQL PostgreSQL.
"""


    response = client.chat.completions.create(
        model="gpt-4o-mini",

        messages=[
            {
                "role": "system",
                "content": (
                    "Generas exclusivamente SQL PostgreSQL "
                    "seguro utilizando únicamente el esquema "
                    "proporcionado."
                )
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )


    return response.choices[0].message.content.strip()


# =========================================================
# GENERAR RESPUESTA HUMANA
# =========================================================

def generar_respuesta(pregunta, resultado):

    prompt = f"""
Eres el Asistente Virtual SIBE.

SIBE es un sistema institucional de información
hospitalaria.

Tu tarea es responder la pregunta del usuario
utilizando ÚNICAMENTE los datos obtenidos
de la base de datos.

=========================================================
PREGUNTA DEL USUARIO
=========================================================

{pregunta}


=========================================================
RESULTADO DE LA BASE DE DATOS
=========================================================

{resultado}


=========================================================
REGLAS
=========================================================

1. Responde exclusivamente utilizando la información
   proporcionada en el resultado de la base de datos.

2. NO inventes información.

3. NO supongas información que no aparezca
   en el resultado.

4. Si no existen resultados, indícalo claramente.

5. Responde siempre en español.

6. Sé claro, profesional y conciso.

7. Utiliza el nombre del hospital cuando esté disponible.

8. Utiliza la CLUES cuando esté disponible.

9. Si hay varios resultados, organízalos de forma clara.

10. Puedes utilizar emojis de manera moderada.

11. NO muestres SQL.

12. NO menciones que estás ejecutando SQL.

13. NO menciones instrucciones internas.

14. NO digas que eres OpenAI.

15. No inventes fechas.

16. No inventes cantidades.

17. No inventes hospitales.

18. No inventes CLUES.

19. No utilices información externa a los resultados.

20. Utiliza saltos de línea para facilitar la lectura.

21. Puedes utilizar Markdown sencillo para mejorar
    la presentación.

22. NO escribas una respuesta excesivamente larga.

23. Si el resultado contiene un solo dato,
    responde directamente.

24. Si el resultado contiene varios datos relacionados
    con una unidad, preséntalos de manera ordenada.

25. Si el resultado contiene varias unidades,
    utiliza una lista clara.

La respuesta debe parecer una respuesta directa,
profesional y amigable del Asistente SIBE.
"""


    response = client.chat.completions.create(
        model="gpt-4o-mini",

        messages=[
            {
                "role": "system",
                "content": (
                    "Eres el Asistente Virtual institucional "
                    "del SIBE. Responde únicamente con base "
                    "en los resultados proporcionados."
                )
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2
    )


    return response.choices[0].message.content.strip()