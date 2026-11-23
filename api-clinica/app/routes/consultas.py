"""CRUD de CONSULTA.

O veterinário que registra a consulta é sempre o que está logado (vem do
token, em g.veterinario) - o frontend não manda id_veterinario."""
from flask import Blueprint, g, jsonify, request

from app.auth import login_required
from app.db import get_conn
from app.validacoes import campos_faltando

bp = Blueprint("consultas", __name__, url_prefix="/consultas")

CAMPOS = """c.id_consulta, c.id_animal, a.nome AS nome_animal, c.id_veterinario,
            v.nome_completo AS nome_veterinario, c.data_hora, c.motivo, c.historico,
            c.sintomas, c.diagnostico, c.tratamento, c.status"""

STATUS_VALIDOS = ("AGENDADA", "EM_ATENDIMENTO", "CONCLUIDA", "CANCELADA")


def _select_base():
    return f"""SELECT {CAMPOS}
               FROM consulta c
               JOIN animal a ON a.id_animal = c.id_animal
               JOIN veterinario v ON v.id_veterinario = c.id_veterinario"""


@bp.get("/")
@login_required
def listar():
    sql = _select_base() + " WHERE 1=1"
    parametros = []
    if request.args.get("id_animal"):
        sql += " AND c.id_animal = %s"
        parametros.append(request.args["id_animal"])
    if request.args.get("status"):
        sql += " AND c.status = %s"
        parametros.append(request.args["status"])
    sql += " ORDER BY c.data_hora DESC"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, parametros)
        return jsonify(cur.fetchall())


@bp.get("/<int:id_consulta>")
@login_required
def buscar(id_consulta):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(_select_base() + " WHERE c.id_consulta = %s", (id_consulta,))
        linha = cur.fetchone()
    if not linha:
        return jsonify({"erro": "consulta não encontrada"}), 404
    return jsonify(linha)


@bp.post("/")
@login_required
def criar():
    dados = request.get_json(silent=True) or {}
    faltando = campos_faltando(dados, ["id_animal", "data_hora", "motivo"])
    if faltando:
        return jsonify({"erro": f"campos obrigatórios: {', '.join(faltando)}"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO consulta (id_animal, id_veterinario, data_hora, motivo, historico,
               sintomas, diagnostico, tratamento, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                dados["id_animal"], g.veterinario["id_veterinario"], dados["data_hora"],
                dados["motivo"].strip(), dados.get("historico"), dados.get("sintomas"),
                dados.get("diagnostico"), dados.get("tratamento"), dados.get("status", "AGENDADA"),
            ),
        )
        return jsonify({"id_consulta": cur.lastrowid}), 201


@bp.put("/<int:id_consulta>")
@login_required
def atualizar(id_consulta):
    dados = request.get_json(silent=True) or {}
    faltando = campos_faltando(dados, ["data_hora", "motivo"])
    if faltando:
        return jsonify({"erro": f"campos obrigatórios: {', '.join(faltando)}"}), 400
    status = dados.get("status", "AGENDADA")
    if status not in STATUS_VALIDOS:
        return jsonify({"erro": f"status deve ser um de: {', '.join(STATUS_VALIDOS)}"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE consulta SET data_hora=%s, motivo=%s, historico=%s, sintomas=%s,
               diagnostico=%s, tratamento=%s, status=%s WHERE id_consulta = %s""",
            (
                dados["data_hora"], dados["motivo"].strip(), dados.get("historico"),
                dados.get("sintomas"), dados.get("diagnostico"), dados.get("tratamento"),
                status, id_consulta,
            ),
        )
        if cur.rowcount == 0:
            return jsonify({"erro": "consulta não encontrada"}), 404
    return jsonify({"mensagem": "atualizada"})


@bp.delete("/<int:id_consulta>")
@login_required
def cancelar(id_consulta):
    # Consulta é histórico clínico: "excluir" aqui significa marcar como CANCELADA.
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE consulta SET status = 'CANCELADA' WHERE id_consulta = %s", (id_consulta,))
        if cur.rowcount == 0:
            return jsonify({"erro": "consulta não encontrada"}), 404
    return jsonify({"mensagem": "cancelada"})
