# Contexto do Projeto
- **Framework Principal:** Django na versão 6.0.4
- **Ambiente de Produção:** sem ambiente de produção, apenas container docker de testes
- **Controle de Versão:** Git.

# Regras de Desenvolvimento
1. Ao criar novas `views` ou modelos, retorne o código sempre acompanhado de um teste unitário básico.
2. Não utilize pacotes externos desnecessários; prefira as bibliotecas nativas do Python ou do próprio Django.
3. Se a instrução envolver alterações na infraestrutura (como regras de Nginx ou certificados SSL), forneça apenas os comandos de diagnóstico primeiro. Não gere comandos de reinício de serviço (`systemctl restart`) sem que eu peça explicitamente.
4. Seja especifico nas alterações em código do ambiente, não gere código desnecessário ou fora do escopo do projeto

# Segurança e Uso do Telegram (UserBot)
5. **Prevenção de Banimento:** O UserBot utiliza um número de telefone pessoal. NUNCA realize disparos em massa, loops de criação de grupos ou requisições repetitivas que possam ser interpretadas como spam pelo Telegram.
6. **Prioridade para Mocks:** Em ambiente de desenvolvimento e testes unitários, SEMPRE utilize mocks para simular a API do Telegram/Telethon. Evite acionar a API real desnecessariamente.
7. **Limitação de Criação:** A criação real de grupos deve ser feita apenas para validação final ou sob demanda explícita do usuário.

# Padrões de Ambiente
- Assuma que o usuário do terminal no servidor é `root`.
- O diretório final_topicos está mapeado para dentro do container no `/app`, duvidas confira o arquivo `docker-compose.yml` e `dockerfile` na raiz do projeto
- Todo o código bruto do projeto está localizado em `src`
- Dúvidas sobre o escopo do projeto podem ser conferidas na pasta `scope_project` Onde contem a documentação de como deve funcionar e as tabelas do banco de dados
