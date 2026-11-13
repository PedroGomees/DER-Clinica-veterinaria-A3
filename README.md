# SDM – Sistema de Gestão de Clínica Veterinária

Projeto A3 – Sistemas Distribuídos e Mobile.

## Arquitetura

```
Frontend Web (HTML/CSS/JS)  --HTTP/REST/JSON-->  API da Clínica (Flask) --SQL--> MariaDB (clinica_veterinaria)
                                                      |-- HTTPS/GET/JSON --> API pública ViaCEP
                                                      |-- HTTP/REST/JSON --> API Governamental Simulada (Flask) --SQL--> MariaDB (governo_simulado)
```

| Pasta | O que é | Porta |
|---|---|---|
| `frontend/` | Interface web | 8000 |
| `api-clinica/` | API privada da clínica (Flask) | 5000 |
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

### 4. Frontend
```bash
cd frontend
python -m http.server 8000
```
Abra http://localhost:8000

## Trabalho em grupo (Git)

- `main` só recebe código que funciona.
- Cada tarefa em uma branch: `git checkout -b feature/nome-da-tarefa`.
- Abra um Pull Request para a `main` e peça revisão de um colega.
- Commits pequenos e com mensagem clara ("adiciona CRUD de tutor").
- **Nunca** suba o arquivo `.env` (senhas). Só o `.env.example`.
- Cada módulo de rotas fica em um arquivo próprio em `api-clinica/app/routes/` para evitar conflitos.

## Cronograma

| Semana | Entrega |
|---|---|
| 1 (29/10) | Modelagem e arquitetura |
| 2 (05/11) | Banco de dados e API privada |
| 3 (12/11) | Interface web e funcionalidades clínicas |
| 4 (19/11) | API governamental e integração |
| 5 (26/11) | Testes, documentação e apresentação |
