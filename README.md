# final_topicos

Resumo do setup Docker + desenvolvimento

Este repositório roda uma aplicação Django com Docker Compose. A seguir descrevo como os containers são construídos, o mapeamento de diretórios, variáveis de ambiente e comandos úteis para desenvolvimento.

Como os containers são criados
- O `Dockerfile` baseia a imagem em `python:3.12.13-slim-trixie`, instala dependências do sistema, atualiza `pip` e instala `Django==6.0.4` e `psycopg2-binary`.

- O `docker-compose.yml` define dois serviços principais:
	- `web`: build local (`build: .`), monta o diretório do projeto na raiz do container com `- .:/app`, e define `working_dir: /app/src`. Expõe a porta `8000` para desenvolvimento (`8000:8000`). Variáveis de ambiente relevantes são definidas ali (DEBUG, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD).
	- `postgres`: usa `postgres:16`, lê variáveis no `.env` (se existir), expõe `5433:5432` no host e monta o volume `postgres_data:/var/lib/postgresql/data` para persistência.

Mapeamento de diretórios e volume
- Host `.` é montado em `/app` do container `web`. O `working_dir` do serviço está em `/app/src`, ou seja, o código executado assume que `manage.py` e o código Django estão sob `src/`.
- O PostgreSQL persiste dados no volume nomeado `postgres_data` (definido no topo do `docker-compose.yml`).

Variáveis de ambiente e `.env`
- O compose usa um arquivo `.env` (opcional) para carregar variáveis usadas pelo serviço `postgres` (ex.: `POSTGRES_USER`, `POSTGRES_PASSWORD`).
- No `docker-compose.yml` também há variáveis passadas para `web` (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD). Para evitar avisos sobre variáveis não definidas, crie um arquivo `.env.example` e depois copie para `.env`.

Exemplo de `.env.example` (crie na raiz do projeto):

```
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=teste_sigaa
DB_HOST=postgres
DEBUG=1
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=teste_sigaa
```

Comandos úteis (desenvolvimento)
- Validar compose:

```bash
docker compose config
```

- Build (sem cache) e subir em background:

```bash
docker compose build --no-cache
docker compose up -d
```

- Ver logs:

```bash
docker compose logs -f web
docker compose logs -f postgres
```

- Entrar no container `web`:

```bash
docker compose exec web /bin/sh
# ou bash se disponível
```

- Rodar migrações, criar superuser e rodar servidor (dentro do container `web` ou usando `docker compose run`):

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py runserver 0.0.0.0:8000
```
