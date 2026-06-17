from django import forms
from .models import TelegramSettings

class TelegramSettingsForm(forms.ModelForm):
    class Meta:
        model = TelegramSettings
        fields = ['bot_token']
        labels = {
            'bot_token': 'Token da API do Bot (BotFather)',
        }
        widgets = {
            'bot_token': forms.PasswordInput(render_value=True, attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500',
                'placeholder': '123456789:ABCDefghIJKLmnopQRSTuvwxyz'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(TelegramSettingsForm, self).__init__(*args, **kwargs)
        # Se houver um token, não exige que seja preenchido novamente para salvar (evita limpar o campo acidentalmente)
        if self.instance and self.instance.bot_token:
            self.fields['bot_token'].required = False
