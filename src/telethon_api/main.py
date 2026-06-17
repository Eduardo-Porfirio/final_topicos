from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.tl.functions.messages import CreateChatRequest
import os

app = FastAPI(title="Telethon Microservice", description="Serviço para automação de grupos no Telegram")

# Credenciais do Telegram (MTProto API)
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Verificação básica
if not all([API_ID, API_HASH, BOT_TOKEN]):
    print("AVISO: Credenciais do Telegram incompletas no .env. O Telethon não iniciará corretamente.")
    API_ID = "12345" # Valores dummy apenas para o container não dar crash no ValueError
    API_HASH = "dummy_hash"

# Inicializa o client do Telethon
# Utilizamos a sessão em memória para simplificar, mas em prod o ideal é um arquivo de sessão persistente.
client = TelegramClient('bot_session', API_ID, API_HASH)

class GroupCreateRequest(BaseModel):
    turma_nome: str
    users_to_add: list[str] = []

@app.on_event("startup")
async def startup_event():
    # O bot precisa iniciar a sessão ao subir o FastAPI
    if API_ID and API_HASH and BOT_TOKEN:
        await client.start(bot_token=BOT_TOKEN)
        print("Bot Telethon iniciado com sucesso!")

@app.post("/create-group")
async def create_group(request: GroupCreateRequest):
    """
    Endpoint para criar um novo grupo no Telegram.
    Recebe o nome da turma e uma lista opcional de usernames para adicionar.
    """
    if not client.is_connected():
        raise HTTPException(status_code=503, detail="Telethon client não está conectado.")

    try:
        # A chamada MTProto para criar um grupo simples
        result = await client(CreateChatRequest(
            users=request.users_to_add,
            title=request.turma_nome
        ))
        
        # Extrai o ID do grupo recém-criado
        chat_id = result.chats[0].id
        
        # Dica: Em grupos criados via API, o ID costuma ser convertido para supergrupo ou adicionado um prefixo negativo.
        # Estamos pegando o ID bruto aqui.
        return {"status": "success", "chat_id": chat_id, "turma": request.turma_nome}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Endpoint simples para verificar se o microserviço está no ar."""
    return {"status": "ok", "connected": client.is_connected()}
