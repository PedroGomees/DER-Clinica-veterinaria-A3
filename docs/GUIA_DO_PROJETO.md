# Guia do Projeto SDM – Clínica Veterinária

Este guia explica o que é o projeto, o que tem em cada pasta e arquivo, como o Flask funciona e como front-end, back-end e banco de dados conversam entre si. Foi escrito para quem nunca usou Flask.

---

## 1. O que é o projeto

Um sistema web para uma clínica veterinária. Ele permite cadastrar tutores e animais, registrar consultas e vacinas, vincular microchip e comunicar ao governo (simulado) o cadastro dos animais e as vacinas antirrábicas.

O sistema é feito de **três programas independentes**, mais os bancos de dados:

| Programa | Tecnologia | Porta | Função |
|---|---|---|---|
| **Frontend** | HTML, CSS, JavaScript | 8000 | A tela que o usuário vê |
| **API da clínica** | Python + Flask | 5000 | Regras de negócio e acesso ao banco da clínica |
| **API governamental simulada** | Python + Flask | 5001 | Finge ser o sistema do governo |
| **Banco da clínica** | MariaDB (XAMPP) | 3306 | Dados da clínica (`clinica_veterinaria`) |
| **Banco do governo** | MariaDB (XAMPP) | 3306 | Dados do governo (`governo_simulado`), separado |
| **ViaCEP** | API pública na internet | – | Consulta de endereço pelo CEP (só consumimos) |

---

## 2. Front e back são separados? Como tudo se comunica?

**Sim, são separados.** O frontend não tem acesso ao banco de dados. Ele só sabe "pedir coisas" para a API por HTTP, e a API responde com JSON.

```
 Navegador (frontend, porta 8000)
        │  HTTP / JSON  (fetch)
        ▼
 API da clínica (Flask, porta 5000)  ──SQL──►  Banco clinica_veterinaria
        │
        ├──HTTPS / GET / JSON──►  ViaCEP (internet)
        │
        └──HTTP / JSON──►  API governamental (Flask, porta 5001) ──SQL──► Banco governo_simulado
```

Regras importantes dessa arquitetura:

- **Só a API da clínica fala com o banco da clínica.** O frontend nunca faz SQL.
- **Só a API governamental fala com o banco do governo.** A clínica não acessa esse banco; ela manda uma requisição HTTP e recebe a resposta.
- **Todos conversam por HTTP com JSON.** JSON é só um formato de texto para trocar dados, por exemplo `{"nome": "Cachorro"}`.
- Cada parte pode ser feita, testada e rodada separadamente. Isso ajuda o trabalho em grupo.

### Por que precisamos do CORS?
O navegador bloqueia, por segurança, uma página em `localhost:8000` que tenta chamar `localhost:5000` (portas diferentes contam como "sites" diferentes). O pacote `flask-cors`, ativado no `create_app`, diz ao navegador: "pode deixar, o frontend tem permissão". Sem isso, o `fetch` do frontend falha com erro de CORS.

---

## 3. Estrutura de pastas

```
.
├── README.md                  Instruções rápidas de instalação e execução
├── .gitignore                 O que o Git deve ignorar (venv, .env, etc.)
├── .gitattributes / LICENSE   Criados pelo GitHub
├── api-clinica/               API privada da clínica (Flask)
├── api-governo/               API governamental simulada (Flask)
├── database/                  Scripts SQL (a "fonte da verdade" do banco)
├── docs/                      DER e documentação
└── frontend/                  Interface web
```

---

## 4. Cada pasta e cada arquivo

### 4.1 Raiz

| Arquivo | O que faz |
|---|---|
| `README.md` | Porta de entrada do projeto: arquitetura, como rodar, regras de Git. |
| `.gitignore` | Lista o que **não** vai para o GitHub: `venv/`, `__pycache__/`, `.env` (senhas) e arquivos do editor. |
| `.gitattributes` | Padroniza o fim de linha dos arquivos entre Windows e outros sistemas. |
| `LICENSE` | Licença do projeto, criada pelo GitHub. |

### 4.2 `api-clinica/` – o back-end principal

| Arquivo | O que faz |
|---|---|
| `run.py` | **Ponto de partida.** Cria o app e o liga na porta 5000. Você roda `python run.py`. |
| `requirements.txt` | Lista das bibliotecas Python (Flask, flask-cors, PyMySQL, python-dotenv, requests). Instala com `pip install -r requirements.txt`. |
| `.env.example` | Modelo das configurações (host, usuário e senha do banco). Cada pessoa copia para `.env` e ajusta. O `.env` real **nunca** vai para o Git. |
| `app/__init__.py` | Contém `create_app()`: cria o Flask, liga o CORS e **registra os módulos de rotas**. É aqui que você pluga cada novo módulo. |
| `app/config.py` | Lê as variáveis do `.env` e as guarda numa classe `Config` (host, porta, usuário, senha e nome do banco). |
| `app/db.py` | A função `get_conn()`, que abre uma conexão com o MariaDB. Todo código que precisa do banco chama ela. |
| `app/routes/` | **Um arquivo por assunto** (espécies, tutores, animais...). Cada arquivo define os endpoints daquele assunto. |
| `app/routes/especies.py` | CRUD completo de espécie. **É o modelo** para os demais módulos. |
| `app/services/` | Código que conversa com serviços externos (ViaCEP, API do governo). Ainda vazio. |
| `tests/` | Futuros testes automatizados. |

### 4.3 `api-governo/` – o "governo" simulado

Tem a mesma estrutura, só que menor, e roda na porta **5001** com banco próprio (`governo_simulado`).
Por enquanto responde só `GET /`. Na Semana 4 ela vai receber o cadastro de animais e as vacinas antirrábicas, devolver um **protocolo** e poder simular falhas.

### 4.4 `database/` – scripts SQL

| Arquivo | O que faz |
|---|---|
| `clinica/schema.sql` | Cria o banco `clinica_veterinaria` e as 10 tabelas do DER, com chaves, unicidades e regras. |
| `clinica/seed.sql` | Insere dados iniciais: espécies (Cachorro, Gato, Ave, Coelho) e uma raça "SRD" para cada espécie. |
| `governo/schema.sql` | Cria o banco `governo_simulado` (animais registrados, vacinas registradas e controle de idempotência). |

> O banco do XAMPP é **local** de cada pessoa e não vai para o GitHub. Por isso os `.sql` ficam no repositório: cada pessoa roda os scripts e fica com o mesmo banco. Se alguém mudar uma tabela, deve atualizar o `schema.sql` e avisar o grupo.

### 4.5 `docs/`

| Item | O que é |
|---|---|
| `der/A3_DER_Clinica_Veterinaria.drawio` | DER editável no draw.io (versão final). |
| `der/A3_DER_Clinica_Veterinaria.pdf` / `.png` | O mesmo DER em PDF e imagem, para o documento acadêmico. |
| `der/versoes-anteriores/` | Versão antiga do DER, guardada por segurança. |
| `GUIA_DO_PROJETO.md` | Este guia. |

### 4.6 `frontend/`

| Arquivo | O que faz |
|---|---|
| `index.html` | Página de teste: lista as espécies e tem um formulário para cadastrar. Mostra na prática como o front chama a API. |
| `js/api.js` | **Funções que falam com a API.** Define o endereço da API e `api.get`, `api.post`, `api.put` e `api.delete`. Todas as páginas usam este arquivo. |
| `css/style.css` | Estilo visual básico. |

---

## 5. Como o Flask funciona

Flask é uma biblioteca Python para criar **servidores web**. Ele fica "escutando" numa porta, esperando pedidos (requisições), e para cada pedido executa uma função sua e devolve uma resposta.

### 5.1 Os 5 conceitos básicos

1. **Rota (endpoint):** um endereço + um método HTTP que está ligado a uma função. Exemplo: `GET /especies/`.
2. **Método HTTP:** o "verbo" do pedido (`GET`, `POST`, `PUT`, `DELETE`).
3. **Requisição (`request`):** o que o cliente mandou (corpo JSON, parâmetros na URL).
4. **Resposta:** o que a API devolve (JSON + código de status).
5. **Blueprint:** um "grupo de rotas" em um arquivo próprio, para não ter tudo num arquivo gigante.

### 5.2 Anatomia de uma rota (do nosso `especies.py`)

```python
bp = Blueprint("especies", __name__, url_prefix="/especies")   # grupo de rotas; todas começam com /especies

@bp.get("/")                       # GET /especies/
def listar():
    with get_conn() as conn, conn.cursor() as cur:             # abre conexão com o banco
        cur.execute("SELECT ... FROM especie")                 # executa o SQL
        return jsonify(cur.fetchall())                         # devolve o resultado como JSON
```

- `@bp.get("/")` diz: "quando chegar um GET em `/especies/`, execute a função abaixo".
- `jsonify(...)` transforma dicionários e listas Python em JSON.
- `<int:id_especie>` na rota (ex.: `/especies/<int:id_especie>`) captura um número da URL e o entrega como parâmetro da função.

### 5.3 A "fábrica" do app (`create_app`)

Em vez de criar o Flask solto, usamos a função `create_app()` (em `app/__init__.py`). Ela:

1. cria o app e carrega as configurações (`Config`);
2. liga o CORS;
3. **registra cada Blueprint** (`app.register_blueprint(especies.bp)`);
4. define a rota de teste `GET /`.

Quando o `run.py` roda, ele chama `create_app()` e sobe o servidor. **Registrar o Blueprint é obrigatório:** se você criar um arquivo de rotas e esquecer de registrá-lo no `__init__.py`, as rotas não existem.

### 5.4 Configuração e `.env`

Senhas e endereços do banco **não ficam escritos no código**. Ficam no `.env` (fora do Git). O `config.py` lê esse arquivo e o `db.py` usa as configurações para conectar. Assim, cada integrante pode ter uma senha diferente no seu XAMPP sem alterar o código.

### 5.5 A conexão com o banco (`db.py`)

```python
with get_conn() as conn, conn.cursor() as cur:
    cur.execute("SELECT ... WHERE id = %s", (valor,))
```

- `get_conn()` abre a conexão; o `with` fecha automaticamente no final.
- O **cursor** (`cur`) é quem executa SQL e traz resultados.
- Usamos `DictCursor`: cada linha vem como dicionário (`{"id_especie": 1, "nome": "Cachorro"}`), que o `jsonify` converte direto em JSON.
- `autocommit=True`: cada `INSERT`/`UPDATE` já é gravado na hora.
- **Sempre use `%s` e passe os valores numa tupla.** Nunca monte o SQL concatenando texto: isso abriria brecha para **SQL injection** (um ataque em que o usuário digita SQL malicioso no campo).

---

## 6. Como funciona um endpoint, passo a passo

Exemplo real: o usuário digita "Hamster" no formulário e clica em Adicionar.

```
1. index.html        chama  api.post("/especies/", {nome: "Hamster"})
2. js/api.js         faz    fetch("http://localhost:5000/especies/", método POST, corpo JSON)
3. Navegador         envia  o pedido HTTP para a porta 5000 (o CORS libera)
4. Flask             encontra a rota "POST /especies/" → função criar()
5. criar()           lê o JSON com request.get_json(), valida o campo "nome"
6. criar()           abre a conexão (get_conn) e executa  INSERT INTO especie ...
7. MariaDB           grava a linha e devolve o id gerado (cur.lastrowid)
8. criar()           responde  {"id_especie": 5}  com status 201
9. js/api.js         recebe o JSON e devolve ao index.html
10. index.html       recarrega a lista e a tela mostra "Hamster"
```

### Códigos de status HTTP que usamos

| Código | Significado | Quando |
|---|---|---|
| `200` | OK | Consulta ou atualização deu certo |
| `201` | Criado | Um registro novo foi criado (POST) |
| `400` | Pedido inválido | Faltou um campo obrigatório ou o dado é inválido |
| `404` | Não encontrado | O id pedido não existe |
| `500` | Erro no servidor | Bug ou banco fora do ar |

O `js/api.js` olha o status: se não for sucesso, lança um erro com a mensagem que veio no campo `erro` do JSON.

---

## 7. O que é CRUD

**CRUD** são as 4 operações básicas sobre qualquer dado: **C**reate (criar), **R**ead (ler), **U**pdate (atualizar), **D**elete (apagar). Cada uma corresponde a um método HTTP e a um comando SQL:

| Operação | Método HTTP | Endpoint (espécie) | SQL |
|---|---|---|---|
| **Create** | `POST` | `POST /especies/` | `INSERT INTO especie ...` |
| **Read** (lista) | `GET` | `GET /especies/` | `SELECT ... FROM especie` |
| **Read** (um) | `GET` | `GET /especies/3` | `SELECT ... WHERE id_especie = 3` |
| **Update** | `PUT` | `PUT /especies/3` | `UPDATE especie SET ... WHERE id_especie = 3` |
| **Delete** | `DELETE` | `DELETE /especies/3` | no nosso caso, `UPDATE ... SET ativo = 0` |

### Inativação lógica (por que o DELETE não apaga)
No nosso projeto, "excluir" significa **marcar `ativo = 0`**, e não apagar a linha. Motivo: uma espécie, um tutor ou um animal pode já ter histórico (consultas, vacinas). Apagar quebraria esses registros. Por isso as tabelas têm o campo `ativo`, e as listagens normalmente mostram só os ativos (`WHERE ativo = 1`).

### Validações
Antes de gravar, a rota confere o que chegou (ex.: `nome` é obrigatório). Se faltar algo, responde `400` com uma mensagem clara. **Nunca confie nos dados que vêm do frontend:** a validação precisa estar na API.

---

## 8. Como criar um novo módulo (receita)

Exemplo: CRUD de tutores.

1. Copie `app/routes/especies.py` para `app/routes/tutores.py`.
2. Troque o nome do blueprint e o prefixo: `Blueprint("tutores", __name__, url_prefix="/tutores")`.
3. Troque a tabela e os campos nos SQLs (`tutor`, `nome_completo`, `cpf`, etc.).
4. Ajuste as validações (CPF obrigatório, etc.).
5. Registre em `app/__init__.py`: `from .routes import tutores` e `app.register_blueprint(tutores.bp)`.
6. Teste no Postman ou Thunder Client.
7. Faça a tela no frontend usando `api.get("/tutores/")` etc.

---

## 9. Como as integrações vão funcionar

### ViaCEP (API pública)
O frontend **não** chama o ViaCEP direto. Ele chama a **nossa** API (`GET /cep/<cep>`), que consulta `https://viacep.com.br/ws/<cep>/json/` com a biblioteca `requests` e devolve o resultado. Vantagem: o tratamento de erro fica num lugar só.

### API governamental simulada
1. A clínica registra uma vacina antirrábica (`antirrabica = 1`) ou cadastra um animal.
2. A API da clínica cria uma linha em `integracao_governo` com status `PENDENTE` e uma **chave de idempotência**.
3. Ela envia uma requisição HTTP para a API governamental (porta 5001).
4. O governo grava no **banco dele**, devolve um **protocolo** e a clínica marca `CONFIRMADO`.
5. Se o governo estiver fora do ar, a clínica marca `FALHA`, guarda a mensagem de erro e **tenta de novo** depois (campo `tentativas`).

A **idempotência** garante que, se a clínica reenviar a mesma operação (por causa de uma falha de rede, por exemplo), o governo **não duplica** o registro: ele reconhece a chave e devolve o mesmo protocolo.

---

## 10. Como rodar tudo (resumo)

1. Ligue o MySQL no XAMPP e rode os `.sql` de `database/` no phpMyAdmin.
2. Em `api-clinica/`: crie o `venv`, instale o `requirements.txt`, copie `.env.example` para `.env` e rode `python run.py`.
3. Em `api-governo/`: o mesmo, e a porta será 5001.
4. Em `frontend/`: `python -m http.server 8000` e abra `http://localhost:8000`.

Para testar a API sem o frontend, use o navegador (`http://localhost:5000/especies/`) ou o Postman / Thunder Client.

---

## 11. Status atual

**Pronto:** DER, scripts SQL, estrutura das duas APIs, CRUD de espécie, página de teste no frontend.

**Falta fazer:** CRUD de raça, endereço, tutor e animal; login do veterinário; ViaCEP; consultas, vacinas e microchip; API governamental e a integração; telas do frontend; testes, Swagger/OpenAPI, documentação e apresentação.

---

## 12. Glossário rápido

| Termo | Significado |
|---|---|
| **API** | Programa que recebe pedidos e devolve dados, sem tela. |
| **Endpoint** | Um endereço específico da API (ex.: `GET /especies/`). |
| **Rota** | A ligação entre um endereço + método e a função que o atende. |
| **REST** | Estilo de API onde cada coisa tem um endereço e os verbos HTTP indicam a ação. |
| **JSON** | Formato de texto para trocar dados entre programas. |
| **Blueprint** | Grupo de rotas do Flask num arquivo separado. |
| **CORS** | Permissão para um site em uma porta chamar uma API em outra. |
| **CRUD** | Criar, ler, atualizar e apagar. |
| **Idempotência** | Repetir a mesma operação não gera duplicidade. |
| **venv** | Ambiente virtual do Python: isola as bibliotecas de cada projeto. |
| **SQL injection** | Ataque que insere SQL malicioso num campo; evitado com `%s`. |
