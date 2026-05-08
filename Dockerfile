# Usamos o Python 3.9 (compatível com Django 3.1.4)
FROM python:3.12.13-slim-trixie


# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Evita que o Python gere arquivos .pyc e permite log em tempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependências do sistema (se precisar de banco de dados, adicione aqui)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Instala o Django 3.1.4 diretamente ou via requirements.txt
RUN pip install --upgrade pip
RUN pip install Django==6.0.4
RUN pip install psycopg2-binary
RUN pip install python-dotenv

# Copia o seu código para dentro do contêiner
COPY . .