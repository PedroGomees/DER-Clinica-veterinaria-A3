"""Vínculo de microchip.

Regra do DER: um animal só pode ter UM vínculo ativo por vez, e um número
de chip só pode estar ativo em UM animal por vez. O banco garante isso
com índices únicos "parciais" (colunas geradas animal_ativo/chip_ativo em
vinculo_microchip). Aqui na API fazemos a mesma conferência ANTES de
tentar gravar, só para devolver uma mensagem de erro clara; o banco é
quem garante a regra de verdade, por último.

Nunca apagamos uma linha desta tabela: "desvincular" marca ativo=0 e
preenche data_desvinculacao, preservando o histórico."""
import pymysql
from flask import Blueprint, g, jsonify, request

from app.auth import login_required
from app.db import get_conn
from app.validacoes import campos_faltando

bp = Blueprint("microchips", __name__, url_prefix="/microchips")

CAMPOS = """m.id_vinculo, m.id_animal, a.nome AS nome_animal, m.id_veterinario,
            v.nome_completo AS nome_veterinario, m.numero_microchip, m.data_vinculacao,
            m.data_desvinculacao, m.ativo, m.observacao"""


def _select_base():
    return f"""SELECT {CAMPOS}
               FROM vinculo_microchip m
               JOIN animal a ON a.id_animal = m.id_animal
               JOIN veterinario v ON v.id_veterinario = m.id_veterinario"""


@bp.get("/")
@login_required
def listar():
    # histórico completo de um animal, mais recente primeiro
    sql = _select_base() + " WHERE 1=1"
    parametros = []
    if request.args.get("id_animal"):
        sql += " AND m.id_animal = %s"
        parametros.append(request.args["id_animal"])
    sql += " ORDER BY m.data_vinculacao DESC"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, parametros)
        return jsonify(cur.fetchall())


@bp.post("/")
@login_required
def vincular():
    dados = request.get_json(silent=True) or {}
    faltando = campos_faltando(dados, ["id_animal", "numero_microchip"])
    if faltando:
        return jsonify({"erro": f"campos obrigatórios: {', '.join(faltando)}"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id_vinculo FROM vinculo_microchip WHERE id_animal = %s AND ativo = 1",
            (dados["id_animal"],),
        )
        if cur.fetchone():
            return jsonify({"erro": "este animal já tem um microchip ativo; desvincule antes"}), 409

        cur.execute(
            "SELECT id_vinculo FROM vinculo_microchip WHERE numero_microchip = %s AND ativo = 1",
            (dados["numero_microchip"],),
        )
        if cur.fetchone():
            return jsonify({"erro": "este número de microchip já está em uso em outro animal"}), 409

        try:
            cur.execute(
                """INSERT INTO vinculo_microchip (id_animal, id_veterinario, numero_microchip, observacao)
                   VALUES (%s, %s, %s, %s)""",
                (dados["id_animal"], g.veterinario["id_veterinario"], dados["numero_microchip"],
                 dados.get("observacao")),
            )
        except pymysql.err.IntegrityError:
            # segunda linha de defesa: o próprio banco recusou (condição de corrida)
            return jsonify({"erro": "conflito de vínculo de microchip, tente novamente"}), 409
        return jsonify({"id_vinculo": cur.lastrowid}), 201


@bp.post("/<int:id_vinculo>/desvincular")
@login_required
def desvincular(id_vinculo):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE vinculo_microchip SET ativo = 0, data_desvinculacao = NOW()
               WHERE id_vinculo = %s AND ativo = 1""",
            (id_vinculo,),
        )
        if cur.rowcount == 0:
            return jsonify({"erro": "vínculo não encontrado ou já estava inativo"}), 404
    return jsonify({"mensagem": "desvinculado"})
