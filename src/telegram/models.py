from django.db import models
from django.core.exceptions import ValidationError
from turma.models import Turma

class TelegramSettings(models.Model):
    """
    Modelo Singleton para armazenar configurações globais da API do Telegram.
    Sempre existirá apenas 1 registro desta tabela.
    """
    bot_token = models.CharField(max_length=255, blank=True, null=True, help_text="Token da API fornecido pelo BotFather")
    data_atualizacao = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and TelegramSettings.objects.exists():
            # Se já existir um registro e estamos tentando criar um novo, atualiza o existente
            return TelegramSettings.objects.first().save(*args, **kwargs)
        super(TelegramSettings, self).save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configurações da API do Telegram"

    class Meta:
        verbose_name = "Configuração do Telegram"
        verbose_name_plural = "Configurações do Telegram"

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
