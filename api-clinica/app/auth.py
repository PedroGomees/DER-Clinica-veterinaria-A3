"""Login com token (JWT).

Como funciona, em 3 passos:
1. O veterinário manda e-mail + senha para POST /auth/login.
2. Se a senha confere, geramos um "crachá" digital assinado (o token) com
   gerar_token() e devolvemos para o frontend.
3. Nas próximas chamadas, o frontend manda esse token no cabeçalho
   "Authorization: Bearer <token>". O decorator @login_required confere
   a assinatura do token antes de deixar a rota executar.

O token NÃO fica guardado no banco: ele mesmo carrega os dados (id e nome
do veterinário) de forma assinada. Se alguém alterar um caractere do
token, a assinatura não bate mais e o pedido é rejeitado.
"""
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

VALIDADE_TOKEN = timedelta(hours=8)


def gerar_token(id_veterinario, nome_completo):
    payload = {
        "id_veterinario": id_veterinario,
        "nome_completo": nome_completo,
        "exp": datetime.now(timezone.utc) + VALIDADE_TOKEN,
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def login_required(funcao):
    """Decorator: coloque @login_required em cima de uma rota para exigir
    o token. O veterinário logado fica disponível em g.veterinario."""

    @wraps(funcao)
    def decorada(*args, **kwargs):
        cabecalho = request.headers.get("Authorization", "")
        if not cabecalho.startswith("Bearer "):
            return jsonify({"erro": "faça login: token ausente"}), 401

        token = cabecalho.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "sessão expirada, faça login de novo"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "token inválido"}), 401

        g.veterinario = payload
        return funcao(*args, **kwargs)

    return decorada
