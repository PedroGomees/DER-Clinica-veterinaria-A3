"""Comunicação da clínica com a API governamental simulada.

Cada tentativa de comunicação vira uma linha em integracao_governo (ver
database/clinica/schema.sql), com uma chave de idempotência (um código
único por operação). Se a chamada falhar e formos reenviar depois, usamos
a MESMA chave: assim, se a mensagem tiver chegado ao governo da primeira
vez (só a resposta que se perdeu), ele não duplica o registro, só devolve
o mesmo protocolo de novo.

Este módulo nunca levanta exceção para quem chamou: cadastrar um animal
ou uma vacina aqui na clínica não pode falhar só porque o "governo" está
fora do ar. O status fica registrado para reenvio manual (ou automático,
numa versão futura) pela tela de Integrações.
"""
import uuid

import requests
from flask import current_app

from app.db import get_conn

TIMEOUT_SEGUNDOS = 5


def _criar_integracao(id_animal, id_vacina, tipo_operacao):
    chave = str(uuid.uuid4())
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO integracao_governo (id_animal, id_vacina, tipo_operacao, status, chave_idempotencia)
               VALUES (%s, %s, %s, 'PENDENTE', %s)""",
            (id_animal, id_vacina, tipo_operacao, chave),
        )
        return cur.lastrowid, chave


def _marcar_resultado(id_integracao, status, protocolo=None, erro=None):
    with get_conn() as conn, conn.cursor() as cur:
        if status == "CONFIRMADO":
            cur.execute(
                """UPDATE integracao_governo SET status=%s, protocolo=%s, tentativas = tentativas + 1,
                   ultima_tentativa = NOW(), data_confirmacao = NOW(), mensagem_erro = NULL
                   WHERE id_integracao = %s""",
                (status, protocolo, id_integracao),
            )
        else:
            cur.execute(
                """UPDATE integracao_governo SET status=%s, tentativas = tentativas + 1,
                   ultima_tentativa = NOW(), mensagem_erro = %s WHERE id_integracao = %s""",
                (status, (erro or "")[:500], id_integracao),
            )


def _buscar_animal(id_animal):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT a.id_animal, a.nome, esp.nome AS especie, r.nome AS raca
               FROM animal a
               JOIN especie esp ON esp.id_especie = a.id_especie
               JOIN raca r ON r.id_raca = a.id_raca
               WHERE a.id_animal = %s""",
            (id_animal,),
        )
        return cur.fetchone()


def _buscar_vacina(id_vacina):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT data_aplicacao, lote FROM vacina WHERE id_vacina = %s", (id_vacina,))
        return cur.fetchone()


def _enviar(id_integracao, caminho, payload):
    url = current_app.config["GOVERNO_URL"].rstrip("/") + caminho
    try:
        resposta = requests.post(url, json=payload, timeout=TIMEOUT_SEGUNDOS)
    except requests.RequestException as erro:
        _marcar_resultado(id_integracao, "FALHA", erro=f"não foi possível conectar: {erro}")
        return

    if resposta.status_code in (200, 201):
        protocolo = (resposta.json() or {}).get("protocolo")
        _marcar_resultado(id_integracao, "CONFIRMADO", protocolo=protocolo)
    else:
        _marcar_resultado(id_integracao, "FALHA", erro=f"HTTP {resposta.status_code}: {resposta.text[:300]}")


def enviar_cadastro_animal(id_animal, tipo_operacao="CADASTRO_ANIMAL"):
    """Chamado ao criar ou atualizar um animal na clínica."""
    animal = _buscar_animal(id_animal)
    if not animal:
        return None
    id_integracao, chave = _criar_integracao(id_animal, None, tipo_operacao)
    payload = {
        "chave_idempotencia": chave,
        "id_animal_clinica": animal["id_animal"],
        "nome": animal["nome"],
        "especie": animal["especie"],
        "raca": animal["raca"],
    }
    _enviar(id_integracao, "/animais/", payload)
    return id_integracao


def enviar_vacina_antirrabica(id_vacina, id_animal):
    """Chamado ao registrar uma vacina com antirrabica = 1."""
    vacina = _buscar_vacina(id_vacina)
    if not vacina:
        return None
    id_integracao, chave = _criar_integracao(id_animal, id_vacina, "VACINA_ANTIRRABICA")
    payload = {
        "chave_idempotencia": chave,
        "id_vacina_clinica": id_vacina,
        "id_animal_clinica": id_animal,
        "data_aplicacao": str(vacina["data_aplicacao"]),
        "lote": vacina.get("lote"),
    }
    _enviar(id_integracao, "/vacinas/", payload)
    return id_integracao


def reenviar(id_integracao):
    """Tenta de novo uma integração que ficou com status FALHA, reusando a
    mesma chave de idempotência (por isso o governo não duplica o registro)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM integracao_governo WHERE id_integracao = %s", (id_integracao,))
        linha = cur.fetchone()
    if not linha:
        return False

    if linha["tipo_operacao"] == "VACINA_ANTIRRABICA":
        vacina = _buscar_vacina(linha["id_vacina"])
        if not vacina:
            return False
        payload = {
            "chave_idempotencia": linha["chave_idempotencia"],
            "id_vacina_clinica": linha["id_vacina"],
            "id_animal_clinica": linha["id_animal"],
            "data_aplicacao": str(vacina["data_aplicacao"]),
            "lote": vacina.get("lote"),
        }
        caminho = "/vacinas/"
    else:
        animal = _buscar_animal(linha["id_animal"])
        if not animal:
            return False
        payload = {
            "chave_idempotencia": linha["chave_idempotencia"],
            "id_animal_clinica": animal["id_animal"],
            "nome": animal["nome"],
            "especie": animal["especie"],
            "raca": animal["raca"],
        }
        caminho = "/animais/"

    _enviar(linha["id_integracao"], caminho, payload)
    return True
