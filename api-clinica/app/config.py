import os

from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "clinica_veterinaria")

    # Assina o token (JWT) do login. Em grupo, usem o mesmo valor no .env
    # de cada um só importa durante o desenvolvimento; não precisa ser secreto
    # de verdade para o trabalho da faculdade, mas evite deixar em branco.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-nao-use-em-producao")

    GOVERNO_URL = os.getenv("GOVERNO_URL", "http://localhost:5001")
