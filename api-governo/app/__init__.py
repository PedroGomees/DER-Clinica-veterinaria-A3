from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    @app.get("/")
    def inicio():
        return jsonify({"mensagem": "API Governamental Simulada no ar"})

    # TODO (Semana 4): criar em routes/ os endpoints de
    #  - cadastro/atualização de animal
    #  - registro de vacina antirrábica
    #  - consulta de protocolo
    # Todos devem respeitar a chave de idempotência (tabela operacao_recebida)
    # e poder simular indisponibilidade para testar o reenvio da clínica.

    return app
