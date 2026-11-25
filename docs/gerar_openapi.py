"""Gera os arquivos openapi.json de api-clinica/ e api-governo/.

Por que um script, em vez de escrever o JSON na mão? Porque a lista de
endpoints muda conforme o projeto cresce. Se o grupo criar uma rota nova,
basta adicionar ela na lista `ROTAS` correspondente e rodar:

    python docs/gerar_openapi.py

Isso evita o JSON do Swagger ficar desatualizado em relação ao código.
"""
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ERRO = {
    "type": "object",
    "properties": {"erro": {"type": "string"}},
}


def resposta_erro(descricao):
    return {"description": descricao, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Erro"}}}}


def resposta_json(descricao, schema):
    return {"description": descricao, "content": {"application/json": {"schema": schema}}}


def ref(nome):
    return {"$ref": f"#/components/schemas/{nome}"}


def lista(nome):
    return {"type": "array", "items": ref(nome)}


SEGURANCA = [{"bearerAuth": []}]


# ============================================================
# api-clinica
# ============================================================

SCHEMAS_CLINICA = {
    "Erro": ERRO,
    "RegistrarVeterinario": {
        "type": "object",
        "required": ["nome_completo", "cpf", "crmv", "uf_crmv", "email", "senha"],
        "properties": {
            "nome_completo": {"type": "string"},
            "cpf": {"type": "string", "example": "111.444.777-35"},
            "crmv": {"type": "string"},
            "uf_crmv": {"type": "string", "example": "SP"},
            "email": {"type": "string", "format": "email"},
            "telefone": {"type": "string"},
            "senha": {"type": "string", "format": "password", "minLength": 6},
        },
    },
    "Login": {
        "type": "object",
        "required": ["email", "senha"],
        "properties": {"email": {"type": "string", "format": "email"}, "senha": {"type": "string", "format": "password"}},
    },
    "LoginResposta": {
        "type": "object",
        "properties": {
            "token": {"type": "string", "description": "JWT; mande em 'Authorization: Bearer <token>'"},
            "veterinario": {
                "type": "object",
                "properties": {
                    "id_veterinario": {"type": "integer"},
                    "nome_completo": {"type": "string"},
                    "email": {"type": "string"},
                },
            },
        },
    },
    "Especie": {
        "type": "object",
        "properties": {
            "id_especie": {"type": "integer"},
            "nome": {"type": "string"},
            "descricao": {"type": "string", "nullable": True},
            "ativo": {"type": "integer", "enum": [0, 1]},
        },
    },
    "EspecieEntrada": {
        "type": "object",
        "required": ["nome"],
        "properties": {"nome": {"type": "string"}, "descricao": {"type": "string", "nullable": True}},
    },
    "Raca": {
        "type": "object",
        "properties": {
            "id_raca": {"type": "integer"},
            "nome": {"type": "string"},
            "id_especie": {"type": "integer"},
            "descricao": {"type": "string", "nullable": True},
            "ativo": {"type": "integer", "enum": [0, 1]},
        },
    },
    "RacaEntrada": {
        "type": "object",
        "required": ["nome", "id_especie"],
        "properties": {
            "nome": {"type": "string"},
            "id_especie": {"type": "integer"},
            "descricao": {"type": "string", "nullable": True},
        },
    },
    "Endereco": {
        "type": "object",
        "properties": {
            "id_endereco": {"type": "integer"},
            "cep": {"type": "string", "example": "01001000"},
            "logradouro": {"type": "string"},
            "numero": {"type": "string"},
            "complemento": {"type": "string", "nullable": True},
            "bairro": {"type": "string"},
            "cidade": {"type": "string"},
            "uf": {"type": "string"},
        },
    },
    "EnderecoEntrada": {
        "type": "object",
        "required": ["cep", "logradouro", "numero", "bairro", "cidade", "uf"],
        "properties": {
            "cep": {"type": "string"},
            "logradouro": {"type": "string"},
            "numero": {"type": "string"},
            "complemento": {"type": "string", "nullable": True},
            "bairro": {"type": "string"},
            "cidade": {"type": "string"},
            "uf": {"type": "string"},
        },
    },
    "Tutor": {
        "type": "object",
        "properties": {
            "id_tutor": {"type": "integer"},
            "nome_completo": {"type": "string"},
            "cpf": {"type": "string"},
            "dt_nasc": {"type": "string", "format": "date", "nullable": True},
            "email": {"type": "string", "nullable": True},
            "telefone": {"type": "string", "nullable": True},
            "data_cadastro": {"type": "string"},
            "ativo": {"type": "integer", "enum": [0, 1]},
            "id_endereco": {"type": "integer"},
            "cep": {"type": "string"},
            "logradouro": {"type": "string"},
            "numero": {"type": "string"},
            "complemento": {"type": "string", "nullable": True},
            "bairro": {"type": "string"},
            "cidade": {"type": "string"},
            "uf": {"type": "string"},
        },
    },
    "TutorEntrada": {
        "type": "object",
        "required": ["nome_completo", "cpf", "endereco"],
        "properties": {
            "nome_completo": {"type": "string"},
            "cpf": {"type": "string"},
            "dt_nasc": {"type": "string", "format": "date", "nullable": True},
            "email": {"type": "string", "nullable": True},
            "telefone": {"type": "string", "nullable": True},
            "endereco": ref("EnderecoEntrada"),
        },
    },
    "Animal": {
        "type": "object",
        "properties": {
            "id_animal": {"type": "integer"},
            "nome": {"type": "string"},
            "id_especie": {"type": "integer"},
            "nome_especie": {"type": "string"},
            "id_raca": {"type": "integer"},
            "nome_raca": {"type": "string"},
            "sexo": {"type": "string", "enum": ["M", "F"]},
            "dt_nasc": {"type": "string", "format": "date", "nullable": True},
            "porte": {"type": "string", "enum": ["PEQUENO", "MEDIO", "GRANDE"], "nullable": True},
            "id_tutor": {"type": "integer"},
            "nome_tutor": {"type": "string"},
            "observacao": {"type": "string", "nullable": True},
            "ativo": {"type": "integer", "enum": [0, 1]},
        },
    },
    "AnimalEntrada": {
        "type": "object",
        "required": ["nome", "id_especie", "id_raca", "sexo", "id_tutor"],
        "properties": {
            "nome": {"type": "string"},
            "id_especie": {"type": "integer"},
            "id_raca": {"type": "integer", "description": "precisa pertencer à id_especie informada"},
            "sexo": {"type": "string", "enum": ["M", "F"]},
            "dt_nasc": {"type": "string", "format": "date", "nullable": True},
            "porte": {"type": "string", "enum": ["PEQUENO", "MEDIO", "GRANDE"], "nullable": True},
            "id_tutor": {"type": "integer"},
            "observacao": {"type": "string", "nullable": True},
        },
    },
    "Veterinario": {
        "type": "object",
        "properties": {
            "id_veterinario": {"type": "integer"},
            "nome_completo": {"type": "string"},
            "crmv": {"type": "string"},
            "uf_crmv": {"type": "string"},
        },
    },
    "Consulta": {
        "type": "object",
        "properties": {
            "id_consulta": {"type": "integer"},
            "id_animal": {"type": "integer"},
            "nome_animal": {"type": "string"},
            "id_veterinario": {"type": "integer"},
            "nome_veterinario": {"type": "string"},
            "data_hora": {"type": "string", "example": "2026-11-24 14:30:00"},
            "motivo": {"type": "string"},
            "historico": {"type": "string", "nullable": True},
            "sintomas": {"type": "string", "nullable": True},
            "diagnostico": {"type": "string", "nullable": True},
            "tratamento": {"type": "string", "nullable": True},
            "status": {"type": "string", "enum": ["AGENDADA", "EM_ATENDIMENTO", "CONCLUIDA", "CANCELADA"]},
        },
    },
    "ConsultaEntrada": {
        "type": "object",
        "required": ["id_animal", "data_hora", "motivo"],
        "properties": {
            "id_animal": {"type": "integer"},
            "data_hora": {"type": "string", "example": "2026-11-24 14:30:00"},
            "motivo": {"type": "string"},
            "historico": {"type": "string", "nullable": True},
            "sintomas": {"type": "string", "nullable": True},
            "diagnostico": {"type": "string", "nullable": True},
            "tratamento": {"type": "string", "nullable": True},
            "status": {"type": "string", "enum": ["AGENDADA", "EM_ATENDIMENTO", "CONCLUIDA", "CANCELADA"]},
        },
    },
    "Vacina": {
        "type": "object",
        "properties": {
            "id_vacina": {"type": "integer"},
            "id_animal": {"type": "integer"},
            "nome_animal": {"type": "string"},
            "id_veterinario": {"type": "integer"},
            "nome_veterinario": {"type": "string"},
            "nome_vacina": {"type": "string"},
            "antirrabica": {"type": "integer", "enum": [0, 1], "description": "1 = comunicada à API governamental"},
            "fabricante": {"type": "string", "nullable": True},
            "lote": {"type": "string", "nullable": True},
            "data_aplicacao": {"type": "string", "format": "date"},
            "dose": {"type": "string", "nullable": True},
            "via_administracao": {"type": "string", "nullable": True},
            "proxima_dose": {"type": "string", "format": "date", "nullable": True},
            "observacao": {"type": "string", "nullable": True},
        },
    },
    "VacinaEntrada": {
        "type": "object",
        "required": ["id_animal", "nome_vacina", "data_aplicacao"],
        "properties": {
            "id_animal": {"type": "integer"},
            "nome_vacina": {"type": "string"},
            "data_aplicacao": {"type": "string", "format": "date"},
            "antirrabica": {"type": "boolean"},
            "fabricante": {"type": "string", "nullable": True},
            "lote": {"type": "string", "nullable": True},
            "dose": {"type": "string", "nullable": True},
            "via_administracao": {"type": "string", "nullable": True},
            "proxima_dose": {"type": "string", "format": "date", "nullable": True},
            "observacao": {"type": "string", "nullable": True},
        },
    },
    "Microchip": {
        "type": "object",
        "properties": {
            "id_vinculo": {"type": "integer"},
            "id_animal": {"type": "integer"},
            "nome_animal": {"type": "string"},
            "id_veterinario": {"type": "integer"},
            "nome_veterinario": {"type": "string"},
            "numero_microchip": {"type": "string"},
            "data_vinculacao": {"type": "string"},
            "data_desvinculacao": {"type": "string", "nullable": True},
            "ativo": {"type": "integer", "enum": [0, 1]},
            "observacao": {"type": "string", "nullable": True},
        },
    },
    "MicrochipEntrada": {
        "type": "object",
        "required": ["id_animal", "numero_microchip"],
        "properties": {
            "id_animal": {"type": "integer"},
            "numero_microchip": {"type": "string", "example": "981000000123456"},
            "observacao": {"type": "string", "nullable": True},
        },
    },
    "Cep": {
        "type": "object",
        "properties": {
            "cep": {"type": "string"},
            "logradouro": {"type": "string"},
            "bairro": {"type": "string"},
            "cidade": {"type": "string"},
            "uf": {"type": "string"},
        },
    },
    "Integracao": {
        "type": "object",
        "properties": {
            "id_integracao": {"type": "integer"},
            "id_animal": {"type": "integer"},
            "nome_animal": {"type": "string"},
            "id_vacina": {"type": "integer", "nullable": True},
            "tipo_operacao": {"type": "string", "enum": ["CADASTRO_ANIMAL", "ATUALIZACAO_ANIMAL", "VACINA_ANTIRRABICA"]},
            "status": {"type": "string", "enum": ["PENDENTE", "ENVIADO", "CONFIRMADO", "FALHA"]},
            "protocolo": {"type": "string", "nullable": True},
            "tentativas": {"type": "integer"},
            "data_criacao": {"type": "string"},
            "ultima_tentativa": {"type": "string", "nullable": True},
            "data_confirmacao": {"type": "string", "nullable": True},
            "mensagem_erro": {"type": "string", "nullable": True},
        },
    },
}

TAGS_CLINICA = [
    {"name": "Autenticação", "description": "Cadastro e login do veterinário; o token (JWT) gerado aqui é exigido pelas demais rotas."},
    {"name": "Espécies", "description": "Cadastro de apoio, usado no formulário de animal."},
    {"name": "Raças", "description": "Cadastro de apoio; toda raça pertence a uma espécie."},
    {"name": "Endereços", "description": "CRUD de endereço (normalmente criado/editado junto com o tutor)."},
    {"name": "Tutores", "description": "Tutores dos animais, com endereço."},
    {"name": "Animais", "description": "Animais atendidos pela clínica."},
    {"name": "Veterinários", "description": "Lista de veterinários cadastrados (somente leitura)."},
    {"name": "Consultas", "description": "Histórico clínico de consultas."},
    {"name": "Vacinas", "description": "Vacinas aplicadas; a antirrábica é comunicada ao governo."},
    {"name": "Microchip", "description": "Vínculo de microchip, com histórico."},
    {"name": "CEP", "description": "Consulta de endereço via ViaCEP."},
    {"name": "Integração governo", "description": "Acompanhamento e reenvio da comunicação com a API governamental simulada."},
]

PATHS_CLINICA = {
    "/": {
        "get": {
            "tags": ["Autenticação"],
            "summary": "Verifica se a API está no ar",
            "responses": {"200": resposta_json("API no ar", {"type": "object", "properties": {"mensagem": {"type": "string"}}})},
        }
    },
    "/auth/registrar": {
        "post": {
            "tags": ["Autenticação"],
            "summary": "Cadastra um novo veterinário",
            "requestBody": {"required": True, "content": {"application/json": {"schema": ref("RegistrarVeterinario")}}},
            "responses": {
                "201": resposta_json("Cadastrado", {"type": "object", "properties": {"id_veterinario": {"type": "integer"}}}),
                "400": resposta_erro("Campo obrigatório faltando, ou CPF/senha inválidos"),
                "409": resposta_erro("CPF, e-mail ou CRMV já cadastrado"),
            },
        }
    },
    "/auth/login": {
        "post": {
            "tags": ["Autenticação"],
            "summary": "Login; devolve o token usado nas demais rotas",
            "requestBody": {"required": True, "content": {"application/json": {"schema": ref("Login")}}},
            "responses": {
                "200": resposta_json("Login OK", ref("LoginResposta")),
                "400": resposta_erro("E-mail ou senha não informados"),
                "401": resposta_erro("E-mail ou senha incorretos"),
            },
        }
    },
    "/auth/me": {
        "get": {
            "tags": ["Autenticação"],
            "summary": "Confere se o token ainda é válido",
            "security": SEGURANCA,
            "responses": {
                "200": resposta_json("Token válido", {"type": "object", "properties": {"id_veterinario": {"type": "integer"}, "nome_completo": {"type": "string"}, "exp": {"type": "integer"}}}),
                "401": resposta_erro("Token ausente, inválido ou expirado"),
            },
        }
    },
}


def crud_simples(prefixo, tag, nome_schema, nome_entrada, id_param, id_tipo="integer", filtros=None, exemplo_id=1):
    """Monta o GET lista / GET um / POST / PUT / DELETE de um cadastro simples
    (espécie, raça, endereço), no padrão repetido em várias rotas."""
    filtros = filtros or []
    caminho_base = f"/{prefixo}/"
    caminho_item = f"/{prefixo}/{{{id_param}}}"
    parametros_lista = [
        {"name": f["nome"], "in": "query", "required": False, "schema": {"type": f.get("tipo", "string")}, "description": f["descricao"]}
        for f in filtros
    ]
    paths = {}
    ops = {}
    if "listar" not in (nome_entrada,):
        pass
    ops["get"] = {
        "tags": [tag],
        "summary": f"Lista {tag.lower()}",
        "parameters": parametros_lista,
        "responses": {"200": resposta_json("Lista", lista(nome_schema))},
    }
    ops["post"] = {
        "tags": [tag],
        "summary": f"Cria {tag.lower()[:-1] if tag.endswith('s') else tag.lower()}",
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref(nome_entrada)}}},
        "responses": {
            "201": resposta_json("Criado", {"type": "object", "properties": {id_param: {"type": id_tipo}}}),
            "400": resposta_erro("Campo obrigatório faltando"),
            "409": resposta_erro("Conflito (ex.: duplicado)"),
        },
    }
    paths[caminho_base] = ops

    item_ops = {
        "get": {
            "tags": [tag],
            "summary": "Busca um registro pelo id",
            "parameters": [{"name": id_param, "in": "path", "required": True, "schema": {"type": id_tipo, "example": exemplo_id}}],
            "responses": {"200": resposta_json("Encontrado", ref(nome_schema)), "404": resposta_erro("Não encontrado")},
        },
        "put": {
            "tags": [tag],
            "summary": "Atualiza um registro",
            "parameters": [{"name": id_param, "in": "path", "required": True, "schema": {"type": id_tipo, "example": exemplo_id}}],
            "requestBody": {"required": True, "content": {"application/json": {"schema": ref(nome_entrada)}}},
            "responses": {
                "200": resposta_json("Atualizado", {"type": "object", "properties": {"mensagem": {"type": "string"}}}),
                "400": resposta_erro("Campo obrigatório faltando"),
                "404": resposta_erro("Não encontrado"),
            },
        },
        "delete": {
            "tags": [tag],
            "summary": "Inativa um registro (ativo = 0; não apaga)",
            "parameters": [{"name": id_param, "in": "path", "required": True, "schema": {"type": id_tipo, "example": exemplo_id}}],
            "responses": {
                "200": resposta_json("Inativado", {"type": "object", "properties": {"mensagem": {"type": "string"}}}),
                "404": resposta_erro("Não encontrado"),
            },
        },
    }
    paths[caminho_item] = item_ops
    return paths


PATHS_CLINICA.update(
    crud_simples(
        "especies", "Espécies", "Especie", "EspecieEntrada", "id_especie",
        filtros=[{"nome": "todas", "descricao": "1 = inclui inativas", "tipo": "integer"}],
    )
)

# raças: sem DELETE endpoint diferente, mas tem o filtro id_especie e PUT sem exigir id_especie no corpo
PATHS_CLINICA["/racas/"] = {
    "get": {
        "tags": ["Raças"], "summary": "Lista raças",
        "parameters": [
            {"name": "id_especie", "in": "query", "schema": {"type": "integer"}, "description": "filtra as raças de uma espécie"},
            {"name": "todas", "in": "query", "schema": {"type": "integer"}, "description": "1 = inclui inativas"},
        ],
        "responses": {"200": resposta_json("Lista", lista("Raca"))},
    },
    "post": {
        "tags": ["Raças"], "summary": "Cria raça",
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("RacaEntrada")}}},
        "responses": {
            "201": resposta_json("Criada", {"type": "object", "properties": {"id_raca": {"type": "integer"}}}),
            "400": resposta_erro("nome e id_especie são obrigatórios, ou espécie não existe"),
            "409": resposta_erro("já existe uma raça com este nome para esta espécie"),
        },
    },
}
PATHS_CLINICA["/racas/{id_raca}"] = {
    "get": {
        "tags": ["Raças"], "summary": "Busca uma raça",
        "parameters": [{"name": "id_raca", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Encontrada", ref("Raca")), "404": resposta_erro("Não encontrada")},
    },
    "put": {
        "tags": ["Raças"], "summary": "Atualiza uma raça",
        "parameters": [{"name": "id_raca", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "required": ["nome"], "properties": {"nome": {"type": "string"}, "descricao": {"type": "string", "nullable": True}}}}}},
        "responses": {"200": resposta_json("Atualizada", {"type": "object", "properties": {"mensagem": {"type": "string"}}}), "400": resposta_erro("nome é obrigatório"), "404": resposta_erro("Não encontrada")},
    },
    "delete": {
        "tags": ["Raças"], "summary": "Inativa uma raça",
        "parameters": [{"name": "id_raca", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Inativada", {"type": "object", "properties": {"mensagem": {"type": "string"}}}), "404": resposta_erro("Não encontrada")},
    },
}

# endereços: só tem POST e GET/PUT por id (sem lista, sem DELETE)
PATHS_CLINICA["/enderecos/"] = {
    "post": {
        "tags": ["Endereços"], "summary": "Cria um endereço",
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("EnderecoEntrada")}}},
        "responses": {"201": resposta_json("Criado", {"type": "object", "properties": {"id_endereco": {"type": "integer"}}}), "400": resposta_erro("Campo obrigatório faltando")},
    }
}
PATHS_CLINICA["/enderecos/{id_endereco}"] = {
    "get": {
        "tags": ["Endereços"], "summary": "Busca um endereço",
        "parameters": [{"name": "id_endereco", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Encontrado", ref("Endereco")), "404": resposta_erro("Não encontrado")},
    },
    "put": {
        "tags": ["Endereços"], "summary": "Atualiza um endereço",
        "parameters": [{"name": "id_endereco", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("EnderecoEntrada")}}},
        "responses": {"200": resposta_json("Atualizado", {"type": "object", "properties": {"mensagem": {"type": "string"}}}), "400": resposta_erro("Campo obrigatório faltando"), "404": resposta_erro("Não encontrado")},
    },
}

# tutores (autenticado)
PATHS_CLINICA["/tutores/"] = {
    "get": {
        "tags": ["Tutores"], "summary": "Lista tutores", "security": SEGURANCA,
        "parameters": [
            {"name": "q", "in": "query", "schema": {"type": "string"}, "description": "busca por nome ou CPF"},
            {"name": "todos", "in": "query", "schema": {"type": "integer"}, "description": "1 = inclui inativos"},
        ],
        "responses": {"200": resposta_json("Lista", lista("Tutor")), "401": resposta_erro("Sem token")},
    },
    "post": {
        "tags": ["Tutores"], "summary": "Cria um tutor (e o endereço dele, numa transação)", "security": SEGURANCA,
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("TutorEntrada")}}},
        "responses": {
            "201": resposta_json("Criado", {"type": "object", "properties": {"id_tutor": {"type": "integer"}}}),
            "400": resposta_erro("Campo obrigatório faltando, ou CPF inválido"),
            "401": resposta_erro("Sem token"),
            "409": resposta_erro("Já existe um tutor com este CPF"),
        },
    },
}
PATHS_CLINICA["/tutores/{id_tutor}"] = {
    "get": {
        "tags": ["Tutores"], "summary": "Busca um tutor", "security": SEGURANCA,
        "parameters": [{"name": "id_tutor", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Encontrado", ref("Tutor")), "401": resposta_erro("Sem token"), "404": resposta_erro("Não encontrado")},
    },
    "put": {
        "tags": ["Tutores"], "summary": "Atualiza um tutor e o endereço dele", "security": SEGURANCA,
        "parameters": [{"name": "id_tutor", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("TutorEntrada")}}},
        "responses": {
            "200": resposta_json("Atualizado", {"type": "object", "properties": {"mensagem": {"type": "string"}}}),
            "400": resposta_erro("Campo obrigatório faltando, ou CPF inválido"),
            "401": resposta_erro("Sem token"),
            "404": resposta_erro("Não encontrado"),
            "409": resposta_erro("Já existe um tutor com este CPF"),
        },
    },
    "delete": {
        "tags": ["Tutores"], "summary": "Inativa um tutor (preserva os animais dele)", "security": SEGURANCA,
        "parameters": [{"name": "id_tutor", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Inativado", {"type": "object", "properties": {"mensagem": {"type": "string"}}}), "401": resposta_erro("Sem token"), "404": resposta_erro("Não encontrado")},
    },
}

# animais
PATHS_CLINICA["/animais/"] = {
    "get": {
        "tags": ["Animais"], "summary": "Lista animais", "security": SEGURANCA,
        "parameters": [
            {"name": "id_tutor", "in": "query", "schema": {"type": "integer"}, "description": "filtra pelos animais de um tutor"},
            {"name": "q", "in": "query", "schema": {"type": "string"}, "description": "busca pelo nome do animal"},
            {"name": "todos", "in": "query", "schema": {"type": "integer"}, "description": "1 = inclui inativos"},
        ],
        "responses": {"200": resposta_json("Lista", lista("Animal")), "401": resposta_erro("Sem token")},
    },
    "post": {
        "tags": ["Animais"],
        "summary": "Cria um animal (e avisa a API governamental em segundo plano)",
        "security": SEGURANCA,
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("AnimalEntrada")}}},
        "responses": {
            "201": resposta_json("Criado", {"type": "object", "properties": {"id_animal": {"type": "integer"}}}),
            "400": resposta_erro("Campo obrigatório faltando, tutor/espécie/raça inválidos, ou a raça não pertence à espécie"),
            "401": resposta_erro("Sem token"),
        },
    },
}
PATHS_CLINICA["/animais/{id_animal}"] = {
    "get": {
        "tags": ["Animais"], "summary": "Busca um animal", "security": SEGURANCA,
        "parameters": [{"name": "id_animal", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Encontrado", ref("Animal")), "401": resposta_erro("Sem token"), "404": resposta_erro("Não encontrado")},
    },
    "put": {
        "tags": ["Animais"], "summary": "Atualiza um animal (e avisa a API governamental)", "security": SEGURANCA,
        "parameters": [{"name": "id_animal", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("AnimalEntrada")}}},
        "responses": {
            "200": resposta_json("Atualizado", {"type": "object", "properties": {"mensagem": {"type": "string"}}}),
            "400": resposta_erro("Campo obrigatório faltando, ou dados inválidos"),
            "401": resposta_erro("Sem token"),
            "404": resposta_erro("Não encontrado"),
        },
    },
    "delete": {
        "tags": ["Animais"], "summary": "Inativa um animal (preserva o histórico clínico)", "security": SEGURANCA,
        "parameters": [{"name": "id_animal", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Inativado", {"type": "object", "properties": {"mensagem": {"type": "string"}}}), "401": resposta_erro("Sem token"), "404": resposta_erro("Não encontrado")},
    },
}

# veterinarios (só leitura)
PATHS_CLINICA["/veterinarios/"] = {
    "get": {
        "tags": ["Veterinários"], "summary": "Lista veterinários ativos", "security": SEGURANCA,
        "responses": {"200": resposta_json("Lista", lista("Veterinario")), "401": resposta_erro("Sem token")},
    }
}

# consultas
PATHS_CLINICA["/consultas/"] = {
    "get": {
        "tags": ["Consultas"], "summary": "Lista consultas", "security": SEGURANCA,
        "parameters": [
            {"name": "id_animal", "in": "query", "schema": {"type": "integer"}},
            {"name": "status", "in": "query", "schema": {"type": "string", "enum": ["AGENDADA", "EM_ATENDIMENTO", "CONCLUIDA", "CANCELADA"]}},
        ],
        "responses": {"200": resposta_json("Lista", lista("Consulta")), "401": resposta_erro("Sem token")},
    },
    "post": {
        "tags": ["Consultas"], "summary": "Registra uma consulta (o veterinário é o do token)", "security": SEGURANCA,
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("ConsultaEntrada")}}},
        "responses": {
            "201": resposta_json("Criada", {"type": "object", "properties": {"id_consulta": {"type": "integer"}}}),
            "400": resposta_erro("Campo obrigatório faltando"),
            "401": resposta_erro("Sem token"),
        },
    },
}
PATHS_CLINICA["/consultas/{id_consulta}"] = {
    "get": {
        "tags": ["Consultas"], "summary": "Busca uma consulta", "security": SEGURANCA,
        "parameters": [{"name": "id_consulta", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Encontrada", ref("Consulta")), "401": resposta_erro("Sem token"), "404": resposta_erro("Não encontrada")},
    },
    "put": {
        "tags": ["Consultas"], "summary": "Atualiza uma consulta", "security": SEGURANCA,
        "parameters": [{"name": "id_consulta", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("ConsultaEntrada")}}},
        "responses": {
            "200": resposta_json("Atualizada", {"type": "object", "properties": {"mensagem": {"type": "string"}}}),
            "400": resposta_erro("Campo obrigatório faltando, ou status inválido"),
            "401": resposta_erro("Sem token"),
            "404": resposta_erro("Não encontrada"),
        },
    },
    "delete": {
        "tags": ["Consultas"], "summary": "Cancela uma consulta (status = CANCELADA; não apaga)", "security": SEGURANCA,
        "parameters": [{"name": "id_consulta", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Cancelada", {"type": "object", "properties": {"mensagem": {"type": "string"}}}), "401": resposta_erro("Sem token"), "404": resposta_erro("Não encontrada")},
    },
}

# vacinas
PATHS_CLINICA["/vacinas/"] = {
    "get": {
        "tags": ["Vacinas"], "summary": "Lista vacinas", "security": SEGURANCA,
        "parameters": [{"name": "id_animal", "in": "query", "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Lista", lista("Vacina")), "401": resposta_erro("Sem token")},
    },
    "post": {
        "tags": ["Vacinas"],
        "summary": "Registra uma vacina aplicada (se antirrabica=true, comunica o governo)",
        "security": SEGURANCA,
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("VacinaEntrada")}}},
        "responses": {
            "201": resposta_json("Criada", {"type": "object", "properties": {"id_vacina": {"type": "integer"}}}),
            "400": resposta_erro("Campo obrigatório faltando"),
            "401": resposta_erro("Sem token"),
        },
    },
}
PATHS_CLINICA["/vacinas/{id_vacina}"] = {
    "get": {
        "tags": ["Vacinas"], "summary": "Busca uma vacina", "security": SEGURANCA,
        "parameters": [{"name": "id_vacina", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Encontrada", ref("Vacina")), "401": resposta_erro("Sem token"), "404": resposta_erro("Não encontrada")},
    },
    "put": {
        "tags": ["Vacinas"], "summary": "Atualiza uma vacina", "security": SEGURANCA,
        "parameters": [{"name": "id_vacina", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("VacinaEntrada")}}},
        "responses": {
            "200": resposta_json("Atualizada", {"type": "object", "properties": {"mensagem": {"type": "string"}}}),
            "400": resposta_erro("Campo obrigatório faltando"),
            "401": resposta_erro("Sem token"),
            "404": resposta_erro("Não encontrada"),
        },
    },
}

# microchips
PATHS_CLINICA["/microchips/"] = {
    "get": {
        "tags": ["Microchip"], "summary": "Histórico de vínculos de microchip", "security": SEGURANCA,
        "parameters": [{"name": "id_animal", "in": "query", "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Lista", lista("Microchip")), "401": resposta_erro("Sem token")},
    },
    "post": {
        "tags": ["Microchip"], "summary": "Vincula um microchip a um animal", "security": SEGURANCA,
        "requestBody": {"required": True, "content": {"application/json": {"schema": ref("MicrochipEntrada")}}},
        "responses": {
            "201": resposta_json("Vinculado", {"type": "object", "properties": {"id_vinculo": {"type": "integer"}}}),
            "400": resposta_erro("Campo obrigatório faltando"),
            "401": resposta_erro("Sem token"),
            "409": resposta_erro("Animal já tem microchip ativo, ou o número já está em uso em outro animal"),
        },
    },
}
PATHS_CLINICA["/microchips/{id_vinculo}/desvincular"] = {
    "post": {
        "tags": ["Microchip"], "summary": "Desvincula um microchip (preserva o histórico)", "security": SEGURANCA,
        "parameters": [{"name": "id_vinculo", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {
            "200": resposta_json("Desvinculado", {"type": "object", "properties": {"mensagem": {"type": "string"}}}),
            "401": resposta_erro("Sem token"),
            "404": resposta_erro("Vínculo não encontrado ou já estava inativo"),
        },
    }
}

# cep
PATHS_CLINICA["/cep/{cep}"] = {
    "get": {
        "tags": ["CEP"], "summary": "Consulta um endereço pelo CEP (via ViaCEP)",
        "parameters": [{"name": "cep", "in": "path", "required": True, "schema": {"type": "string"}, "example": "01001000"}],
        "responses": {
            "200": resposta_json("Encontrado", ref("Cep")),
            "400": resposta_erro("CEP deve ter 8 dígitos"),
            "404": resposta_erro("CEP não encontrado"),
            "502": resposta_erro("Não foi possível consultar o ViaCEP agora"),
        },
    }
}

# integracoes
PATHS_CLINICA["/integracoes/"] = {
    "get": {
        "tags": ["Integração governo"], "summary": "Lista o status das comunicações com o governo", "security": SEGURANCA,
        "parameters": [
            {"name": "status", "in": "query", "schema": {"type": "string", "enum": ["PENDENTE", "ENVIADO", "CONFIRMADO", "FALHA"]}},
            {"name": "id_animal", "in": "query", "schema": {"type": "integer"}},
        ],
        "responses": {"200": resposta_json("Lista", lista("Integracao")), "401": resposta_erro("Sem token")},
    }
}
PATHS_CLINICA["/integracoes/{id_integracao}/reenviar"] = {
    "post": {
        "tags": ["Integração governo"],
        "summary": "Reenvia uma integração (reusa a mesma chave de idempotência)",
        "security": SEGURANCA,
        "parameters": [{"name": "id_integracao", "in": "path", "required": True, "schema": {"type": "integer"}}],
        "responses": {"200": resposta_json("Resultado do reenvio", ref("Integracao")), "401": resposta_erro("Sem token"), "404": resposta_erro("Integração não encontrada")},
    }
}

OPENAPI_CLINICA = {
    "openapi": "3.0.3",
    "info": {
        "title": "API da Clínica Veterinária",
        "description": "API privada da clínica: login, cadastros, atendimento clínico e acompanhamento da integração com o governo. Projeto A3 · Sistemas Distribuídos e Mobile.",
        "version": "1.0.0",
    },
    "servers": [{"url": "http://localhost:5000", "description": "Servidor local"}],
    "tags": TAGS_CLINICA,
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http", "scheme": "bearer", "bearerFormat": "JWT",
                "description": "Token devolvido por POST /auth/login. Mande como 'Authorization: Bearer <token>'.",
            }
        },
        "schemas": SCHEMAS_CLINICA,
    },
    "paths": PATHS_CLINICA,
}


# ============================================================
# api-governo
# ============================================================

SCHEMAS_GOVERNO = {
    "Erro": ERRO,
    "CadastroAnimal": {
        "type": "object",
        "required": ["chave_idempotencia", "id_animal_clinica", "nome"],
        "properties": {
            "chave_idempotencia": {"type": "string", "description": "UUID gerado pela clínica; reenviar com a mesma chave não duplica o registro"},
            "id_animal_clinica": {"type": "integer", "description": "id do animal no sistema da clínica"},
            "nome": {"type": "string"},
            "especie": {"type": "string"},
            "raca": {"type": "string"},
            "numero_microchip": {"type": "string", "nullable": True},
        },
    },
    "RegistroVacina": {
        "type": "object",
        "required": ["chave_idempotencia", "id_animal_clinica", "id_vacina_clinica"],
        "properties": {
            "chave_idempotencia": {"type": "string"},
            "id_animal_clinica": {"type": "integer", "description": "o animal precisa já estar cadastrado (ver POST /animais/)"},
            "id_vacina_clinica": {"type": "integer", "description": "id da vacina no sistema da clínica"},
            "data_aplicacao": {"type": "string", "format": "date"},
            "lote": {"type": "string", "nullable": True},
        },
    },
    "ProtocoloResposta": {
        "type": "object",
        "properties": {
            "protocolo": {"type": "string", "example": "AN-20261124211317-7AG4"},
            "repetido": {"type": "boolean", "description": "true quando a chave_idempotencia já tinha sido recebida antes"},
        },
    },
    "AnimalRegistrado": {
        "type": "object",
        "properties": {
            "id_registro": {"type": "integer"},
            "id_animal_clinica": {"type": "integer"},
            "nome": {"type": "string"},
            "especie": {"type": "string"},
            "raca": {"type": "string", "nullable": True},
            "numero_microchip": {"type": "string", "nullable": True},
            "protocolo": {"type": "string"},
            "data_registro": {"type": "string"},
            "data_atualizacao": {"type": "string", "nullable": True},
        },
    },
}

PARAM_SIMULAR_FALHA = {
    "name": "simular_falha", "in": "query", "required": False,
    "schema": {"type": "integer", "enum": [0, 1]},
    "description": "1 = devolve 503 de propósito, para testar o reenvio do lado da clínica",
}

OPENAPI_GOVERNO = {
    "openapi": "3.0.3",
    "info": {
        "title": "API Governamental Simulada",
        "description": "Finge ser o sistema do governo: recebe o cadastro de animais e as vacinas antirrábicas enviadas pela clínica. Tem banco de dados próprio, separado do banco da clínica. Projeto A3 · Sistemas Distribuídos e Mobile.",
        "version": "1.0.0",
    },
    "servers": [{"url": "http://localhost:5001", "description": "Servidor local"}],
    "tags": [
        {"name": "Animais", "description": "Cadastro/atualização de animais (upsert idempotente)."},
        {"name": "Vacinas", "description": "Registro de vacinas antirrábicas (idempotente)."},
    ],
    "components": {"schemas": SCHEMAS_GOVERNO},
    "paths": {
        "/": {
            "get": {
                "tags": ["Animais"], "summary": "Verifica se a API está no ar",
                "responses": {"200": resposta_json("No ar", {"type": "object", "properties": {"mensagem": {"type": "string"}}})},
            }
        },
        "/animais/": {
            "post": {
                "tags": ["Animais"],
                "summary": "Cadastra ou atualiza um animal (idempotente)",
                "parameters": [PARAM_SIMULAR_FALHA],
                "requestBody": {"required": True, "content": {"application/json": {"schema": ref("CadastroAnimal")}}},
                "responses": {
                    "200": resposta_json("Já tinha sido recebido antes (mesma chave_idempotencia): devolve o mesmo protocolo", ref("ProtocoloResposta")),
                    "201": resposta_json("Registrado", ref("ProtocoloResposta")),
                    "400": resposta_erro("chave_idempotencia, id_animal_clinica ou nome faltando"),
                    "409": resposta_erro("Erro de integridade ao gravar"),
                    "503": resposta_erro("Falha simulada (?simular_falha=1)"),
                },
            }
        },
        "/animais/{id_animal_clinica}": {
            "get": {
                "tags": ["Animais"], "summary": "Busca o registro de um animal",
                "parameters": [{"name": "id_animal_clinica", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": resposta_json("Encontrado", ref("AnimalRegistrado")), "404": resposta_erro("Animal não registrado no governo")},
            }
        },
        "/vacinas/": {
            "post": {
                "tags": ["Vacinas"],
                "summary": "Registra uma vacina antirrábica (idempotente)",
                "parameters": [PARAM_SIMULAR_FALHA],
                "requestBody": {"required": True, "content": {"application/json": {"schema": ref("RegistroVacina")}}},
                "responses": {
                    "200": resposta_json("Já tinha sido recebido antes: devolve o mesmo protocolo", ref("ProtocoloResposta")),
                    "201": resposta_json("Registrado", ref("ProtocoloResposta")),
                    "400": resposta_erro("Campo obrigatório faltando"),
                    "422": resposta_erro("O animal ainda não está cadastrado no governo"),
                    "409": resposta_erro("Erro de integridade ao gravar"),
                    "503": resposta_erro("Falha simulada (?simular_falha=1)"),
                },
            }
        },
    },
}


def salvar(caminho, documento):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(documento, f, ensure_ascii=False, indent=2)
    # valida que o próprio arquivo que acabamos de escrever é JSON válido
    with open(caminho, encoding="utf-8") as f:
        json.load(f)
    print(f"OK: {caminho} ({len(documento['paths'])} caminhos)")


if __name__ == "__main__":
    salvar(os.path.join(RAIZ, "api-clinica", "openapi.json"), OPENAPI_CLINICA)
    salvar(os.path.join(RAIZ, "api-governo", "openapi.json"), OPENAPI_GOVERNO)
