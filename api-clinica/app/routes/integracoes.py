"""Painel de acompanhamento da integração com o governo. Mostra o que foi
enviado, o que confirmou (com protocolo) e o que falhou, com um botão de
reenvio para os casos de falha."""
from flask import Blueprint, jsonify, request

from app.auth import login_required
from app.db import get_conn
from app.services import governo_service

bp = Blueprint("integracoes", __name__, url_prefix="/integracoes")

CAMPOS = """i.id_integracao, i.id_animal, a.nome AS nome_animal, i.id_vacina,
            i.tipo_operacao, i.status, i.protocolo, i.tentativas, i.data_criacao,
            i.ultima_tentativa, i.data_confirmacao, i.mensagem_erro"""


@bp.get("/")
@login_required
def listar():
    sql = f"""SELECT {CAMPOS} FROM integracao_governo i
              JOIN animal a ON a.id_animal = i.id_animal WHERE 1=1"""
    parametros = []
    if request.args.get("status"):
        sql += " AND i.status = %s"
        parametros.append(request.args["status"])
    if request.args.get("id_animal"):
        sql += " AND i.id_animal = %s"
        parametros.append(request.args["id_animal"])
    sql += " ORDER BY i.data_criacao DESC"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, parametros)
        return jsonify(cur.fetchall())


@bp.post("/<int:id_integracao>/reenviar")
@login_required
def reenviar(id_integracao):
    ok = governo_service.reenviar(id_integracao)
    if not ok:
        return jsonify({"erro": "integração não encontrada"}), 404

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT {CAMPOS} FROM integracao_governo i "
                     "JOIN animal a ON a.id_animal = i.id_animal "
                     "WHERE i.id_integracao = %s", (id_integracao,))
        return jsonify(cur.fetchone())
