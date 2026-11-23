"""Cadastro e login do veterinário."""
import pymysql
from flask import Blueprint, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth import gerar_token, login_required
from app.db import get_conn
from app.validacoes import campos_faltando, cpf_valido

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/registrar")
def registrar():
    dados = request.get_json(silent=True) or {}
    faltando = campos_faltando(dados, ["nome_completo", "cpf", "crmv", "uf_crmv", "email", "senha"])
    if faltando:
        return jsonify({"erro": f"campos obrigatórios: {', '.join(faltando)}"}), 400
    if not cpf_valido(dados["cpf"]):
        return jsonify({"erro": "CPF inválido"}), 400
    if len(dados["senha"]) < 6:
        return jsonify({"erro": "a senha precisa ter pelo menos 6 caracteres"}), 400

    senha_hash = generate_password_hash(dados["senha"])
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """INSERT INTO veterinario
                   (nome_completo, cpf, crmv, uf_crmv, email, telefone, senha_hash, email_confirmado)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, 1)""",
                # email_confirmado = 1: este projeto não tem um servidor de e-mail de
                # verdade, então simulamos a confirmação automática no cadastro. Num
                # sistema real, aqui enviaríamos um link/código por e-mail antes disso.
                (
                    dados["nome_completo"].strip(),
                    dados["cpf"],
                    dados["crmv"].strip(),
                    dados["uf_crmv"].strip().upper(),
                    dados["email"].strip().lower(),
                    dados.get("telefone"),
                    senha_hash,
                ),
            )
            id_veterinario = cur.lastrowid
    except pymysql.err.IntegrityError:
        return jsonify({"erro": "já existe um veterinário com este CPF, e-mail ou CRMV"}), 409

    return jsonify({"id_veterinario": id_veterinario}), 201


@bp.post("/login")
def login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get("email") or "").strip().lower()
    senha = dados.get("senha") or ""
    if not email or not senha:
        return jsonify({"erro": "informe e-mail e senha"}), 400

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id_veterinario, nome_completo, email, senha_hash FROM veterinario "
            "WHERE email = %s AND ativo = 1",
            (email,),
        )
        veterinario = cur.fetchone()

    if not veterinario or not check_password_hash(veterinario["senha_hash"], senha):
        return jsonify({"erro": "e-mail ou senha incorretos"}), 401

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE veterinario SET ultimo_acesso = NOW() WHERE id_veterinario = %s",
            (veterinario["id_veterinario"],),
        )

    token = gerar_token(veterinario["id_veterinario"], veterinario["nome_completo"])
    return jsonify(
        {
            "token": token,
            "veterinario": {
                "id_veterinario": veterinario["id_veterinario"],
                "nome_completo": veterinario["nome_completo"],
                "email": veterinario["email"],
            },
        }
    )


@bp.get("/me")
@login_required
def me():
    """Confere se o token ainda é válido e devolve quem está logado.
    O frontend usa isto ao carregar cada página protegida."""
    return jsonify(g.veterinario)
