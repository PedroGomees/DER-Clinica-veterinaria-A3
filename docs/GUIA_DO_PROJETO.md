# Guia do Projeto SDM – Clínica Veterinária

Este guia explica o que é o projeto, o que tem em cada pasta e arquivo, como o Flask funciona, como o login funciona, e como front-end, back-end e banco de dados conversam entre si. Foi escrito para quem nunca usou Flask.

> Procurando **como o sistema foi construído, em etapas** (para a apresentação ou o relatório)? Veja [`ETAPAS_DE_DESENVOLVIMENTO.md`](ETAPAS_DE_DESENVOLVIMENTO.md).

---

## 1. O que é o projeto

Um sistema web para uma clínica veterinária. Ele permite:

- fazer login como veterinário (com cadastro e senha);
- cadastrar tutores (com endereço, preenchido automaticamente pelo CEP) e seus animais;
- registrar consultas, vacinas e o vínculo de microchip na ficha de cada animal;
- comunicar ao governo (simulado) o cadastro dos animais e as vacinas antirrábicas, acompanhando o status de cada envio.

O sistema é feito de **três programas independentes**, mais os bancos de dados:

| Programa | Tecnologia | Porta | Função |
|---|---|---|---|
| **Frontend** | HTML, CSS, JavaScript | 8000 | A tela que o usuário vê |
| **API da clínica** | Python + Flask | 5000 | Login, regras de negócio e acesso ao banco da clínica |
| **API governamental simulada** | Python + Flask | 5001 | Finge ser o sistema do governo |
| **Banco da clínica** | MariaDB (XAMPP) | 3306 | Dados da clínica (`clinica_veterinaria`) |
| **Banco do governo** | MariaDB (XAMPP) | 3306 | Dados do governo (`governo_simulado`), separado |
| **ViaCEP** | API pública na internet | – | Consulta de endereço pelo CEP (só consumimos) |

---

## 2. Front e back são separados? Como tudo se comunica?

**Sim, são separados.** O frontend não tem acesso ao banco de dados. Ele só sabe "pedir coisas" para a API por HTTP, e a API responde com JSON.

```
 Navegador (frontend, porta 8000)
        │  HTTP / JSON  (fetch, com o token de login no cabeçalho)
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
| `requirements.txt` | Bibliotecas Python: Flask, flask-cors, PyMySQL, python-dotenv, requests, **PyJWT** (login). |
| `.env.example` | Modelo das configurações (banco, `SECRET_KEY` do login, endereço do governo). Cada pessoa copia para `.env`. |
| `app/__init__.py` | `create_app()`: cria o Flask, liga o CORS, **registra todos os blueprints** e trata erros (404/405/500) em JSON. |
| `app/config.py` | Lê o `.env` e guarda tudo numa classe `Config`. |
| `app/db.py` | `get_conn()`, que abre a conexão com o MariaDB. Aceita `autocommit=False` para operações que gravam em duas tabelas de uma vez (ver `tutores.py`). |
| `app/auth.py` | Geração e conferência do **token de login (JWT)**: `gerar_token()` e o decorator `@login_required`. |
| `app/validacoes.py` | Funções pequenas: validar CPF, CEP, achar campos obrigatórios faltando. |
| `app/routes/` | **Um arquivo por assunto.** Veja a tabela abaixo. |
| `app/services/viacep_service.py` | Fala com a API pública ViaCEP. |
| `app/services/governo_service.py` | Fala com a API governamental simulada: registra a tentativa, envia, e sabe reenviar usando a mesma chave de idempotência. |
| `tests/` | Reservado para testes automatizados futuros (hoje vazio). |

Rotas (`app/routes/`), todas exigindo login (`@login_required`) **exceto** `auth`, `especies`, `racas`, `enderecos` (cadastro de apoio) e `cep`:

| Arquivo | Prefixo | O que cobre |
|---|---|---|
| `auth.py` | `/auth` | Cadastro e login do veterinário, token JWT |
| `especies.py` | `/especies` | CRUD de espécie (o modelo original) |
| `racas.py` | `/racas` | CRUD de raça (sempre ligada a uma espécie) |
| `enderecos.py` | `/enderecos` | CRUD de endereço |
| `tutores.py` | `/tutores` | CRUD de tutor, já gravando o endereço junto (transação) |
| `animais.py` | `/animais` | CRUD de animal + aviso automático ao governo |
| `veterinarios.py` | `/veterinarios` | Lista de veterinários (somente leitura) |
| `consultas.py` | `/consultas` | CRUD de consulta (o veterinário vem do token) |
| `vacinas.py` | `/vacinas` | CRUD de vacina; antirrábica aciona o governo |
| `microchips.py` | `/microchips` | Vincular/desvincular microchip, com histórico |
| `cep.py` | `/cep` | Consulta de CEP via ViaCEP |
| `integracoes.py` | `/integracoes` | Painel da integração com o governo + reenvio |

### 4.3 `api-governo/` – o "governo" simulado

| Arquivo | O que faz |
|---|---|
| `app/routes/animais.py` | `POST /animais/`: cadastra ou atualiza um animal (idempotente); aceita `?simular_falha=1` para testes. |
| `app/routes/vacinas.py` | `POST /vacinas/`: registra uma vacina antirrábica (o animal precisa já estar cadastrado). |
| `app/utils.py` | Gera o número de protocolo (ex.: `AN-20261123153000-X7K9`). |

Roda na porta **5001**, com banco próprio (`governo_simulado`).

### 4.4 `database/` – scripts SQL

| Arquivo | O que faz |
|---|---|
| `clinica/schema.sql` | Cria o banco `clinica_veterinaria` e as 10 tabelas do DER, com chaves, unicidades e regras. |
| `clinica/seed.sql` | Espécies (Cachorro, Gato, Ave, Coelho), uma raça "SRD" por espécie, e um **veterinário de demonstração** (`dev@clinica.com` / `clinica123`). |
| `governo/schema.sql` | Cria o banco `governo_simulado` (animais registrados, vacinas registradas e controle de idempotência). |

> O banco do XAMPP é **local** de cada pessoa e não vai para o GitHub. Por isso os `.sql` ficam no repositório: cada pessoa roda os scripts e fica com o mesmo banco. Se alguém mudar uma tabela, deve atualizar o `schema.sql` e avisar o grupo.

### 4.5 `docs/`

| Item | O que é |
|---|---|
| `der/A3_DER_Clinica_Veterinaria.drawio` | DER editável no draw.io (versão final). |
| `der/A3_DER_Clinica_Veterinaria.pdf` / `.png` | O mesmo DER em PDF e imagem, para o documento acadêmico. |
| `der/versoes-anteriores/` | Versão antiga do DER, guardada por segurança. |
| `GUIA_DO_PROJETO.md` | Este guia. |
| `ETAPAS_DE_DESENVOLVIMENTO.md` | Como o sistema foi construído, passo a passo. |

### 4.6 `frontend/`

| Arquivo | O que faz |
|---|---|
| `login.html` | Tela de entrada: login e cadastro de veterinário (dois formulários, um botão alterna entre eles). |
| `index.html` | Painel inicial: saudação, contadores (tutores, animais, integrações com falha) e explicação do fluxo. |
| `tutores.html` | Lista, busca, cria e edita tutores. O formulário tem o botão **Buscar CEP**, que preenche o endereço. |
| `animais.html` | Lista, busca, cria e edita animais. O formulário tem os selects encadeados **espécie → raça**. |
| `animal.html` | **Ficha do animal**, a tela mais importante: três abas (Consultas, Vacinas, Microchip), cada uma com formulário de registro e histórico. |
| `cadastros.html` | Administração de Espécies e Raças. |
| `integracoes.html` | Painel da integração com o governo: status de cada envio, com botão **Reenviar** nos que falharam. |
| `js/api.js` | Função `api.get/post/put/delete`: monta o `fetch`, inclui o token de login no cabeçalho e trata erros. |
| `js/auth.js` | `getToken`, `salvarSessao`, `logout`, `exigirLogin` (usadas por toda página protegida). |
| `js/nav.js` | Desenha a barra lateral (igual em todas as páginas) e funções auxiliares (`escaparHtml`, `formatarData`, `mostrarAviso`). |
| `css/style.css` | Sistema visual único: cores, cartões, tabelas, formulários, modais, selos de status, abas, responsivo. |

---

## 5. Como o Flask funciona

Flask é uma biblioteca Python para criar **servidores web**. Ele fica "escutando" numa porta, esperando pedidos (requisições), e para cada pedido executa uma função sua e devolve uma resposta.

### 5.1 Os 5 conceitos básicos

1. **Rota (endpoint):** um endereço + um método HTTP que está ligado a uma função. Exemplo: `GET /especies/`.
2. **Método HTTP:** o "verbo" do pedido (`GET`, `POST`, `PUT`, `DELETE`).
3. **Requisição (`request`):** o que o cliente mandou (corpo JSON, parâmetros na URL, cabeçalhos como o token de login).
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
3. **registra cada Blueprint** (`app.register_blueprint(especies.bp)`, e assim por diante para os 12 módulos);
4. define a rota de teste `GET /` e os tratadores de erro (404/405/500 em JSON).

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
- `autocommit=True` por padrão: cada `INSERT`/`UPDATE` já é gravado na hora.
- **Sempre use `%s` e passe os valores numa tupla.** Nunca monte o SQL concatenando texto: isso abriria brecha para **SQL injection** (um ataque em que o usuário digita SQL malicioso no campo).

**Transação (duas tabelas de uma vez só):** criar um tutor grava `endereco` e `tutor`. Se a segunda gravação falhasse depois da primeira já ter acontecido, sobraria um endereço "órfão". Por isso `tutores.py` usa `get_conn(autocommit=False)` e só confirma (`conn.commit()`) depois das duas gravações; se algo der errado, `conn.rollback()` desfaz tudo.

---

## 6. Login e token (JWT)

O login não guarda "sessão" no servidor. Em vez disso:

1. `POST /auth/login` confere o e-mail e a senha (a senha fica no banco como **hash**, nunca em texto puro — `werkzeug.security.generate_password_hash`/`check_password_hash`).
2. Se estiver certo, a API gera um **token** (`app/auth.py → gerar_token`): um texto assinado digitalmente que carrega o id e o nome do veterinário, com validade de 8 horas.
3. O frontend guarda esse token no `localStorage` (`js/auth.js → salvarSessao`) e o manda em **todo** pedido seguinte, no cabeçalho `Authorization: Bearer <token>` (`js/api.js`).
4. Nas rotas protegidas, o decorator `@login_required` confere a assinatura do token antes de deixar a função rodar. Se o token não vier, estiver errado ou tiver expirado, a API responde `401` — e o frontend manda o usuário de volta para `login.html` (`js/api.js`, ao ver um 401).

Como o token carrega os dados assinados, a API **não precisa consultar o banco para saber quem está logado** em cada pedido — só confere a assinatura. É por isso que `g.veterinario["id_veterinario"]` é usado direto em `consultas.py`, `vacinas.py` e `microchips.py` para saber quem está registrando o quê, sem o frontend precisar informar isso.

---

## 7. Como funciona um endpoint, passo a passo

Exemplo real: o usuário registra uma vacina antirrábica na ficha do animal.

```
1. animal.html        chama  api.post("/vacinas/", {..., antirrabica: true})
2. js/api.js           faz    fetch(".../vacinas/", método POST, corpo JSON, com o token no cabeçalho)
3. Navegador            envia  o pedido HTTP para a porta 5000 (o CORS libera)
4. Flask                 confere o token (@login_required) e encontra a rota POST /vacinas/ → função criar()
5. criar()                lê o JSON, valida os campos, grava em INSERT INTO vacina ...
6. criar()                como antirrabica = 1, chama governo_service.enviar_vacina_antirrabica(...)
7. governo_service    grava uma linha em integracao_governo (PENDENTE) e faz POST para a API do governo
8. API do governo     grava no banco dela, devolve um protocolo
9. governo_service    marca a integração como CONFIRMADO (ou FALHA, se algo der errado)
10. criar()               responde {"id_vacina": 7} com status 201
11. animal.html         atualiza o histórico de vacinas na tela
```

Repare que os passos 6–9 acontecem **dentro** do mesmo pedido, mas o resultado da integração com o governo não trava nem derruba o cadastro da vacina: se falhar, a vacina continua salva e a falha fica registrada para reenvio (tela **Integração governo**).

### Códigos de status HTTP que usamos

| Código | Significado | Quando |
|---|---|---|
| `200` | OK | Consulta ou atualização deu certo |
| `201` | Criado | Um registro novo foi criado (POST) |
| `400` | Pedido inválido | Faltou um campo obrigatório ou o dado é inválido |
| `401` | Não autenticado | Faltou o token, ou ele é inválido/expirou, ou a senha está errada |
| `404` | Não encontrado | O id pedido não existe |
| `409` | Conflito | Ex.: CPF duplicado, ou o animal já tem um microchip ativo |
| `422` | Não processável | Ex.: a API do governo recebeu uma vacina de um animal que ela não conhece |
| `500` | Erro no servidor | Bug ou banco fora do ar |

O `js/api.js` olha o status: se não for sucesso, lança um erro com a mensagem que veio no campo `erro` do JSON (e, se for `401`, já manda para o login).

---

## 8. O que é CRUD

**CRUD** são as 4 operações básicas sobre qualquer dado: **C**reate (criar), **R**ead (ler), **U**pdate (atualizar), **D**elete (apagar). Cada uma corresponde a um método HTTP e a um comando SQL:

| Operação | Método HTTP | Endpoint (espécie) | SQL |
|---|---|---|---|
| **Create** | `POST` | `POST /especies/` | `INSERT INTO especie ...` |
| **Read** (lista) | `GET` | `GET /especies/` | `SELECT ... FROM especie` |
| **Read** (um) | `GET` | `GET /especies/3` | `SELECT ... WHERE id_especie = 3` |
| **Update** | `PUT` | `PUT /especies/3` | `UPDATE especie SET ... WHERE id_especie = 3` |
| **Delete** | `DELETE` | `DELETE /especies/3` | no nosso caso, `UPDATE ... SET ativo = 0` |

### Inativação lógica (por que o DELETE não apaga)
No nosso projeto, "excluir" significa **marcar `ativo = 0`**, e não apagar a linha, para espécie, raça, endereço (indiretamente), tutor e animal. Motivo: um tutor ou um animal pode já ter histórico (consultas, vacinas). Apagar quebraria esses registros. Consulta não tem campo `ativo`: "cancelar" marca `status = 'CANCELADA'`. Vínculo de microchip nunca é apagado: "desvincular" marca `ativo = 0` e preenche `data_desvinculacao`.

### Validações
Antes de gravar, a rota confere o que chegou (campos obrigatórios, CPF válido, sexo entre `M`/`F`, etc.). Se faltar algo, responde `400` com uma mensagem clara. **Nunca confie nos dados que vêm do frontend:** a validação precisa estar na API.

---

## 9. Como criar um novo módulo (receita)

Exemplo: um CRUD novo qualquer.

1. Copie `app/routes/especies.py` (CRUD simples) ou `app/routes/consultas.py` (CRUD que usa `@login_required` e `g.veterinario`) para o novo arquivo.
2. Troque o nome do blueprint e o prefixo: `Blueprint("nome", __name__, url_prefix="/nome")`.
3. Troque a tabela e os campos nos SQLs.
4. Ajuste as validações.
5. Registre em `app/__init__.py`: importe o módulo e chame `app.register_blueprint(nome.bp)`.
6. Teste no Postman/Thunder Client, ou com o `python -c` mostrado no README.
7. Faça a tela no frontend usando `api.get("/nome/")` etc.

---

## 10. Como as integrações funcionam

### ViaCEP (API pública)
O frontend **não** chama o ViaCEP direto. Ele chama a **nossa** rota `GET /cep/<cep>`, que usa `app/services/viacep_service.py` para consultar `https://viacep.com.br/ws/<cep>/json/`. Vantagem: o tratamento de erro fica num lugar só, e o frontend não depende de um serviço externo estar sempre no ar da mesma forma.

### API governamental simulada
1. A clínica registra uma vacina antirrábica (`antirrabica = 1`) ou cadastra/atualiza um animal.
2. `app/services/governo_service.py` cria uma linha em `integracao_governo` com status `PENDENTE` e uma **chave de idempotência** (um UUID).
3. Ela envia uma requisição HTTP `POST` para a API governamental (porta 5001), em `/animais/` ou `/vacinas/`.
4. O governo confere a `chave_idempotencia`: se já viu essa chave antes, devolve o **mesmo protocolo** de novo (não duplica nada); senão, grava no **banco dele** e gera um protocolo novo.
5. A clínica marca `CONFIRMADO` (com o protocolo) ou, se a chamada falhar, `FALHA` (com a mensagem de erro e `tentativas` incrementado).
6. A tela **Integração governo** lista tudo isso e tem um botão **Reenviar** para as linhas com `FALHA` — o reenvio usa a mesma chave de idempotência, então é seguro repetir.

Para testar uma falha de propósito, a API do governo aceita `?simular_falha=1` (ex.: chamando `POST http://localhost:5001/animais/?simular_falha=1` direto).

---

## 11. Como rodar tudo (resumo)

1. Ligue o MySQL no XAMPP e rode os `.sql` de `database/` no phpMyAdmin (clinica/schema.sql → clinica/seed.sql → governo/schema.sql).
2. Em `api-clinica/`: crie o `venv`, instale o `requirements.txt`, copie `.env.example` para `.env` e rode `python run.py`.
3. Em `api-governo/`: o mesmo, e a porta será 5001.
4. Em `frontend/`: `python -m http.server 8000` e abra `http://localhost:8000/login.html`.
5. Entre com o veterinário de demonstração (`dev@clinica.com` / `clinica123`) ou cadastre um novo.

Para testar a API sem o frontend, use o Postman / Thunder Client, sempre mandando o cabeçalho `Authorization: Bearer <token>` nas rotas protegidas (o token vem da resposta de `POST /auth/login`).

---

## 12. Status atual

**Pronto:** DER; as 10 tabelas e os seeds; login com JWT; CRUD completo de espécie, raça, endereço, tutor (com transação) e animal; consultas, vacinas e microchip; ViaCEP; API governamental simulada com idempotência; o acompanhamento e reenvio das integrações; e o frontend completo (login, painel, tutores, animais, ficha do animal com 3 abas, cadastros de apoio e o painel de integrações), com um visual único em todas as telas.

**Ainda vale revisar com o grupo:** rodar os scripts `.sql` contra o MariaDB de verdade (foram escritos e revisados, mas testados aqui só com um banco simulado, sem MariaDB disponível nesta máquina — veja o aviso no README); Swagger/OpenAPI; testes automatizados de verdade (hoje a verificação é manual/roteirizada); apresentação final.

---

## 13. Glossário rápido

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
| **JWT** | "JSON Web Token": o formato do token de login, assinado digitalmente. |
| **Hash de senha** | Transformação de mão única da senha; o banco nunca guarda a senha em texto puro. |
| **Idempotência** | Repetir a mesma operação não gera duplicidade. |
| **Transação** | Um grupo de gravações que acontece tudo ou nada (commit/rollback). |
| **venv** | Ambiente virtual do Python: isola as bibliotecas de cada projeto. |
| **SQL injection** | Ataque que insere SQL malicioso num campo; evitado com `%s`. |
