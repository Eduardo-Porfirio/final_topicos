from django.contrib import admin
from .models import Turma

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('idturma', 'idcompcurricular', 'matricula', 'flstatus')
    list_filter = ('flstatus', 'idcompcurricular')
    search_fields = ('matricula',)
