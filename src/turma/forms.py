from django import forms
from .models import Turma

class TurmaForm(forms.ModelForm):
    flstatus = forms.BooleanField(required=False, initial=True, label='Ativa')

    class Meta:
        model = Turma
        fields = ['idcompcurricular', 'matricula', 'flstatus']
        labels = {
            'idcompcurricular': 'Componente Curricular',
            'matricula': 'Número de Matrícula/Alunos',
        }
        widgets = {
            'idcompcurricular': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'matricula': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'flstatus': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }
