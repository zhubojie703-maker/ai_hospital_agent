import re


FORBIDDEN_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "truncate",
    "replace",
    "attach",
    "detach",
    "pragma",
    "vacuum",
}


def _strip_sql_comments(sql: str) -> str:
    sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql.strip()


def validate_select_sql(sql: str) -> str:
    """Return normalized SQL if it is a safe SELECT query."""
    if not sql or not sql.strip():
        raise ValueError("SQL 为空，无法执行。")

    normalized = _strip_sql_comments(sql).strip()
    statements = [part.strip() for part in normalized.split(";") if part.strip()]
    if len(statements) != 1:
        raise ValueError("只允许执行单条 SELECT 查询。")

    statement = statements[0]
    lower = statement.lower()
    if not (lower.startswith("select") or lower.startswith("with")):
        raise ValueError("只允许执行 SELECT 查询。")

    tokens = set(re.findall(r"\b[a-z_]+\b", lower))
    blocked = tokens.intersection(FORBIDDEN_KEYWORDS)
    if blocked:
        raise ValueError(f"SQL 包含禁止关键字：{', '.join(sorted(blocked))}")

    return statement


def add_default_limit(sql: str, limit: int = 10) -> str:
    statement = validate_select_sql(sql)
    lower = statement.lower()
    if " limit " in f" {lower} ":
        return statement
    return f"{statement} LIMIT {limit}"
