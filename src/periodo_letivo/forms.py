from django import forms
from .models import PeriodoLetivo

class PeriodoLetivoForm(forms.ModelForm):
    status = forms.BooleanField(required=False, initial=True, label='Ativo')

    class Meta:
        model = PeriodoLetivo
        fields = ['nmperiodo', 'dtinicial', 'dtfinal', 'status']
        labels = {
            'nmperiodo': 'Nome do Período',
            'dtinicial': 'Data de Início',
            'dtfinal': 'Data de Término',
        }
        widgets = {
            'dtinicial': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-lg'}),
            'dtfinal': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-lg'}),
            'nmperiodo': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Ex: 2026.1'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        dtinicial = cleaned_data.get('dtinicial')
        dtfinal = cleaned_data.get('dtfinal')

        if dtinicial and dtfinal and dtinicial >= dtfinal:
            self.add_error('dtfinal', "A data de término deve ser posterior à data de início.")
        
        return cleaned_data
