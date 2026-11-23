"""Recebe o cadastro/atualização de um animal vindo da clínica.

Idempotência: cada pedido traz uma "chave_idempotencia". Se a mesma chave
chegar de novo (porque a clínica reenviou depois de uma falha de rede, por
exemplo), devolvemos o MESMO protocolo de antes, sem duplicar nada. Isso é
registrado na tabela operacao_recebida.

Para a demonstração/teste do reenvio, dá para forçar uma falha chamando
POST /animais/?simular_falha=1 (sem isso, o endpoint funciona normalmente)."""
import pymysql
from flask import Blueprint, jsonify, request

from app.db import get_conn
from app.utils import gerar_protocolo

bp = Blueprint("animais", __name__, url_prefix="/animais")


@bp.post("/")
def cadastrar_ou_atualizar():
    dados = request.get_json(silent=True) or {}
    chave = dados.get("chave_idempotencia")
    if not chave:
        return jsonify({"erro": "chave_idempotencia é obrigatória"}), 400
    if not dados.get("id_animal_clinica") or not dados.get("nome"):
        return jsonify({"erro": "id_animal_clinica e nome são obrigatórios"}), 400

    if request.args.get("simular_falha") == "1":
        # Usado só para testar, na marra, o reenvio do lado da clínica.
        return jsonify({"erro": "serviço indisponível (falha simulada)"}), 503

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT protocolo FROM operacao_recebida WHERE chave_idempotencia = %s",
            (chave,),
        )
        existente = cur.fetchone()
        if existente:
            return jsonify({"protocolo": existente["protocolo"], "repetido": True}), 200

        protocolo = gerar_protocolo("AN")
        try:
            cur.execute(
                """INSERT INTO animal_registrado
                   (id_animal_clinica, nome, especie, raca, numero_microchip, protocolo)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                     nome = VALUES(nome), especie = VALUES(especie), raca = VALUES(raca),
                     data_atualizacao = NOW()""",
                (
                    dados["id_animal_clinica"], dados["nome"], dados.get("especie"),
                    dados.get("raca"), dados.get("numero_microchip"), protocolo,
                ),
            )
            cur.execute(
                "INSERT INTO operacao_recebida (chave_idempotencia, protocolo) VALUES (%s, %s)",
                (chave, protocolo),
            )
        except pymysql.err.IntegrityError as erro:
            return jsonify({"erro": f"não foi possível registrar: {erro}"}), 409

    return jsonify({"protocolo": protocolo}), 201


@bp.get("/<int:id_animal_clinica>")
def buscar(id_animal_clinica):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM animal_registrado WHERE id_animal_clinica = %s",
            (id_animal_clinica,),
        )
        linha = cur.fetchone()
    if not linha:
        return jsonify({"erro": "animal não registrado no governo"}), 404
    return jsonify(linha)
