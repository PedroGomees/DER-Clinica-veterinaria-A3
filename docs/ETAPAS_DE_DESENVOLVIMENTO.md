# Etapas de desenvolvimento

Este documento registra **como o sistema foi construído**, em ordem, com as decisões tomadas e por quê. Serve de referência para o relatório/apresentação e para quem quiser entender o raciocínio por trás do código (não só o que ele faz, mas por que foi feito assim).

> Para entender a estrutura do projeto e como o Flask funciona, veja [`GUIA_DO_PROJETO.md`](GUIA_DO_PROJETO.md). Este documento aqui é sobre o **processo**, não sobre "como usar".

---

## Ponto de partida

O projeto já tinha, antes desta etapa:

- o DER completo (10 entidades, revisado e com as cardinalidades corretas);
- o `schema.sql` e o `seed.sql` do banco da clínica, batendo com o DER;
- o esqueleto das duas APIs Flask (`create_app`, `config`, `db.py`) e um único CRUD de exemplo (espécie), para servir de modelo;
- a estrutura de pastas (`api-clinica/`, `api-governo/`, `database/`, `docs/`, `frontend/`) e o repositório Git já criado no GitHub.

A tarefa desta etapa foi **terminar o sistema inteiro**: todos os CRUDs, login, as integrações (ViaCEP e governo), e todo o frontend, sem reescrever o que já funcionava.

---

## 1. Planejamento antes de escrever código

Antes de mexer em qualquer arquivo, foi decidido:

- **Ordem de construção:** autenticação → cadastros (raça, endereço, tutor, animal) → atendimento clínico (consulta, vacina, microchip) → integrações (ViaCEP, governo) → frontend → testes → documentação. Essa ordem segue a dependência real: não dá para testar "consulta" sem ter "animal", nem "animal" sem "tutor".
- **Login com JWT**, não sessão de servidor. Motivo: a API é *stateless* (não guarda quem está logado em memória), o que é mais simples de testar e de rodar em duas portas diferentes (clínica e governo) sem compartilhar estado.
- **Senha do veterinário:** nunca gravada em texto puro. Foi usado `werkzeug.security` (já vem com o Flask, não precisa de biblioteca nova) em vez de implementar hash na mão.
- **Quem registra cada consulta/vacina/microchip é o veterinário logado** (tirado do token), não um campo escolhido no formulário. Isso elimina uma tela inteira (escolher o veterinário) e corresponde ao uso real: quem preenche o formulário é quem está atendendo.
- **Nada de DELETE de verdade** em dado com histórico clínico. Cada tabela já previa isso no DER (`ativo`, `status`, `data_desvinculacao`); a implementação só seguiu a regra.

---

## 2. Backend da clínica: autenticação

Arquivos: `app/auth.py`, `app/validacoes.py`, `app/routes/auth.py`.

1. `validacoes.py` ganhou funções pequenas e reaproveitáveis (`cpf_valido`, `cep_valido`, `campos_faltando`), para não repetir validação em cada rota.
2. `auth.py` ficou só com a lógica de token: `gerar_token()` (cria o JWT, válido por 8 horas) e o decorator `@login_required` (lê o cabeçalho `Authorization`, confere a assinatura, e expõe `g.veterinario` para a rota usar).
3. `routes/auth.py` usa os dois: `POST /auth/registrar` (valida CPF, cria o hash da senha, insere), `POST /auth/login` (confere a senha com `check_password_hash`, atualiza `ultimo_acesso`, devolve o token) e `GET /auth/me` (só para o frontend confirmar que o token ainda vale).

**Decisão consciente:** o campo `email_confirmado` do DER existe, mas o projeto não tem servidor de e-mail. Em vez de deixar essa funcionalidade pela metade, o cadastro já marca `email_confirmado = 1` automaticamente, com um comentário no código explicando que, num sistema real, isso dependeria de enviar um link/código por e-mail antes.

---

## 3. Backend da clínica: cadastros

Arquivos: `app/routes/racas.py`, `enderecos.py`, `tutores.py`, `animais.py`, `veterinarios.py`.

- `racas.py` e `enderecos.py` seguiram exatamente o padrão de `especies.py` (o modelo que já existia).
- `tutores.py` foi o primeiro módulo "não trivial": criar ou editar um tutor também grava o endereço dele, e são duas tabelas. Para evitar um endereço órfão se a segunda gravação falhar, essa rota usa `get_conn(autocommit=False)` e confirma as duas gravações juntas (`conn.commit()`) ou desfaz as duas (`conn.rollback()`). Essa necessidade motivou adicionar o parâmetro `autocommit` em `app/db.py` (que, por padrão, continua `True`, sem quebrar as rotas já prontas).
- `animais.py` implementa a regra mais importante do DER: a raça precisa pertencer à espécie escolhida. Isso é garantido **no banco** (chave estrangeira composta `fk_animal_raca_especie`, que já existia no schema); a API só traduz o erro do banco (`IntegrityError`) numa mensagem de API (`400`) em vez de deixar vazar um erro de SQL cru.
- `veterinarios.py` é só leitura: existe para telas futuras que precisem mostrar "quem é quem", sem expor senha/CPF.

---

## 4. Backend da clínica: atendimento clínico

Arquivos: `consultas.py`, `vacinas.py`, `microchips.py`.

- **Consulta:** CRUD normal, com um detalhe: "excluir" uma consulta marca `status = 'CANCELADA'` em vez de apagar (consulta é histórico clínico).
- **Vacina:** ao criar uma vacina com `antirrabica = true`, a rota chama o serviço de integração com o governo **depois** de gravar a vacina, assim ela fica salva na clínica mesmo que a comunicação com o governo falhe.
- **Microchip** foi o módulo com mais regras de negócio:
  - um animal só pode ter um vínculo ativo por vez;
  - um número de chip só pode estar ativo em um animal por vez;
  - nunca apagar: "desvincular" marca `ativo = 0` e `data_desvinculacao`.

  Essas regras já existiam no `schema.sql` como colunas geradas + `UNIQUE` (`animal_ativo`, `chip_ativo`). A API faz a mesma conferência **antes** de tentar gravar (para devolver uma mensagem de erro legível, tipo "este animal já tem um microchip ativo"), e ainda captura `IntegrityError` como segunda linha de defesa, para o caso de duas pessoas tentarem vincular o mesmo chip ao mesmo tempo (condição de corrida). Nesse caso o banco é a autoridade final, não a API.

---

## 5. Integração com serviços externos

### ViaCEP
`app/services/viacep_service.py` é só uma função (`buscar_cep`) que chama `https://viacep.com.br/ws/<cep>/json/` com a biblioteca `requests` e devolve `None` se der qualquer problema de rede. A rota `GET /cep/<cep>` trata os três casos possíveis: CEP mal formado (`400`), ViaCEP fora do ar (`502`) e CEP não encontrado (`404`).

### API governamental simulada
Esta foi a parte mais trabalhosa, por ter duas pontas (clínica e governo) que precisam concordar num contrato.

**Do lado da clínica** (`app/services/governo_service.py`):
1. Toda tentativa de comunicação cria uma linha em `integracao_governo`, com uma **chave de idempotência** nova (um UUID).
2. A função tenta enviar (`POST` para `/animais/` ou `/vacinas/` do governo).
3. O resultado atualiza a mesma linha: `CONFIRMADO` com o protocolo, ou `FALHA` com a mensagem de erro. Nunca lança uma exceção para quem chamou, já que criar um animal não pode quebrar só porque o governo está fora do ar.
4. `reenviar()` repete o envio **usando a mesma chave de idempotência** salva da primeira vez.

**Do lado do governo** (`app/routes/animais.py` e `vacinas.py`, no `api-governo`):
1. Cada endpoint primeiro confere se já existe uma `operacao_recebida` com aquela chave; se sim, devolve o mesmo protocolo de novo, sem duplicar nada. É isso que torna o reenvio seguro.
2. O cadastro de animal usa `INSERT ... ON DUPLICATE KEY UPDATE`, então o mesmo endpoint serve tanto para "cadastrar" quanto para "atualizar" (a clínica manda `tipo_operacao` diferente, mas o governo trata as duas como um "salvar").
3. Registrar uma vacina exige que o animal já esteja cadastrado (`422` se não estiver), refletindo a ordem real: o animal precisa existir antes da vacina dele.
4. Os dois endpoints aceitam `?simular_falha=1`, só para testar o reenvio sem precisar desligar o servidor de verdade.

**Por que isso importa para a nota do projeto:** essa é a parte que demonstra "sistemas distribuídos" de verdade: dois serviços independentes, com bancos separados, que precisam continuar funcionando (ou pelo menos falhar de forma registrada e recuperável) mesmo quando um deles está indisponível.

---

## 6. Testes, sem ter o MariaDB disponível

Esta máquina onde o código foi escrito **não tem o XAMPP/MariaDB instalado**. Em vez de entregar o código sem testar, foi criado um banco falso em Python só para a validação:

- Um `pymysql.connect` falso devolve uma conexão/cursor que:
  - **confere se o número de `%s` no SQL bate com o número de parâmetros** (pega erro de "esqueci de passar um valor");
  - **olha o `FROM`/`INTO`/`UPDATE` do SQL** para saber qual tabela devolver como resultado fabricado (assim uma rota que faz `JOIN` com três tabelas recebe a linha certa, não a de qualquer tabela citada);
  - respeita a diferença entre "nenhum resultado" e "um resultado", para testar os casos de erro (ex.: tutor não encontrado → `404`).
- Em cima disso, o `app.test_client()` do próprio Flask disparou **todas as rotas das duas APIs**, incluindo os casos de erro de propósito (CPF inválido, sem token, microchip duplicado, vacina sem animal cadastrado no governo, etc.).
- Esse teste pegou pelo menos um bug de verdade: a rota de reenvio de integração (`POST /integracoes/<id>/reenviar`) fazia duas consultas SQL diferentes dentro do mesmo pedido, e a primeira versão do "banco falso" devolvia a linha errada para a segunda consulta, escondendo um `KeyError`. Corrigir o próprio teste (para ele reconhecer a tabela certa de cada consulta) revelou que o código da aplicação estava correto; o problema era só do simulador.
- Depois, as duas APIs foram **de fato colocadas no ar** (`python run.py`, com esse mesmo banco falso) e o frontend foi testado **clicando nas telas de verdade** num navegador: login, criar tutor (com busca de CEP real), listar/editar animal, abrir a ficha do animal e usar as três abas, cadastrar espécie/raça, e ver o painel de integrações (inclusive clicando em "Reenviar"). Não apareceu nenhum erro no console do navegador.

**O que isso garante, e o que não garante:** essa bateria de testes garante que o Python está correto (sem erros de digitação, de parâmetro, de importação, de formato de resposta) e que o frontend conversa certo com a API (JSON no formato esperado, CORS, token, etc.). **Não substitui** testar com o MariaDB de verdade: nomes de coluna errados no SQL, restrições `UNIQUE`/`FOREIGN KEY` reais e a performance das consultas só aparecem rodando contra o banco. Por isso, o primeiro passo de quem for usar o projeto deve ser rodar os scripts de `database/` no XAMPP e testar um fluxo completo (criar tutor → criar animal → registrar consulta/vacina/microchip) com o banco real.

---

## 7. Frontend

O frontend foi escrito por último de propósito: só depois de todas as rotas existirem e estarem testadas é que dava para saber exatamente quais campos cada tela precisava mandar e receber.

1. **Sistema visual primeiro** (`css/style.css`): cores, cartões, tabela, formulário, modal, abas e selos de status foram definidos uma vez só, antes de qualquer página, para todas saírem consistentes (a mesma barra lateral, os mesmos botões) sem repetir CSS.
2. **Infraestrutura compartilhada** (`js/api.js`, `js/auth.js`, `js/nav.js`): o `fetch` com o token, o guard de login, e a função que desenha a barra lateral. Assim, cada página HTML fica curta e focada só na sua própria tela.
3. **Páginas, na ordem das dependências:** login → painel inicial → tutores (CEP) → animais (espécie/raça) → ficha do animal (consultas/vacinas/microchip, as três abas) → cadastros de apoio → integrações.
4. A **ficha do animal** (`animal.html`) foi a página mais trabalhosa, porque reúne três fluxos (consulta, vacina, microchip) numa tela só, com abas, cada uma com seu formulário e sua lista de histórico. Isso espelha a estrutura do DER, com ANIMAL no centro das relações 1:N com CONSULTA, VACINA e VINCULO_MICROCHIP.

---

## 8. Documentação

Por fim, a documentação foi revisada/reescrita para refletir o sistema **pronto**, não mais o esqueleto inicial:

- `GUIA_DO_PROJETO.md`: atualizado com todas as rotas, o funcionamento do login/JWT, a transação do tutor, e o status real do projeto.
- `ETAPAS_DE_DESENVOLVIMENTO.md` (este arquivo): o histórico do processo, para quem for apresentar o trabalho explicar as decisões tomadas.
- `README.md`: atualizado com o login de demonstração e qualquer novo passo de instalação.
- `database/clinica/seed.sql`: ganhou um veterinário de demonstração, para o grupo não precisar se cadastrar manualmente só para testar.

---

## 9. Teste contra o banco de verdade (depois que o XAMPP foi instalado)

Tudo até aqui tinha sido validado só com o banco simulado. Assim que o MariaDB ficou disponível (via XAMPP), foi feito um teste de ponta a ponta de verdade: login → criar tutor (com busca de CEP real) → criar animal → a clínica avisar a API governamental sozinha → registrar consulta → registrar vacina antirrábica → a vacina ser confirmada no governo, com protocolo → vincular microchip. Esse teste encontrou dois problemas reais, que só apareceriam rodando contra um banco de verdade:

1. **O `governo/schema.sql` tinha sido importado no banco errado** (`clinica_veterinaria` em vez de `governo_simulado`), um detalhe de como o phpMyAdmin mantém o banco selecionado entre importações, não um erro do script em si. Corrigido criando as tabelas certas no banco certo.
2. **Bug de fuso horário:** o Flask devolvia `datetime`/`date` no formato RFC 1123 (`"Tue, 24 Nov 2026 14:30:00 GMT"`), que **afirma** ser UTC. O navegador acreditava nisso e convertia para o fuso local, deslocando a hora exibida (e, em campos só de data, até o dia). Corrigido dos dois lados: a API agora devolve a data "crua" (`"2026-11-24 14:30:00"`, sem fuso) através de um `JSONProvider` próprio (`app/json_provider.py`), e o frontend (`js/nav.js`) lê esses números na mão, sem usar `new Date(texto)` (que é exatamente o que causa esse tipo de ambiguidade).

Isso mostra por que "testei com um banco simulado" não é a mesma coisa que "testei de verdade": erros de configuração (schema no banco errado) e erros de fuso horário só aparecem com infraestrutura real na mesa.

## 10. Documentação da API (Swagger/OpenAPI)

Depois do sistema completo e testado, foi gerada a documentação interativa dos endpoints, pendente desde a Semana 5 do cronograma:

- `docs/gerar_openapi.py` monta a especificação OpenAPI 3.0 das duas APIs (24 caminhos na clínica, 4 no governo) como um dicionário Python e grava em `openapi.json` dentro de cada pasta (`api-clinica/`, `api-governo/`). É um script, não um JSON escrito à mão, para ficar fácil de estender quando uma rota nova for criada.
- Cada API ganhou um módulo `app/routes/docs.py` com duas rotas nativas do Flask: `GET /openapi.json` (devolve o arquivo) e `GET /docs` (uma página HTML simples que carrega o Swagger UI via CDN, apontando para `/openapi.json`).
- A documentação foi testada de verdade: um login foi executado **direto pela tela do Swagger** (botão "Try it out"), contra a API rodando com o banco real, e devolveu o mesmo token que o frontend recebe.

## 11. Revisão de texto e visual

Depois de todo o sistema pronto e testado, vieram dois ajustes finais pedidos pelo grupo:

- **Revisão de texto:** a documentação e os comentários do código usavam bastante travessão (—), um sinal de pontuação comum em texto gerado por IA. Todas as ocorrências em prosa (markdown e comentários de código) foram reescritas sem esse símbolo, trocando por vírgula, dois-pontos ou frases mais curtas. O único lugar onde o "—" continua é dentro do frontend, como marcador visual de "campo vazio" numa tabela (ex.: telefone não informado), que é uma convenção de interface comum, não texto escrito.
- **Visual do frontend:** o CSS foi refeito com uma paleta própria (índigo/violeta), ícones em SVG desenhados à mão para a barra lateral (sem depender de nenhuma biblioteca de ícones nem de internet), avatar com as iniciais do veterinário logado, e uma tela de login com fundo em gradiente. O objetivo foi fugir da aparência "padrão" de um painel administrativo genérico. As telas principais (login, painel, tutores, ficha do animal, integrações) foram conferidas de novo no navegador depois da mudança.

## 12. Responsividade

Numa tela estreita, o menu lateral virava uma barra horizontal cheia de links, que não cabiam e ficavam cortados. A solução não foi tentar espremer os links numa linha só: o menu passou a se comportar como uma **gaveta**. Abaixo de 760px de largura, ele some da tela por completo e só aparece quando o usuário clica num botão de hambúrguer (☰) fixo no canto superior esquerdo, sobrepondo o conteúdo com um fundo escurecido atrás, igual ao padrão que a maioria dos aplicativos usa no celular. Clicar fora do menu, ou num link, fecha ele de novo.

## 13. Diferenciais do frontend

Depois do sistema completo, testado e com a documentação em dia, foram acrescentadas cinco melhorias pontuais, sugeridas para dar um diferencial ao projeto sem mexer na API nem no banco (menor risco, já perto da entrega):

1. **Filtros em Animais** (espécie, sexo, porte): como a lista inteira de animais já vem da API numa só chamada, os filtros são aplicados no próprio navegador (`aplicarFiltrosLocais()` em `animais.html`), sem precisar de parâmetros novos na API.
2. **Filtro de status em Tutores** (somente ativos / ativos e inativos): a API já aceita `?todos=1` desde o início; só faltava um controle na tela para usar essa opção, com uma coluna "Status" mostrando um selo verde ou cinza.
3. **Imprimir a ficha do animal**: um botão que chama `window.print()`. Uma regra `@media print` no CSS esconde o menu, os formulários e botões de ação (classe `.nao-imprime`), e força as três abas (consultas, vacinas, microchip) a aparecerem juntas na impressão, mesmo que só uma estivesse selecionada na tela.
4. **Alerta de vacina com dose próxima**: o campo `proxima_dose` já existia na tabela `vacina` desde o início, mas só aparecia dentro da ficha de cada animal. Um cartão novo no painel inicial busca todas as vacinas (`GET /vacinas/` sem filtro de animal), calcula quantos dias faltam para cada `proxima_dose` e mostra as mais urgentes primeiro, com selo "Atrasada" (vermelho), "Em breve" (laranja, até 7 dias) ou "Agendada" (azul, até 30 dias).
5. **Busca global (Ctrl+K)**: um campo de busca único, acessível de qualquer tela pela barra lateral ou pelo atalho de teclado, que busca tutores e animais ao mesmo tempo (`GET /tutores/?q=` e `GET /animais/?q=` em paralelo) e leva direto para a tela de cada resultado. Não precisou de nenhuma rota nova: reaproveita exatamente os mesmos endpoints que as telas de lista já usavam.

Como o XAMPP não estava ligado no momento em que essas cinco melhorias foram feitas, elas foram testadas de novo com o banco simulado (a mesma técnica da seção 6), e depois confirmadas com o banco de verdade assim que o MariaDB voltou a ficar disponível.

## Decisões que valem destacar (para perguntas da banca)

| Decisão | Por quê |
|---|---|
| JWT em vez de sessão de servidor | API sem estado, mais simples de escalar/testar, funciona igual em qualquer porta |
| Veterinário logado define quem atende | Reflete o uso real; evita campo redundante no formulário |
| Inativação lógica (`ativo`/`status`) em vez de `DELETE` | Preserva histórico clínico, que é dado sensível e não pode sumir |
| Transação na criação do tutor | Evita endereço "órfão" se a segunda gravação falhar |
| Chave de idempotência no envio ao governo | Permite reenviar com segurança sem duplicar registros |
| Falha no governo não derruba o cadastro local | Os dois sistemas são independentes; um fora do ar não pode travar o outro |
| Banco falso para testar sem MariaDB | Permitiu achar bugs de Python antes de depender de infraestrutura externa, mas não substitui testar com o banco de verdade |
| Datas sem fuso horário na API | O sistema é de uma clínica só, sem suporte a fusos diferentes; afirmar "isto é UTC" (como o Flask faz por padrão) só criava confusão e deslocava a hora exibida |
