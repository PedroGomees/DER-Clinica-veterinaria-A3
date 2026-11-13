import pymysql
from flask import current_app


def get_conn():
    """Abre uma conexão com o MariaDB. Use assim:

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT ... WHERE id = %s", (valor,))

    Sempre passe os valores em tupla com %s (nunca concatene texto no SQL).
    """
    c = current_app.config
    return pymysql.connect(
        host=c["DB_HOST"],
        port=c["DB_PORT"],
        user=c["DB_USER"],
        password=c["DB_PASSWORD"],
        database=c["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
