from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .routes import especies


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)  # permite o frontend (outra porta) chamar a API

    # Cada módulo de rotas é um "blueprint". Para adicionar um novo
    # (tutores, animais...), crie o arquivo em routes/ e registre aqui.
    app.register_blueprint(especies.bp)

    @app.get("/")
    def inicio():
        return jsonify({"mensagem": "API da Clínica no ar"})

    return app
