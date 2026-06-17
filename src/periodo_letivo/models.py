from django.db import models


class PeriodoLetivo(models.Model):
    idperiodoletivo = models.BigAutoField(primary_key=True)
    nmperiodo = models.CharField(max_length=255)
    dtinicial = models.DateField()
    dtfinal = models.DateField()
    status = models.BooleanField()

    def __str__(self):
        return self.nmperiodo

    class Meta:
        db_table = 'periodo_letivo'