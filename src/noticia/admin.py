from django.contrib import admin
from .models import Noticia, Atividade

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'dtnoticia', 'idturma', 'flenvio')
    list_filter = ('flenvio', 'dtnoticia', 'idturma')
    search_fields = ('titulo', 'desc_noticia')

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('nmAtividade', 'dtAtividade')
    search_fields = ('nmAtividade', 'descAtividade')
    list_filter = ('dtAtividade',)
