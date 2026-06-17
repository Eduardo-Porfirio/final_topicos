from django import forms
from .models import Noticia

class NoticiaForm(forms.ModelForm):
    flenvio = forms.BooleanField(required=False, initial=False, label='Já Enviada?')

    class Meta:
        model = Noticia
        fields = ['dtnoticia', 'titulo', 'desc_noticia', 'flenvio', 'idturma']
        labels = {
            'dtnoticia': 'Data da Notícia',
            'titulo': 'Título',
            'desc_noticia': 'Conteúdo/Descrição',
            'idturma': 'Turma Alvo',
        }
        widgets = {
            'dtnoticia': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-lg'}),
            'titulo': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'desc_noticia': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg', 'rows': 4}),
            'idturma': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'flenvio': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }
