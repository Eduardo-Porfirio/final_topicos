import json
import urllib.request
import urllib.error
import logging

logger = logging.getLogger(__name__)

def create_telegram_group(turma_nome, users_to_add=None):
    """
    Chama o microserviço Telethon para criar um novo grupo.
    URL interna do container: http://telethon_service:8001/create-group
    """
    url = "http://telethon_service:8001/create-group"
    payload = {
        "turma_nome": turma_nome,
        "users_to_add": users_to_add or []
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if response.status == 200:
                logger.info(f"Grupo criado com sucesso no Telethon: {result.get('chat_id')}")
                return result
            else:
                logger.error(f"Erro ao criar grupo no Telethon: Status {response.status}")
                return None
    except urllib.error.URLError as e:
        logger.error(f"Erro de conexão com o microserviço Telethon: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado na integração com Telethon: {e}")
        return None


def remove_telegram_group_member(chat_id, phone_number):
    """
    Chama o microserviço Telethon para remover um membro do grupo.
    URL interna do container: http://telethon_service:8001/remove-member
    """
    url = "http://telethon_service:8001/remove-member"
    payload = {
        "chat_id": chat_id,
        "user_phone": phone_number
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        logger.error(f"Erro de conexão ao remover membro no Telethon: {e}")
        return False
