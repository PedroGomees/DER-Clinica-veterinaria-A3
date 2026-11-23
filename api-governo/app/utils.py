import random
import string
from datetime import datetime


def gerar_protocolo(prefixo):
    """Gera um número de protocolo "de verdade", tipo AN-20261123153000-X7K9."""
    agora = datetime.now().strftime("%Y%m%d%H%M%S")
    sufixo = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefixo}-{agora}-{sufixo}"
