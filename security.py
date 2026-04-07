def limpiar_sql(sql):
    # quitar bloques markdown
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def validar_sql(sql):
    sql = limpiar_sql(sql)
    sql_lower = sql.lower()

    palabras_prohibidas = ["delete", "drop", "update", "insert", "alter"]

    if any(p in sql_lower for p in palabras_prohibidas):
        return False

    if not sql_lower.startswith("select"):
        return False

    return True
def validar_columnas(sql):
    columnas_validas = ["clues", "nombre", "municipio", "estado", "tipo"]
    sql_lower = sql.lower()

    return any(col in sql_lower for col in columnas_validas)