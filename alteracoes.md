# Registro de Alterações Críticas

Este arquivo documenta as principais mudanças realizadas no projeto, com foco em correções de lógica, persistência de dados e mudanças estruturais.

## [2026-06-11] - Correção de Persistência e Padronização de API

### Período Letivo (`src/periodo_letivo/views.py`)
- **Ativação de Persistência:** Descomentadas as chamadas de `.save()` nas views `inserir_periodo_letivo_view`, `encerrar_periodo_letivo_view` e `inicia_periodo_letivo_view`. Agora os dados são gravados no banco de dados.
- **Retorno de ID:** A view de inserção agora retorna o ID do registro criado no JSON de resposta.

### Componente Curricular (`src/comp_curricular/views.py`)
- **Ativação de Persistência:** Descomentada a chamada de `.save()` na view `inserir_comp_curricular_view`.
- **Padronização JSON:** Substituído o uso de `HttpResponse` por `JsonResponse` em todas as rotas da app para manter a consistência.
- **Suporte a Lote:** A view de inserção agora suporta o recebimento de uma lista de componentes em uma única requisição.
- **Tratamento de Erros:** Adicionada validação de campos obrigatórios e tratamento de `JSONDecodeError`.

## [2026-06-11] - Melhorias no Dashboard e Roteamento

### Dashboard (`src/core/views.py` e `src/templates/dashboard.html`)
- **Novas Estatísticas:** Adicionado o contador de "Componentes Curriculares" ao painel principal.
- **Atualização de Layout:** Grid do dashboard ajustada para comportar 4 cards em telas grandes (layout 1/2/4 colunas responsivo).
- **Links Dinâmicos:** Atualizados os links dos cards para apontarem para as rotas corretas usando a tag `{% url %}`.

### Roteamento (`src/periodo_letivo/urls.py` e `src/comp_curricular/urls.py`)
- **Nomes de Rotas:** Adicionado o parâmetro `name` aos `path` das URLs para permitir o uso de `reverse` e da tag `{% url %}` nos templates, corrigindo erros de `NoReverseMatch`.

## [2026-06-17] - Refinamento de Lógica, Validações e Conformidade

### Modelos e Representação (`__str__`)
- **Exibição Amigável:** Implementado o método `__str__` em todos os modelos principais (`PeriodoLetivo`, `ComponenteCurricular`, `Turma`, `Noticia`, `Atividade`). Isso corrige o problema de exibição de objetos como "object (1)" no frontend, substituindo por nomes, códigos ou títulos legíveis.

### Formulários e Validações (`forms.py`)
- **Correção de Referência:** Corrigido erro em `NoticiaForm` que referenciava o campo `flstatus` em vez de `flenvio`.
- **Validação de Período:** Adicionada regra em `PeriodoLetivoForm` para impedir que a data final seja anterior à data inicial.
- **Campos Booleanos:** Ajustado o parâmetro `required=False` para todos os campos de checkbox (status, ativo, envio), permitindo que registros sejam salvos com valor "Falso".

### Views e APIs (`views.py`)
- **Padronização JSON:** Atualizada a view `consultar_periodo_letivo_view` para retornar `JsonResponse` em vez de texto puro.
- **Correção de Filtro:** Corrigida a lógica de `consultar_noticia_por_turma` para filtrar corretamente pelo ID da turma.

### Testes Automatizados
- **Infraestrutura de Testes:** Criados os primeiros testes unitários para o modelo `PeriodoLetivo` em `src/periodo_letivo/tests.py`.
- **Validação via Docker:** Testes executados e validados com sucesso dentro do container, garantindo conformidade com os critérios de avaliação.

## [2026-06-17] - Módulo de Integração Telegram (Mockup)

### Interface e Navegação
- **Novo Aplicativo:** Criado o app `telegram` para centralizar a futura integração com a API.
- **Painel de Gerenciamento:** Desenvolvida a tela de "Gerenciamento da API do Telegram" (`telegram/management/`) com métricas reais baseadas em banco de dados e logs de auditoria.
- **Central de Disparos:** Criado o mockup da tela "Disparos Telegram" (`telegram/disparos/`) para testar o fluxo de envio segmentado de mensagens (por turma, componente ou geral). Inclui formulário dinâmico utilizando JS.
- **Menu Global (Navbar):** Refatorada a barra de navegação principal. Todos os links principais ("Painel", "Períodos", "Disparos") foram movidos para dentro do **Menu Dropdown de Usuário** (representado pelo avatar), deixando a barra do topo mais limpa e minimalista.

### Infraestrutura Telegram
- **Modelagem de Dados:** Implementados os modelos `TelegramGroup` (vínculo entre turmas e grupos reais), `TelegramAuditLog` (rastreio de eventos) e o **Modelo Singleton `TelegramSettings`** para armazenar o Token do Bot no banco de dados.
- **Configurações Dinâmicas (Interface):** Criada a tela de `Configurações` vinculada ao menu do usuário, permitindo o cadastro e alteração do Token da API (`bot_token`) diretamente pela interface visual, sem necessidade de editar arquivos `.env`.
- **Inteligência de Envio:** A função utilitária `enviar_mensagem_telegram` foi refatorada para ler o token prioritariamente do banco de dados (`TelegramSettings`), utilizando o `.env` apenas como fallback de segurança.
- **Persistência:** Criadas e aplicadas migrações via Docker para sincronização com o banco de dados.
- **Métricas Dinâmicas e Listagem:** A view de gerenciamento agora consome dados reais dos novos modelos, exibindo estatísticas e os últimos logs de atividade. Além disso, a seção estática foi substituída por uma tabela dinâmica que lista todos os **Grupos Gerenciados**, exibindo o nome da turma, número de membros, ID no Telegram e link de convite clicável.
- **Webhook e Bot API:** Criado o endpoint `telegram/webhook/` (com `@csrf_exempt`) para escutar requisições diretas do Telegram. Implementado o processamento básico de comandos como `/start` e `/noticias`.
- **Lógica de Consulta via Bot:** A view do Webhook identifica a qual turma o grupo do Telegram pertence cruzando o `chat_id` com o banco de dados, busca as 5 últimas notícias cadastradas e responde no chat formatado em HTML.
- **Variáveis de Ambiente:** Adicionada a chave `TELEGRAM_BOT_TOKEN` em `.env.example` e configurada a leitura em `settings.py` para permitir requisições seguras à API do Telegram via `urllib.request`.

## Documentação da Arquitetura: Integração Telegram (Django + Telethon)

O projeto utiliza uma arquitetura híbrida para se comunicar com o Telegram, separando responsabilidades para evitar bloqueios síncronos no Django e contornar limitações da API oficial de Bots.

### 1. Divisão de Papéis
*   **API Oficial (BotFather) + Webhooks:** Responsável por **escutar mensagens** dos alunos e **enviar notificações**. Funciona dentro do container Django (`web`), acionada de forma assíncrona ("lazy") quando o Telegram envia um POST para a rota `/telegram/webhook/`.
*   **MTProto API (Telethon) + FastAPI:** Responsável por ações complexas, especificamente a **criação de grupos**. Funciona em um microserviço isolado (`app_telethon`), já que Bots comuns não têm permissão para criar grupos diretamente "do nada".

### 2. Passo a Passo: Fluxo de Criação de Grupos
Quando um professor "abre" uma turma no sistema, o seguinte fluxo acontece:
1.  **Gatilho Interno:** O Django salva a Turma no PostgreSQL.
2.  **Comunicação Inter-containers:** A view do Django dispara uma requisição POST interna para o microserviço (`http://telethon_service:8001/create-group`) passando o nome da disciplina.
3.  **Ação no Telegram:** O FastAPI recebe o JSON e aciona o **Telethon**. O Telethon (agindo com os privilégios da `API_ID` e `API_HASH`) se comunica com os servidores centrais do Telegram e cria um "Supergrupo".
4.  **Devolução do ID:** O Telegram devolve o `chat_id` gerado (ex: `-100987654321`) e o link de convite.
5.  **Persistência no Django:** O FastAPI retorna esses dados na resposta HTTP para o Django. O Django, por sua vez, salva isso no modelo `TelegramGroup`, amarrando aquela Turma àquele chat específico.

### 3. Passo a Passo: Disparo e Escuta de Mensagens
1.  **O Aluno Pergunta:** Um aluno digita `/noticias` no grupo recém-criado.
2.  **O Webhook Atua:** Os servidores do Telegram disparam um POST para o nosso servidor. O Django capta o `chat_id` remetente e procura na tabela `TelegramGroup` qual turma é a dona daquele chat.
3.  **A Resposta:** O Django levanta as últimas 5 notícias daquela turma, formata o texto e envia de volta usando o `TELEGRAM_BOT_TOKEN`, registrando a ação na tabela `TelegramAuditLog`.

---
*Notas:* O projeto segue em ambiente acadêmico com `@csrf_exempt` habilitado para facilitar testes locais via Docker.

