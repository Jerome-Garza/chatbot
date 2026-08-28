def limpiar_sql(sql):
    if not sql:
        return ""

    sql = sql.replace("```sql", "")
    sql = sql.replace("```SQL", "")
    sql = sql.replace("```", "")

    return sql.strip()


def validar_sql(sql):
    sql = limpiar_sql(sql)

    if not sql:
        return False

    sql_lower = sql.lower().strip()

    palabras_prohibidas = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "grant",
        "revoke",
        "replace",
        "merge",
        "comment",
        "vacuum",
        "analyze",
        "refresh",
        "do",
        "call"
    ]

    for palabra in palabras_prohibidas:
        if palabra in sql_lower:
            return False

    if not sql_lower.startswith("select"):
        return False

    if ";" in sql_lower[:-1]:
        return False

    tablas_permitidas = [
        "directorio_unidades",
        "tarjetas_informativas",
        "cat_estatus_unidades"
    ]

    if not any(tabla in sql_lower for tabla in tablas_permitidas):
        return False

    return True


def validar_columnas(sql):
    sql = limpiar_sql(sql)
    sql_lower = sql.lower()

    columnas_validas = [
        "clues",
        "nombre_oficial",
        "entidad_id",
        "tipologia_id",
        "nivel_id",
        "municipio_oficial",
        "estatus_operacion_oficial",
        "datos",
        "updated_at",
        "nombrehospital",
        "entidad",
        "nivelatencion",
        "camascensables",
        "camasnocensables",
        "quirofanosfuncionales",
        "quirofanosnofuncionales",
        "abastomedicamentos",
        "abastomaterialcuracion",
        "telemedicinaespacioequipo",
        "telemedicinaespecialidades",
        "carteraservicios",
        "equipamiento",
        "datoscontacto",
        "contextohistorico",
        "serviciosgenerales",
        "serviciosmedicointegrales",
        "situacionactual",
        "rrhh",
        "detallescartera",
        "updated_at"
    ]

    return any(columna in sql_lower for columna in columnas_validas)


def validar_consulta(sql):
    sql = limpiar_sql(sql)

    if not validar_sql(sql):
        return False

    if not validar_columnas(sql):
        return False

    return True