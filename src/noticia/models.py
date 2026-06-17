from django.db import models

# Create your models here.


class Noticia(models.Model):
    idnoticia = models.AutoField(primary_key=True)
    dtnoticia = models.DateField()
    titulo = models.CharField(max_length=255)
    desc_noticia = models.TextField()
    flenvio = models.BooleanField(default=False)
    # Relacionamento com Turma (conforme diagrama "gerar")
    idturma = models.ForeignKey('turma.Turma', on_delete=models.CASCADE, db_column='idturma')

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = "noticia"


class Atividade(models.Model):
    idAtividade = models.AutoField(primary_key=True)
    nmAtividade = models.CharField(max_length=255)
    descAtividade = models.TextField()
    dtAtividade = models.DateField()

    def __str__(self):
        return self.nmAtividade

    class Meta:
        db_table = "atividade"
