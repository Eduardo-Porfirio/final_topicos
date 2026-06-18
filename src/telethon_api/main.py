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
        # Telegram exige pelo menos 1 usuário para criar um grupo normal.
        # Vamos separar usernames (ex: @portal_sigaa_bot) dos números de telefone.
        # O UserBot resolve usernames muito mais fácil do que telefones não-salvos na agenda.
        usernames = [u for u in request.users_to_add if u.startswith('@')]
        phones = [u for u in request.users_to_add if not u.startswith('@')]
        
        # Garante pelo menos o bot para a criação
        initial_users = usernames if usernames else ["@portal_sigaa_bot"]

        # Cria o grupo
        result = await client(CreateChatRequest(
            users=initial_users,
            title=request.turma_nome
        ))
        
        chat_id = None
        
        # O método mais seguro no Telethon recente é iterar pelos chats retornados
        if hasattr(result, 'chats') and len(result.chats) > 0:
            chat_id = result.chats[0].id
        elif hasattr(result, 'updates'):
            # Em alguns casos do UserBot, ele retorna na aba 'updates'
            u_list = result.updates
            if hasattr(u_list, 'updates'):
                u_list = u_list.updates
                
            for u in u_list:
                if hasattr(u, 'chat_id'):
                    chat_id = u.chat_id
                    break
                elif hasattr(u, 'message') and hasattr(u.message, 'peer_id') and hasattr(u.message.peer_id, 'chat_id'):
                    chat_id = u.message.peer_id.chat_id
                    break

        if not chat_id:
            # Se ainda assim não achar, podemos buscar o último diálogo (gambiarra segura para userbot recém-criador)
            dialogs = await client.get_dialogs(limit=1)
            if dialogs:
                chat_id = dialogs[0].id

        if not chat_id:
            raise Exception("Erro crítico: Grupo criado, mas não foi possível extrair o ID do Chat.")

        # Promove o bot de gestão (@portal_sigaa_bot) a administrador para que ele possa gerenciar o grupo
        from telethon.tl.functions.messages import EditChatAdminRequest
        try:
            bot_username = "@portal_sigaa_bot"
            await client(EditChatAdminRequest(
                chat_id=chat_id,
                user_id=bot_username,
                is_admin=True
            ))
            print(f"Bot {bot_username} promovido a administrador do grupo {chat_id}")
        except Exception as e:
            print(f"Não foi possível promover o bot {bot_username} a administrador: {e}")

        # Agora tenta adicionar os usuários restantes (telefones, etc)
        from telethon.tl.functions.messages import AddChatUserRequest
        
        # Filtra quem não está no initial_users para não duplicar
        remaining_users = [u for u in request.users_to_add if u not in initial_users]
        
        for user in remaining_users:
            try:
                await client(AddChatUserRequest(
                    chat_id=chat_id,
                    user_id=user,
                    fwd_limit=100
                ))
            except Exception as e:
                print(f"Não foi possível adicionar {user}: {e}")

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


class MemberRemoveRequest(BaseModel):
    chat_id: int
    user_phone: str


@app.post("/remove-member")
async def remove_member(request: MemberRemoveRequest):
    if not await client.is_user_authorized():
        raise HTTPException(status_code=401, detail="UserBot não autorizado.")
    try:
        from telethon.tl.functions.messages import DeleteChatUserRequest
        
        # O chat_id no Telethon para normal group deve ser positivo
        chat_id_telethon = abs(request.chat_id)
        
        await client(DeleteChatUserRequest(
            chat_id=chat_id_telethon,
            user_id=request.user_phone
        ))
        return {"status": "success", "message": f"Usuário {request.user_phone} removido do chat {chat_id_telethon}"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
