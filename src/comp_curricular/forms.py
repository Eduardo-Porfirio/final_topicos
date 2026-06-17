from django import forms
from .models import ComponenteCurricular

class ComponenteCurricularForm(forms.ModelForm):
    status = forms.BooleanField(required=False, initial=True, label='Ativo')

    class Meta:
        model = ComponenteCurricular
        fields = ['idperiodoletivo', 'codigo', 'nmcompcurricular', 'status']
        labels = {
            'idperiodoletivo': 'Período Letivo',
            'codigo': 'Código da Disciplina',
            'nmcompcurricular': 'Nome do Componente',
        }
        widgets = {
            'idperiodoletivo': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'codigo': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Ex: DCC001'}),
            'nmcompcurricular': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'placeholder': 'Ex: Banco de Dados'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }
