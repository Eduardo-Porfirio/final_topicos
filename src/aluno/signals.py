import re
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Aluno
from telegram.models import TelegramGroup, TelegramAuditLog
from telegram.services import remove_telegram_group_member

@receiver(post_save, sender=Aluno)
def handle_aluno_status_change(sender, instance, created, **kwargs):
    """
    Sinal que detecta quando o status do aluno é alterado para inativo.
    Se inativado (flstatus=False), solicita ao microserviço Telethon a remoção dele do grupo do Telegram.
    """
    if not created:  # Executa apenas em atualizações
        if not instance.flstatus:  # Se ficou inativo
            # Busca o grupo correspondente à turma do aluno
            grupo = TelegramGroup.objects.filter(turma=instance.idturma, ativo=True).first()
            if grupo:
                # Prepara e normaliza o número do telefone com DDI +55
                phone = re.sub(r'\D', '', instance.num_telefone)
                if phone:
                    if not phone.startswith('55'):
                        phone = '55' + phone
                    phone_formatted = '+' + phone
                    
                    # Dispara a remoção
                    sucesso = remove_telegram_group_member(grupo.id_telegram, phone_formatted)
                    
                    # Registra no log de auditoria
                    TelegramAuditLog.objects.create(
                        tipo='USR',
                        telegram_group=grupo,
                        descricao=f"Aluno {instance.nmaluno} ({phone_formatted}) inativado. Remoção do grupo solicitada.",
                        sucesso=sucesso
                    )
