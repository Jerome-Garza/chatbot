from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from ai import generar_sql, generar_respuesta
from db import ejecutar_query
from security import validar_consulta, limpiar_sql

import unicodedata


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="Chatbot SIBE",
    description="API del Asistente SIBE para consultas hospitalarias",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# MODELO DE PREGUNTA
# =========================================================

class Pregunta(BaseModel):
    mensaje: str


# =========================================================
# LIMPIAR TEXTO
# =========================================================

def limpiar_texto(texto: str) -> str:

    if not texto:
        return ""

    texto = texto.lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = texto.encode(
        "ascii",
        "ignore"
    ).decode("utf-8")

    return texto.strip()


# =========================================================
# FORMATEAR RESULTADOS DE POSTGRESQL
# =========================================================

def formatear(columnas, resultados):

    if not resultados:
        return "No se encontraron resultados para la consulta."

    texto = ""

    for fila in resultados:

        fila_txt = ", ".join(
            [
                f"{col}: {val}"
                for col, val in zip(columnas, fila)
                if val is not None
            ]
        )

        texto += fila_txt + "\n"

    return texto.strip()


# =========================================================
# ENDPOINT INICIO
# =========================================================

@app.get("/")
def inicio():

    return {
        "mensaje": "Chatbot SIBE funcionando"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
def chat(pregunta: Pregunta):

    try:

        # =================================================
        # 1. LIMPIAR PREGUNTA
        # =================================================

        texto = limpiar_texto(
            pregunta.mensaje
        )

        if not texto:

            return {
                "respuesta": "Escribe una pregunta."
            }


        print("\n========================================")
        print("PREGUNTA DEL USUARIO:")
        print(texto)
        print("========================================")


        # =================================================
        # 2. OPENAI GENERA SQL
        # =================================================

        print("\nGENERANDO SQL...")

        sql = generar_sql(texto)


        # =================================================
        # 3. LIMPIAR SQL
        # =================================================

        sql = limpiar_sql(sql)


        print("\nSQL GENERADO:")
        print(sql)


        # =================================================
        # 4. VALIDAR SQL
        # =================================================

        print("\nVALIDANDO SQL...")


        if not validar_consulta(sql):

            print("❌ SQL BLOQUEADO")

            return {
                "respuesta": (
                    "No fue posible procesar esta consulta "
                    "por motivos de seguridad."
                )
            }


        print("✅ SQL APROBADO")


        # =================================================
        # 5. EJECUTAR CONSULTA
        # =================================================

        print("\nEJECUTANDO CONSULTA EN POSTGRESQL...")


        columnas, resultados = ejecutar_query(sql)


        # =================================================
        # 6. FORMATEAR RESULTADOS
        # =================================================

        resultado_bd = formatear(
            columnas,
            resultados
        )


        print("\nRESULTADOS DE POSTGRESQL:")
        print(resultado_bd)


        # =================================================
        # 7. OPENAI INTERPRETA LOS RESULTADOS
        # =================================================

        print("\nGENERANDO RESPUESTA SIBE...")


        respuesta = generar_respuesta(
            pregunta.mensaje,
            resultado_bd
        )


        print("\nRESPUESTA SIBE:")
        print(respuesta)

        print("\n========================================")
        print("CONSULTA FINALIZADA")
        print("========================================\n")


        # =================================================
        # 8. RESPUESTA AL FRONTEND
        # =================================================

        return {
            "respuesta": respuesta
        }


    # =====================================================
    # MANEJO DE ERRORES
    # =====================================================

    except Exception as e:

        print("\n========================================")
        print("❌ ERROR EN CHATBOT SIBE")
        print("========================================")

        print(str(e))

        print("========================================\n")


        return {
            "respuesta": (
                "Ocurrió un error al procesar "
                "tu consulta. Intenta nuevamente."
            )
        }