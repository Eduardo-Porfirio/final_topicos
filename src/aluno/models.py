from django.db import models


class Aluno(models.Model):
    matricula = models.CharField(
        primary_key=True,
        max_length=20)
    
    idturma = models.ForeignKey(
        'turma.Turma',
        on_delete=models.CASCADE,
        related_name='alunos',
        null=True,
        blank=True
    )
    
    num_telefone = models.CharField(
        max_length=20,
        unique=True
    )

    nmaluno = models.CharField(
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