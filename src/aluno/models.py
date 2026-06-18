from django.db import models


class Aluno(models.Model):
    matricula = models.CharField(
        primary_key=True,
        max_length=20)

    num_telefone = models.CharField(
        max_length=20,
        unique=True
    )

    flstatus = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = 'aluno'

    def __str__(self):
        return self.matricula