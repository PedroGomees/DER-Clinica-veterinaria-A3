"""Recebe o registro de uma vacina antirrábica vinda da clínica. O animal
precisa já estar cadastrado aqui (ver routes/animais.py) antes de registrar
a vacina dele - é assim que o "governo" saberia de quem é a vacina."""
import pymysql
from flask import Blueprint, jsonify, request

from app.db import get_conn
from app.utils import gerar_protocolo

bp = Blueprint("vacinas", __name__, url_prefix="/vacinas")


@bp.post("/")
def registrar():
    dados = request.get_json(silent=True) or {}
    chave = dados.get("chave_idempotencia")
    if not chave:
        return jsonify({"erro": "chave_idempotencia é obrigatória"}), 400
    if not dados.get("id_animal_clinica") or not dados.get("id_vacina_clinica"):
        return jsonify({"erro": "id_animal_clinica e id_vacina_clinica são obrigatórios"}), 400

    if request.args.get("simular_falha") == "1":
        return jsonify({"erro": "serviço indisponível (falha simulada)"}), 503

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT protocolo FROM operacao_recebida WHERE chave_idempotencia = %s",
            (chave,),
        )
        existente = cur.fetchone()
        if existente:
            return jsonify({"protocolo": existente["protocolo"], "repetido": True}), 200

        cur.execute(
            "SELECT id_registro FROM animal_registrado WHERE id_animal_clinica = %s",
            (dados["id_animal_clinica"],),
        )
        animal = cur.fetchone()
        if not animal:
            return jsonify({"erro": "animal ainda não está cadastrado no governo"}), 422

        protocolo = gerar_protocolo("VC")
        try:
            cur.execute(
                """INSERT INTO vacina_antirrabica_registrada
                   (id_registro, id_vacina_clinica, data_aplicacao, lote, protocolo)
                   VALUES (%s, %s, %s, %s, %s)""",
                (animal["id_registro"], dados["id_vacina_clinica"], dados.get("data_aplicacao"),
                 dados.get("lote"), protocolo),
            )
            cur.execute(
                "INSERT INTO operacao_recebida (chave_idempotencia, protocolo) VALUES (%s, %s)",
                (chave, protocolo),
            )
        except pymysql.err.IntegrityError as erro:
            return jsonify({"erro": f"não foi possível registrar: {erro}"}), 409

    return jsonify({"protocolo": protocolo}), 201
