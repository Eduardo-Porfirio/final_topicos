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

---
*Notas:* O projeto segue em ambiente acadêmico com `@csrf_exempt` habilitado para facilitar testes locais via Docker.

