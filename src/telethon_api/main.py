from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.tl.functions.messages import CreateChatRequest
import os
import asyncio
from dotenv import load_dotenv

# Carrega .env manualmente (procurando na raiz do projeto, um nível acima de src/telethon_api)
load_dotenv(dotenv_path="../.env")

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title="Telethon UserBot Microservice")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"ERRO DE VALIDAÇÃO: {exc.errors()}")
    print(f"BODY RECEBIDO: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(await request.body())},
    )

# Credenciais
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

# Convertendo API_ID para int
API_ID = int(API_ID) if API_ID else 0

# Persistência da sessão em arquivo
SESSION_NAME = 'userbot_session'
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

class CodeRequest(BaseModel):
    phone: str
    code: str
    phone_code_hash: str

@app.on_event("startup")
async def startup_event():
    await client.connect()
    print(f"Telethon conectado? {await client.is_user_authorized()}")

@app.post("/request-code")
async def request_code():
    """Primeiro passo: Solicita o código SMS ao Telegram"""
    if not client.is_connected():
        await client.connect()
    try:
        sent_code = await client.send_code_request(PHONE)
        return {"status": "code_sent", "phone_code_hash": sent_code.phone_code_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(request: CodeRequest):
    """Segundo passo: Finaliza o login com o código recebido"""
    try:
        await client.sign_in(request.phone, request.code, phone_code_hash=request.phone_code_hash)
        return {"status": "logged_in", "authorized": await client.is_user_authorized()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GroupCreateRequest(BaseModel):
    turma_nome: str
    users_to_add: list[str] = []

@app.post("/create-group")
async def create_group(request: GroupCreateRequest):
    if not await client.is_user_authorized():
        raise HTTPException(status_code=401, detail="UserBot não autorizado. Realize o login via /request-code e /login")

    try:
        # UserBots PODEM usar CreateChatRequest
        result = await client(CreateChatRequest(
            users=request.users_to_add,
            title=request.turma_nome
        ))
        
        print(f"DEBUG RESULT TYPE: {type(result)}")
        
        # Tenta extrair o chat_id de forma agressiva
        chat_id = None
        
        # 1. Tenta atributo chats
        if hasattr(result, 'chats') and result.chats:
            chat_id = result.chats[0].id
            
        # 2. Tenta atributo updates recursivamente
        if chat_id is None and hasattr(result, 'updates'):
            u_list = result.updates
            if hasattr(u_list, 'updates'): # Se for um objeto Updates que contém uma lista updates
                u_list = u_list.updates
            
            if isinstance(u_list, list):
                for u in u_list:
                    # Alguns updates tem chat_id, outros tem peer_id.chat_id
                    if hasattr(u, 'chat_id'):
                        chat_id = u.chat_id
                        break
                    elif hasattr(u, 'message') and hasattr(u.message, 'peer_id') and hasattr(u.message.peer_id, 'chat_id'):
                        chat_id = u.message.peer_id.chat_id
                        break
                    elif hasattr(u, 'peer') and hasattr(u.peer, 'chat_id'):
                        chat_id = u.peer.chat_id
                        break
        
        # Caso 3: Fallback para InvitedUsers ou outros objetos que tenham chats (mesmo que escondidos)
        if chat_id is None:
            # Tenta pegar qualquer atributo que pareça um ID de chat
            try:
                # InvitedUsers costuma ter um link ou referência
                print(f"DEBUG OBJ STR: {str(result)}")
            except: pass
            
        if chat_id is None:
            raise Exception(f"Não foi possível extrair o chat_id do retorno tipo {type(result)}")

        return {"status": "success", "chat_id": chat_id, "turma": request.turma_nome}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "connected": client.is_connected(), 
        "authorized": await client.is_user_authorized()
    }
