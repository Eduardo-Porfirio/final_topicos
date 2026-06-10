from django.contrib import admin
from .models import PeriodoLetivo

@admin.register(PeriodoLetivo)
class PeriodoLetivoAdmin(admin.ModelAdmin):
    list_display = ('nmperiodo', 'dtinicial', 'dtfinal', 'status')
    list_filter = ('status',)
    search_fields = ('nmperiodo',)
