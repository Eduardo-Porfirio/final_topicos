from django.apps import AppConfig


class TurmaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'turma'

    def ready(self):
        # Desativado para evitar criação automática excessiva e problemas com fixtures
        # import turma.signals
        pass
