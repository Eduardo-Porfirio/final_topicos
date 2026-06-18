from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Turma
from telegram.models import TelegramGroup, TelegramAuditLog
from telegram.services import create_telegram_group

@receiver(post_save, sender=Turma)
def trigger_telegram_group_creation(sender, instance, created, **kwargs):
    """
    Sempre que uma nova Turma for criada, solicita ao microserviço Telethon
    a criação de um grupo correspondente no Telegram.
    """
    if created:
        nome_grupo = f"Turma {instance.idturma} - {instance.idcompcurricular.nmcompcurricular}"
        
        # Chama o serviço de integração
        resultado = create_telegram_group(nome_grupo)
        
        if resultado and resultado.get('status') == 'success':
            chat_id = resultado.get('chat_id')
            
            # Cria o registro do grupo no banco de dados do Django
            grupo = TelegramGroup.objects.create(
                id_telegram=chat_id,
                turma=instance,
                ativo=True
            )
            
            # Registra no log de auditoria
            TelegramAuditLog.objects.create(
                tipo='GRP',
                telegram_group=grupo,
                descricao=f"Grupo criado automaticamente via Telethon para a Turma {instance.idturma}",
                sucesso=True
            )
        else:
            # Caso falhe, apenas registramos o erro no log para não travar a criação da Turma
            print(f"Falha ao criar grupo no Telegram para a Turma {instance.idturma}")
            TelegramAuditLog.objects.create(
                tipo='GRP',
                descricao=f"Falha na criação automática do grupo para a Turma {instance.idturma}",
                sucesso=False
            )
