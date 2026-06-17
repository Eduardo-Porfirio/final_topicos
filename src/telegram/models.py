from django.db import models
from turma.models import Turma

class TelegramGroup(models.Model):
    """
    Representa a conexão entre uma Turma do sistema e um grupo real no Telegram.
    """
    id_telegram = models.BigIntegerField(unique=True, help_text="ID interno do chat/grupo no Telegram")
    turma = models.OneToOneField(Turma, on_delete=models.CASCADE, related_name='telegram_group')
    link_convite = models.URLField(max_length=500, blank=True, null=True)
    total_membros = models.IntegerField(default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Grupo Telegram - {self.turma.idcompcurricular.nmcompcurricular}"

    class Meta:
        verbose_name = "Grupo Telegram"
        verbose_name_plural = "Grupos Telegram"

class TelegramAuditLog(models.Model):
    """
    Registra o histórico de interações e envios para auditoria e métricas.
    """
    TIPO_EVENTO = [
        ('MSG', 'Envio de Mensagem'),
        ('GRP', 'Criação de Grupo'),
        ('USR', 'Entrada de Usuário'),
    ]

    tipo = models.CharField(max_length=3, choices=TIPO_EVENTO)
    telegram_group = models.ForeignKey(TelegramGroup, on_delete=models.SET_NULL, null=True, related_name='logs')
    descricao = models.TextField()
    data_evento = models.DateTimeField(auto_now_add=True)
    sucesso = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.data_evento.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Log do Telegram"
        verbose_name_plural = "Logs do Telegram"
        ordering = ['-data_evento']
