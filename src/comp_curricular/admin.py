from django.contrib import admin
from .models import ComponenteCurricular

@admin.register(ComponenteCurricular)
class ComponenteCurricularAdmin(admin.ModelAdmin):
    list_display = ('nmcompcurricular', 'codigo', 'idperiodoletivo', 'status')
    list_filter = ('status', 'idperiodoletivo')
    search_fields = ('nmcompcurricular', 'codigo')
