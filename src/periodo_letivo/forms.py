from django import forms
from .models import PeriodoLetivo

class PeriodoLetivoForm(forms.ModelForm):
    class Meta:
        model = PeriodoLetivo
        fields = ['nmperiodo', 'dtinicial', 'dtfinal', 'status']
        labels = {
            'nmperiodo': 'Nome do Período',
            'dtinicial': 'Data de Início',
            'dtfinal': 'Data de Término',
            'status': 'Ativo',
        }
        widgets = {
            'dtinicial': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-lg'}),
            'dtfinal': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-lg'}),
            'nmperiodo': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Ex: 2026.1'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }
