from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .routes import animais, vacinas


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(animais.bp)
    app.register_blueprint(vacinas.bp)

    @app.get("/")
    def inicio():
        return jsonify({"mensagem": "API Governamental Simulada no ar"})

    @app.errorhandler(404)
    def nao_encontrado(_e):
        return jsonify({"erro": "rota não encontrada"}), 404

    @app.errorhandler(500)
    def erro_interno(_e):
        return jsonify({"erro": "erro interno no servidor"}), 500

    return app
