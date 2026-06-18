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

## [2026-06-18] - Implementação e Ativação da Integração Django-Telethon (Real)

### Automação de Fluxo (Signals)
- **Criação Automática de Grupos:** Implementado o *Django Signal* `post_save` no modelo `Turma`. Agora, a criação de uma nova turma no sistema dispara automaticamente uma solicitação ao microserviço Telethon para gerar um grupo correspondente no Telegram.
- **Registro de Vínculo:** O sistema agora captura o `chat_id` real retornado pelo Telegram e o persiste automaticamente no modelo `TelegramGroup`, eliminando a necessidade de cadastro manual de IDs de chat.
- **Auditoria Automática:** Cada criação de grupo gera um registro no `TelegramAuditLog`, detalhando o sucesso ou falha da operação.

### Microserviço Telethon (UserBot)
- **Migração para UserBot:** O microserviço foi refatorado para operar como um usuário real (UserBot) em vez de um Bot convencional. Isso resolveu o erro `BotMethodInvalidError` e permitiu a criação de grupos via API (CreateChatRequest).
- **Autenticação Segura:** Implementado fluxo de login em dois passos (`request-code` e `login`) para autorizar a conta pessoal via código SMS.
- **Persistência de Sessão:** A sessão do usuário é persistida no arquivo `userbot_session.session`, garantindo que o serviço permaneça autenticado após reinicializações.
- **Extração Resiliente de ID:** Implementada lógica avançada de extração de `chat_id` para suportar diferentes tipos de objetos de retorno do Telegram (`Updates`, `InvitedUsers`), garantindo que o ID correto seja sempre enviado de volta ao Django.

### Camada de Serviço (Services)
- **Novo Arquivo `services.py`:** Toda a lógica de comunicação HTTP entre Django e Telethon foi isolada em `src/telegram/services.py`, utilizando a biblioteca nativa `urllib.request` (zero dependências externas).

### Segurança e Proteção de Dados
- **Proteção de Credenciais:** Removidos todos os logs e prints que exibiam dados sensíveis (Telefone, API_ID) no console.
- **Configuração via .env:** Todas as chaves críticas (`API_ID`, `API_HASH`, `TELEGRAM_PHONE`) são lidas estritamente de variáveis de ambiente.
- **Git Hygiene:** Atualizado o `.gitignore` para bloquear o commit acidental de arquivos de sessão do Telethon (`*.session`).

## [2026-06-18] - Transição para Criação Manual e Gestão de Membros

### Mudança de Estratégia (Manual vs Automático)
- **Desativação de Signals:** Removido o gatilho automático de criação de grupos em `src/turma/signals.py` (desativado em `apps.py`). Isso evita a criação indesejada de dezenas de grupos durante o carregamento de *fixtures* (`loaddata`) e protege o número pessoal do usuário contra banimentos por excesso de requisições.
- **Botão de Ação Manual:** Implementada nova interface no dashboard de gerenciamento que lista "Turmas Pendentes de Grupo". Cada turma possui agora um botão "Criar Grupo & Add Alunos".

### Refatoração de Modelos e Alunos
- **Correção do Modelo Aluno:** Adicionada a `ForeignKey` `idturma` ao modelo `Aluno` em `src/aluno/models.py`. Esta alteração alinha o código com as *fixtures* existentes e permite que múltiplos alunos sejam vinculados a uma única turma.
- **Sincronização de Banco:** Executadas migrações para refletir o novo relacionamento entre Aluno e Turma.

### Inteligência de Membros (Telethon)
- **Adição Automática de Alunos:** A view de criação manual agora busca todos os alunos vinculados à turma, limpa e formata seus números de telefone (adicionando prefixo +55) e envia a lista para o microserviço Telethon.
- **Criação com Convite:** O grupo é criado já incluindo os alunos cadastrados no sistema como membros iniciais.

### Dashboard e Testes
- **Interface Evoluída:** O dashboard agora exibe estatísticas em tempo real de turmas sem grupo e o número de alunos cadastrados em cada uma.
- **Suíte de Testes Atualizada:** Os testes em `src/telegram/tests.py` foram totalmente refatorados para validar o novo fluxo manual, garantindo que a busca de alunos e a comunicação com o Telethon funcionem conforme o esperado.

### Validação e Testes
- **Testes Unitários:** Criada suíte de testes em `src/telegram/tests.py` utilizando *mocks* para simular a API do Telethon.
- **Verificação Ponta a Ponta:** Realizados testes reais criando turmas via shell e admin, confirmando a criação física dos grupos no Telegram e a persistência correta dos dados no PostgreSQL.

