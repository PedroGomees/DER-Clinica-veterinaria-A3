# SDM – Sistema de Gestão de Clínica Veterinária

Projeto A3 – Sistemas Distribuídos e Mobile.

Documentação completa: [`docs/GUIA_DO_PROJETO.md`](docs/GUIA_DO_PROJETO.md) (o que é cada arquivo, como o Flask e o login funcionam) e [`docs/ETAPAS_DE_DESENVOLVIMENTO.md`](docs/ETAPAS_DE_DESENVOLVIMENTO.md) (como o sistema foi construído, passo a passo).

## Arquitetura

```
Frontend Web (HTML/CSS/JS)  --HTTP/REST/JSON-->  API da Clínica (Flask) --SQL--> MariaDB (clinica_veterinaria)
                                                      |-- HTTPS/GET/JSON --> API pública ViaCEP
                                                      |-- HTTP/REST/JSON --> API Governamental Simulada (Flask) --SQL--> MariaDB (governo_simulado)
```

| Pasta | O que é | Porta |
|---|---|---|
| `frontend/` | Interface web (login, tutores, animais, ficha clínica, integrações) | 8000 |
| `api-clinica/` | API privada da clínica (Flask): login, cadastros, atendimento, integrações | 5000 |
| `api-governo/` | API governamental simulada (Flask) | 5001 |
| `database/` | Scripts SQL (a fonte da verdade do banco) | – |
| `docs/` | DER e documentação | – |

## Como rodar (cada pessoa, na sua máquina)

Pré-requisitos: Python 3.10+, XAMPP (MariaDB) e Git.

### 1. Banco de dados
1. Abra o XAMPP e inicie o **MySQL**.
2. Abra o phpMyAdmin (http://localhost/phpmyadmin) → aba **SQL** (ou **Importar**) e rode, nesta ordem:
   1. `database/clinica/schema.sql`
   2. `database/clinica/seed.sql`
   3. `database/governo/schema.sql`

> O banco do XAMPP é local: ele **não** vai para o GitHub. Por isso os scripts `.sql` ficam no repositório.
> Mudou o banco? Atualize o `schema.sql` e avise o grupo.
>
> ⚠️ Estes scripts foram escritos e revisados com cuidado, mas **testados aqui apenas contra um banco simulado** (não havia MariaDB disponível na máquina onde o projeto foi montado). Rode-os no XAMPP e teste um fluxo completo (tutor → animal → consulta/vacina/microchip) antes de confiar neles de olhos fechados. Veja a seção "Testes" de [`docs/ETAPAS_DE_DESENVOLVIMENTO.md`](docs/ETAPAS_DE_DESENVOLVIMENTO.md#6-testes-sem-ter-o-mariadb-disponível) para saber exatamente o que já foi validado.

### 2. API da clínica
```bash
cd api-clinica
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```
Teste: http://localhost:5000/ e http://localhost:5000/especies/
Documentação interativa (Swagger UI): http://localhost:5000/docs

### 3. API governamental simulada
```bash
cd api-governo
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```
Teste: http://localhost:5001/
Documentação interativa (Swagger UI): http://localhost:5001/docs

### 4. Frontend
```bash
cd frontend
python -m http.server 8000
```
Abra http://localhost:8000/login.html

**Login de demonstração** (criado pelo `seed.sql`, para não precisar se cadastrar primeiro):
- E-mail: `dev@clinica.com`
- Senha: `clinica123`

(troque a senha, ou apague esse usuário, antes de qualquer uso fora do ambiente de desenvolvimento)

## O que o sistema faz

- **Login** de veterinário, com cadastro, senha com hash e token (JWT).
- **Tutores**: cadastro com endereço (preenchido automaticamente a partir do CEP, via ViaCEP).
- **Animais**: cadastro ligado a um tutor, espécie e raça (com validação de que a raça pertence à espécie).
- **Ficha do animal**: consultas, vacinas (com a flag "antirrábica") e vínculo de microchip, com histórico preservado.
- **Integração com o governo**: toda vacina antirrábica e todo cadastro/atualização de animal é comunicado à API governamental simulada; a tela "Integração governo" mostra o status de cada envio e permite reenviar os que falharam.

## Documentação da API (Swagger/OpenAPI)

Cada API expõe sua própria documentação interativa, direto no navegador:
- Clínica: http://localhost:5000/docs
- Governo: http://localhost:5001/docs

A especificação (`openapi.json`, na raiz de cada API) é gerada pelo script `docs/gerar_openapi.py`. Se alguém criar uma rota nova, adicione ela na lista de `PATHS_CLINICA`/`PATHS_GOVERNO` desse script e rode de novo:
```bash
python docs/gerar_openapi.py
```

## Trabalho em grupo (Git)

- `main` só recebe código que funciona.
- Cada tarefa em uma branch: `git checkout -b feature/nome-da-tarefa`.
- Abra um Pull Request para a `main` e peça revisão de um colega.
- Commits pequenos e com mensagem clara ("adiciona CRUD de tutor").
- **Nunca** suba o arquivo `.env` (senhas e a chave do login). Só o `.env.example`.
- Cada módulo de rotas fica em um arquivo próprio em `api-clinica/app/routes/` para evitar conflitos.

## Cronograma

| Semana | Entrega |
|---|---|
| 1 (29/10) | Modelagem e arquitetura |
| 2 (05/11) | Banco de dados e API privada |
| 3 (12/11) | Interface web e funcionalidades clínicas |
| 4 (19/11) | API governamental e integração |
| 5 (26/11) | Testes, documentação e apresentação |
