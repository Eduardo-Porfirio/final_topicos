from django.db import models

class Turma(models.Model):
    idturma = models.AutoField(primary_key=True)
    # Relacionamento com Componente Curricular (conforme diagrama)
    idcompcurricular = models.ForeignKey('comp_curricular.ComponenteCurricular', on_delete=models.CASCADE, db_column='idcompcurricular')
    # Relacionamento com Aluno (representado por matricula no diagrama)
    # Nota: Assumindo que existirá um modelo Aluno. Por enquanto, usaremos IntegerField se não estiver definido.
    matricula = models.IntegerField() 
    flstatus = models.BooleanField(default=True)

    def __str__(self):
        return f"Turma {self.idturma} - {self.idcompcurricular.nmcompcurricular}"

    class Meta:
        db_table = 'turma'
