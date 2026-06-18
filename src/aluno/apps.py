from django.apps import AppConfig


class AlunoConfig(AppConfig):
    name = 'aluno'

    def ready(self):
        import aluno.signals
