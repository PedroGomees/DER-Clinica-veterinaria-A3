"""CRUD de VACINA (cada linha é uma dose efetivamente aplicada).

Quando antirrabica = 1, a vacina precisa ser comunicada à API
governamental simulada. Isso é feito automaticamente logo depois do
INSERT, chamando app/services/governo_service.py. Se a comunicação
falhar, a vacina continua salva aqui; o reenvio é feito depois pela
tela de Integrações (POST /integracoes/<id>/reenviar)."""
from flask import Blueprint, g, jsonify, request

from app.auth import login_required
from app.db import get_conn
from app.services import governo_service
from app.validacoes import campos_faltando

bp = Blueprint("vacinas", __name__, url_prefix="/vacinas")

CAMPOS = """vc.id_vacina, vc.id_animal, a.nome AS nome_animal, vc.id_veterinario,
            vt.nome_completo AS nome_veterinario, vc.nome_vacina, vc.antirrabica,
            vc.fabricante, vc.lote, vc.data_aplicacao, vc.dose, vc.via_administracao,
            vc.proxima_dose, vc.observacao"""


def _select_base():
    return f"""SELECT {CAMPOS}
               FROM vacina vc
               JOIN animal a ON a.id_animal = vc.id_animal
               JOIN veterinario vt ON vt.id_veterinario = vc.id_veterinario"""


@bp.get("/")
@login_required
def listar():
    sql = _select_base() + " WHERE 1=1"
    parametros = []
    if request.args.get("id_animal"):
        sql += " AND vc.id_animal = %s"
        parametros.append(request.args["id_animal"])
    sql += " ORDER BY vc.data_aplicacao DESC"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, parametros)
        return jsonify(cur.fetchall())


@bp.get("/<int:id_vacina>")
@login_required
def buscar(id_vacina):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(_select_base() + " WHERE vc.id_vacina = %s", (id_vacina,))
        linha = cur.fetchone()
    if not linha:
        return jsonify({"erro": "vacina não encontrada"}), 404
    return jsonify(linha)


@bp.post("/")
@login_required
def criar():
    dados = request.get_json(silent=True) or {}
    faltando = campos_faltando(dados, ["id_animal", "nome_vacina", "data_aplicacao"])
    if faltando:
        return jsonify({"erro": f"campos obrigatórios: {', '.join(faltando)}"}), 400
    antirrabica = 1 if dados.get("antirrabica") else 0

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO vacina (id_animal, id_veterinario, nome_vacina, antirrabica, fabricante,
               lote, data_aplicacao, dose, via_administracao, proxima_dose, observacao)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                dados["id_animal"], g.veterinario["id_veterinario"], dados["nome_vacina"].strip(),
                antirrabica, dados.get("fabricante"), dados.get("lote"), dados["data_aplicacao"],
                dados.get("dose"), dados.get("via_administracao"), dados.get("proxima_dose"),
                dados.get("observacao"),
            ),
        )
        id_vacina = cur.lastrowid

    if antirrabica:
        governo_service.enviar_vacina_antirrabica(id_vacina, dados["id_animal"])

    return jsonify({"id_vacina": id_vacina}), 201


@bp.put("/<int:id_vacina>")
@login_required
def atualizar(id_vacina):
    dados = request.get_json(silent=True) or {}
    faltando = campos_faltando(dados, ["nome_vacina", "data_aplicacao"])
    if faltando:
        return jsonify({"erro": f"campos obrigatórios: {', '.join(faltando)}"}), 400
    antirrabica = 1 if dados.get("antirrabica") else 0

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE vacina SET nome_vacina=%s, antirrabica=%s, fabricante=%s, lote=%s,
               data_aplicacao=%s, dose=%s, via_administracao=%s, proxima_dose=%s, observacao=%s
               WHERE id_vacina = %s""",
            (
                dados["nome_vacina"].strip(), antirrabica, dados.get("fabricante"), dados.get("lote"),
                dados["data_aplicacao"], dados.get("dose"), dados.get("via_administracao"),
                dados.get("proxima_dose"), dados.get("observacao"), id_vacina,
            ),
        )
        if cur.rowcount == 0:
            return jsonify({"erro": "vacina não encontrada"}), 404
    return jsonify({"mensagem": "atualizada"})
