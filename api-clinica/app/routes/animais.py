"""CRUD de ANIMAL.

Duas regras do DER que valem a pena destacar:
- a raça precisa pertencer à espécie escolhida (o banco garante isso com
  uma chave estrangeira composta: fk_animal_raca_especie);
- se o tutor não souber a raça, o cadastro deve usar a raça "SRD" daquela
  espécie (criada pelo seed.sql), em vez de deixar em branco.

Depois de criar ou atualizar um animal, avisamos a API governamental
simulada em segundo plano (ver app/services/governo_service.py). Se a
notificação falhar, o cadastro do animal aqui na clínica NÃO é desfeito:
a falha fica registrada em integracao_governo para reenvio depois.
"""
import pymysql
from flask import Blueprint, jsonify, request

from app.auth import login_required
from app.db import get_conn
from app.services import governo_service
from app.validacoes import campos_faltando

bp = Blueprint("animais", __name__, url_prefix="/animais")

CAMPOS = """a.id_animal, a.nome, a.id_especie, esp.nome AS nome_especie,
            a.id_raca, r.nome AS nome_raca, a.sexo, a.dt_nasc, a.porte,
            a.id_tutor, t.nome_completo AS nome_tutor, a.observacao, a.ativo"""


def _select_base():
    return f"""SELECT {CAMPOS}
               FROM animal a
               JOIN especie esp ON esp.id_especie = a.id_especie
               JOIN raca r ON r.id_raca = a.id_raca
               JOIN tutor t ON t.id_tutor = a.id_tutor"""


@bp.get("/")
@login_required
def listar():
    sql = _select_base() + " WHERE 1=1"
    parametros = []
    if request.args.get("id_tutor"):
        sql += " AND a.id_tutor = %s"
        parametros.append(request.args["id_tutor"])
    if request.args.get("q"):
        sql += " AND a.nome LIKE %s"
        parametros.append(f"%{request.args['q']}%")
    if request.args.get("todos") != "1":
        sql += " AND a.ativo = 1"
    sql += " ORDER BY a.nome"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, parametros)
        return jsonify(cur.fetchall())


@bp.get("/<int:id_animal>")
@login_required
def buscar(id_animal):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(_select_base() + " WHERE a.id_animal = %s", (id_animal,))
        linha = cur.fetchone()
    if not linha:
        return jsonify({"erro": "animal não encontrado"}), 404
    return jsonify(linha)


def _validar(dados):
    faltando = campos_faltando(dados, ["nome", "id_especie", "id_raca", "sexo", "id_tutor"])
    if faltando:
        return f"campos obrigatórios: {', '.join(faltando)}"
    if dados["sexo"] not in ("M", "F"):
        return "sexo deve ser 'M' ou 'F'"
    if dados.get("porte") and dados["porte"] not in ("PEQUENO", "MEDIO", "GRANDE"):
        return "porte deve ser PEQUENO, MEDIO ou GRANDE"
    return None


@bp.post("/")
@login_required
def criar():
    dados = request.get_json(silent=True) or {}
    erro = _validar(dados)
    if erro:
        return jsonify({"erro": erro}), 400
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO animal (nome, id_especie, id_raca, sexo, dt_nasc, porte, id_tutor, observacao)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    dados["nome"].strip(), dados["id_especie"], dados["id_raca"], dados["sexo"],
                    dados.get("dt_nasc"), dados.get("porte"), dados["id_tutor"], dados.get("observacao"),
                ),
            )
            id_animal = cur.lastrowid
    except pymysql.err.IntegrityError:
        return jsonify({"erro": "tutor, espécie ou raça inválidos (ou a raça não pertence à espécie)"}), 400

    # Avisa o "governo" que existe um animal novo. Não trava a resposta nem
    # desfaz o cadastro se isso falhar: fica pendente em integracao_governo.
    governo_service.enviar_cadastro_animal(id_animal, tipo_operacao="CADASTRO_ANIMAL")

    return jsonify({"id_animal": id_animal}), 201


@bp.put("/<int:id_animal>")
@login_required
def atualizar(id_animal):
    dados = request.get_json(silent=True) or {}
    erro = _validar(dados)
    if erro:
        return jsonify({"erro": erro}), 400
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """UPDATE animal SET nome=%s, id_especie=%s, id_raca=%s, sexo=%s, dt_nasc=%s,
                   porte=%s, id_tutor=%s, observacao=%s WHERE id_animal = %s""",
                (
                    dados["nome"].strip(), dados["id_especie"], dados["id_raca"], dados["sexo"],
                    dados.get("dt_nasc"), dados.get("porte"), dados["id_tutor"], dados.get("observacao"),
                    id_animal,
                ),
            )
            if cur.rowcount == 0:
                return jsonify({"erro": "animal não encontrado"}), 404
    except pymysql.err.IntegrityError:
        return jsonify({"erro": "tutor, espécie ou raça inválidos (ou a raça não pertence à espécie)"}), 400

    governo_service.enviar_cadastro_animal(id_animal, tipo_operacao="ATUALIZACAO_ANIMAL")

    return jsonify({"mensagem": "atualizado"})


@bp.delete("/<int:id_animal>")
@login_required
def inativar(id_animal):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE animal SET ativo = 0 WHERE id_animal = %s", (id_animal,))
        if cur.rowcount == 0:
            return jsonify({"erro": "animal não encontrado"}), 404
    return jsonify({"mensagem": "inativado"})
