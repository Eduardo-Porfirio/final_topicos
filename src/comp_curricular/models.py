from django.db import models
from periodo_letivo.models import PeriodoLetivo

# Create your models here.

class ComponenteCurricular(models.Model):
    idcompcurricular = models.BigAutoField(primary_key=True)
    idperiodoletivo = models.ForeignKey(PeriodoLetivo, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=255)
    nmcompcurricular = models.CharField(max_length=255)
    status = models.BooleanField()

    class Meta:
        db_table = 'comp_curricular'