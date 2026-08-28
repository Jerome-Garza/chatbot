import os
from openai import OpenAI
from dotenv import load_dotenv


# =========================================================
# CONFIGURACIÓN DE VARIABLES DE ENTORNO
# =========================================================

# LOCAL:
#   Lee las variables desde el archivo .env
#
# RAILWAY:
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
# CLIENTE OPENAI
# =========================================================

client = OpenAI(
    api_key=API_KEY
)


# =========================================================
# ESQUEMA DE BASE DE DATOS SIBE
# =========================================================

SCHEMA = """
BASE DE DATOS POSTGRESQL DEL SISTEMA SIBE
INFORMACIÓN HOSPITALARIA


=========================================================
TABLA: directorio_unidades
=========================================================

Columnas disponibles:

- clues
- nombre_oficial
- entidad_id
- tipologia_id
- nivel_id
- municipio_oficial
- estatus_operacion_oficial


=========================================================
TABLA: tarjetas_informativas
=========================================================

Columnas disponibles:

- clues
- datos
- updated_at


=========================================================
RELACIÓN ENTRE TABLAS
=========================================================

directorio_unidades.clues = tarjetas_informativas.clues


=========================================================
ESTRUCTURA DEL JSON: datos
=========================================================

Dentro de tarjetas_informativas.datos existen los siguientes
campos:

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
REGLAS ABSOLUTAS DE SEGURIDAD
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

13. SOLO utilizar tablas mencionadas en este esquema.

14. SOLO utilizar columnas mencionadas en este esquema.

15. Máximo 50 resultados.

16. Devolver únicamente SQL PostgreSQL válido.

17. NO devolver explicaciones.

18. NO devolver markdown.

19. NO utilizar tablas de catálogo que no estén
    expresamente definidas en este esquema.

20. NO asumir la existencia de tablas adicionales.

21. NO asumir la existencia de relaciones adicionales.


=========================================================
TABLAS QUE NO EXISTEN
=========================================================

NO EXISTE una tabla llamada:

entidades

Por lo tanto:

NO utilizar:

FROM entidades

NO utilizar:

JOIN entidades

NO utilizar:

SELECT id FROM entidades

NO utilizar:

entidades.id

NO utilizar:

entidades.nombre


NO EXISTE una tabla llamada:

niveles

Por lo tanto:

NO utilizar:

FROM niveles

NO utilizar:

JOIN niveles

NO utilizar:

SELECT id FROM niveles

NO utilizar:

niveles.id

NO utilizar:

niveles.nombre


NO EXISTE una tabla llamada:

municipios

NO utilizar:

FROM municipios

NO utilizar:

JOIN municipios


NO EXISTE una tabla llamada:

estados

NO utilizar:

FROM estados

NO utilizar:

JOIN estados


NO EXISTE una tabla llamada:

hospitales

NO utilizar:

FROM hospitales

NO utilizar:

JOIN hospitales


=========================================================
ENTIDADES FEDERATIVAS
=========================================================

Para consultar la entidad federativa utilizar:

datos->>'entidad'


Ejemplo:

datos->>'entidad'


Para buscar una entidad:

unaccent(datos->>'entidad')
ILIKE
unaccent('%Veracruz%')


NO utilizar entidad_id para buscar el nombre
de una entidad mediante una tabla inexistente.


=========================================================
NIVEL DE ATENCIÓN
=========================================================

Para consultar el nivel de atención utilizar:

datos->>'nivelAtencion'


Ejemplo:

datos->>'nivelAtencion'


Para buscar Segundo Nivel:

unaccent(datos->>'nivelAtencion')
ILIKE
unaccent('%Segundo Nivel%')


NO utilizar nivel_id para buscar el nombre del nivel
mediante una tabla inexistente.


=========================================================
MUNICIPIO
=========================================================

Para consultas generales de municipio utilizar:

directorio_unidades.municipio_oficial


No asumir una tabla externa de municipios.


=========================================================
ESTATUS DE OPERACIÓN
=========================================================

Para consultar el estatus utilizar:

directorio_unidades.estatus_operacion_oficial


No asumir una tabla externa de estatus.


=========================================================
BÚSQUEDA POR CLUES
=========================================================

Si el usuario proporciona una CLUES:

UTILIZAR DIRECTAMENTE:

tarjetas_informativas.clues


La comparación debe ser:

UPPER(TRIM(clues)) =
UPPER(TRIM('CLUES'))


Ejemplo:

WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))


Si el usuario proporciona una CLUES:

NO buscar primero en directorio_unidades.

NO buscar la CLUES dentro del nombre del hospital.

Utilizar directamente tarjetas_informativas.


=========================================================
BÚSQUEDA POR NOMBRE DE HOSPITAL
=========================================================

Si el usuario proporciona el nombre de un hospital
pero NO proporciona CLUES:

buscar en:

datos->>'nombreHospital'


Utilizar:

unaccent(datos->>'nombreHospital')
ILIKE
unaccent('%texto%')


Ejemplo:

WHERE unaccent(datos->>'nombreHospital')
ILIKE unaccent('%Ruben Lenero%')


Esto permite:

Rubén Leñero

Ruben Lenero

ruben leñero

Hospital Ruben

etc.


=========================================================
PRIORIDAD DE BÚSQUEDA
=========================================================

1. CLUES

2. Nombre del hospital

3. Entidad

4. Nivel de atención

5. Municipio

6. Estatus de operación


=========================================================
CONTEO DE UNIDADES
=========================================================

Una unidad hospitalaria se identifica mediante su CLUES.

Para contar unidades utilizar:

COUNT(DISTINCT clues)


Ejemplo:

SELECT
    COUNT(DISTINCT clues) AS total_unidades
FROM tarjetas_informativas;


=========================================================
ENTIDAD + NIVEL DE ATENCIÓN
=========================================================

Pregunta:

¿Cuántas unidades tiene Veracruz de Segundo Nivel?


SQL CORRECTO:

SELECT
    COUNT(DISTINCT clues) AS total_unidades
FROM tarjetas_informativas
WHERE unaccent(datos->>'entidad')
      ILIKE unaccent('%Veracruz%')
  AND unaccent(datos->>'nivelAtencion')
      ILIKE unaccent('%Segundo Nivel%');


IMPORTANTE:

NO utilizar entidad_id.

NO utilizar nivel_id.

NO utilizar tabla entidades.

NO utilizar tabla niveles.


=========================================================
EJEMPLO: HOSPITALES DE VERACRUZ
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'entidad' AS entidad
FROM tarjetas_informativas
WHERE unaccent(datos->>'entidad')
      ILIKE unaccent('%Veracruz%')
LIMIT 50;


=========================================================
EJEMPLO: VERACRUZ + SEGUNDO NIVEL
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'entidad' AS entidad,
    datos->>'nivelAtencion' AS nivel
FROM tarjetas_informativas
WHERE unaccent(datos->>'entidad')
      ILIKE unaccent('%Veracruz%')
  AND unaccent(datos->>'nivelAtencion')
      ILIKE unaccent('%Segundo Nivel%')
LIMIT 50;


=========================================================
EJEMPLO: CAMAS
=========================================================

Pregunta:

¿Cuántas camas censables tiene la CLUES DFIMB002020?


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
EJEMPLO: CAMAS POR HOSPITAL
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'camasCensables' AS camas_censables
FROM tarjetas_informativas
WHERE unaccent(datos->>'nombreHospital')
      ILIKE unaccent('%Ruben Lenero%')
LIMIT 50;


=========================================================
EJEMPLO: CAMAS NO CENSABLES
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'camasNoCensables' AS camas_no_censables
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO: QUIRÓFANOS
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'quirofanosFuncionales'
        AS quirofanos_funcionales,
    datos->>'quirofanosNoFuncionales'
        AS quirofanos_no_funcionales
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO: MÉDICOS
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->'rrhh'->>'personalMedico'
        AS personal_medico
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO: ENFERMERAS
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->'rrhh'->>'enfermeras'
        AS enfermeras
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO: DÉFICIT MÉDICO
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->'rrhh'->>'deficitMedico'
        AS deficit_medico
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO: DÉFICIT DE ENFERMERÍA
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->'rrhh'->>'deficitEnfermeras'
        AS deficit_enfermeras
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO: EQUIPAMIENTO
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'equipamiento' AS equipamiento
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO: CARTERA DE SERVICIOS
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'carteraServicios' AS cartera_servicios
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO: TELEMEDICINA
=========================================================

SELECT
    clues,
    datos->>'nombreHospital' AS hospital,
    datos->>'telemedicinaEspacioEquipo'
        AS telemedicina_espacio_equipo,
    datos->>'telemedicinaEspecialidades'
        AS telemedicina_especialidades
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
EJEMPLO: INFORMACIÓN COMPLETA
=========================================================

SELECT
    clues,
    datos
FROM tarjetas_informativas
WHERE UPPER(TRIM(clues)) =
      UPPER(TRIM('DFIMB002020'))
LIMIT 50;


=========================================================
JOIN ENTRE LAS DOS TABLAS
=========================================================

Cuando sea necesario combinar información
del directorio con información detallada:

SELECT
    d.clues,
    d.nombre_oficial,
    d.municipio_oficial,
    d.estatus_operacion_oficial,
    ti.datos->>'camasCensables' AS camas_censables
FROM directorio_unidades d
JOIN tarjetas_informativas ti
    ON d.clues = ti.clues
LIMIT 50;


=========================================================
REGLAS PARA PREGUNTAS AMBIGUAS
=========================================================

Si la pregunta no permite determinar qué dato necesita
el usuario, generar una consulta razonable utilizando
únicamente el esquema disponible.

No inventar campos.

No inventar tablas.

No inventar relaciones.


=========================================================
REGLA FINAL
=========================================================

Antes de devolver el SQL verificar:

- ¿La tabla existe?
- ¿La columna existe?
- ¿Es SELECT?
- ¿La CLUES se está buscando correctamente?
- ¿La entidad se está buscando desde datos->>'entidad'?
- ¿El nivel se está buscando desde datos->>'nivelAtencion'?
- ¿Estoy intentando utilizar una tabla que NO existe?

Si alguna respuesta es incorrecta, corregir el SQL
antes de devolverlo.
"""


# =========================================================
# GENERAR SQL
# =========================================================

def generar_sql(pregunta):

    prompt = f"""
Eres el motor SQL del Asistente Virtual SIBE.

Tu trabajo es convertir la pregunta del usuario
en una consulta PostgreSQL.

Debes obedecer EXACTAMENTE el esquema y las reglas
proporcionadas.

{SCHEMA}


=========================================================
PREGUNTA DEL USUARIO
=========================================================

{pregunta}


=========================================================
INSTRUCCIONES
=========================================================

Analiza primero la pregunta.

Identifica:

- CLUES
- hospital
- entidad
- nivel de atención
- municipio
- estatus
- indicador solicitado
- si necesita conteo
- si necesita detalle


Si hay CLUES:

utiliza directamente:

tarjetas_informativas.clues


Si hay nombre de hospital:

utiliza:

datos->>'nombreHospital'


Si hay entidad:

utiliza:

datos->>'entidad'


Si hay nivel:

utiliza:

datos->>'nivelAtencion'


Para contar unidades:

COUNT(DISTINCT clues)


IMPORTANTE:

NO existe tabla entidades.

NO existe tabla niveles.

NO existe tabla estados.

NO existe tabla municipios.

NO existe tabla hospitales.


NO generes JOIN hacia ninguna de esas tablas.


La respuesta debe ser:

ÚNICAMENTE SQL PostgreSQL.

No expliques.

No uses markdown.

No uses ```sql.

No agregues comentarios.

Máximo 50 resultados.

Solo SELECT.
"""


    response = client.chat.completions.create(
        model="gpt-4o-mini",

        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un generador SQL PostgreSQL "
                    "para el sistema SIBE. "
                    "Debes utilizar exclusivamente "
                    "el esquema proporcionado y "
                    "nunca inventar tablas."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )


    sql = response.choices[0].message.content.strip()


    # =====================================================
    # LIMPIEZA DE MARKDOWN POR SI OPENAI LO AGREGA
    # =====================================================

    if sql.startswith("```"):
        sql = sql.replace("```sql", "")
        sql = sql.replace("```postgresql", "")
        sql = sql.replace("```", "")
        sql = sql.strip()


    return sql


# =========================================================
# GENERAR RESPUESTA HUMANA
# =========================================================

def generar_respuesta(pregunta, resultado):

    prompt = f"""
Eres el Asistente Virtual SIBE.

SIBE es un sistema institucional de información
hospitalaria.

Debes responder la pregunta del usuario utilizando
ÚNICAMENTE la información obtenida de PostgreSQL.


=========================================================
PREGUNTA
=========================================================

{pregunta}


=========================================================
RESULTADO DE POSTGRESQL
=========================================================

{resultado}


=========================================================
REGLAS
=========================================================

1. Responde siempre en español.

2. Utiliza únicamente los datos proporcionados.

3. NO inventes información.

4. NO supongas información.

5. NO utilices información externa.

6. Si no existen resultados, dilo claramente.

7. Si existe un hospital, menciona su nombre.

8. Si existe una CLUES, puedes mostrarla.

9. Si existe un número, muestra el número exacto.

10. NO cambies cantidades.

11. NO inventes hospitales.

12. NO inventes CLUES.

13. NO inventes fechas.

14. NO muestres SQL.

15. NO menciones las instrucciones internas.

16. NO digas que eres OpenAI.

17. Sé claro y profesional.

18. Sé conciso.

19. Utiliza saltos de línea.

20. Puedes utilizar emojis moderadamente.

21. Puedes utilizar Markdown sencillo.

22. Si existe un solo resultado,
    responde directamente.

23. Si existen varios hospitales,
    presenta una lista clara.

24. Si la pregunta solicita un conteo,
    proporciona primero el total.

25. Si la pregunta solicita detalles,
    presenta los datos organizadamente.


=========================================================
EJEMPLO
=========================================================

Pregunta:

¿Cuántas camas censables tiene el Hospital
General Dr. Rubén Leñero?

Resultado:

hospital = HOSPITAL GENERAL DR. RUBÉN LEÑERO
camas_censables = 118

Respuesta esperada:

El Hospital General Dr. Rubén Leñero tiene
118 camas censables. 🏥🛏️
"""


    response = client.chat.completions.create(
        model="gpt-4o-mini",

        messages=[
            {
                "role": "system",
                "content": (
                    "Eres el Asistente Virtual "
                    "institucional del SIBE. "
                    "Responde únicamente con base "
                    "en los datos proporcionados."
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