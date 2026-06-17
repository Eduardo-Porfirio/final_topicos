import json
import urllib.request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import TelegramGroup, TelegramAuditLog, TelegramSettings
from .forms import TelegramSettingsForm
from turma.models import Turma
from comp_curricular.models import ComponenteCurricular
from noticia.models import Noticia

# ----------------- GERENCIAMENTO DA INTERFACE -----------------

@login_required
def telegram_management_view(request):
    total_grupos = TelegramGroup.objects.count()
    grupos_ativos = TelegramGroup.objects.filter(ativo=True).count()
    total_mensagens = TelegramAuditLog.objects.filter(tipo='MSG', sucesso=True).count()
    total_usuarios = sum(g.total_membros for g in TelegramGroup.objects.all())
    ultimos_logs = TelegramAuditLog.objects.all()[:5]
    
    # Verifica se o bot_token está configurado no BD ou no .env
    configuracao = TelegramSettings.get_settings()
    api_configurada = bool(configuracao.bot_token) or bool(settings.TELEGRAM_BOT_TOKEN)

    context = {
        'total_grupos': total_grupos,
        'total_mensagens': total_mensagens,
        'total_usuarios': total_usuarios,
        'grupos_ativos': grupos_ativos,
        'ultimos_logs': ultimos_logs,
        'api_configurada': api_configurada,
    }
    return render(request, 'telegram/management.html', context)

@login_required
def telegram_disparos_view(request):
    turmas = Turma.objects.all()
    componentes = ComponenteCurricular.objects.all()
    context = {'turmas': turmas, 'componentes': componentes}
    return render(request, 'telegram/disparos.html', context)

@login_required
def telegram_settings_view(request):
    # Recupera o registro Singleton
    configuracao = TelegramSettings.get_settings()
    
    if request.method == 'POST':
        form = TelegramSettingsForm(request.POST, instance=configuracao)
        if form.is_valid():
            # Lógica para não sobrescrever com string vazia se já havia token (por causa do password input)
            novo_token = form.cleaned_data.get('bot_token')
            if not novo_token and configuracao.bot_token:
                form.instance.bot_token = configuracao.bot_token
            form.save()
            messages.success(request, 'Configurações do Telegram atualizadas com sucesso!')
            return redirect('telegram_settings')
    else:
        form = TelegramSettingsForm(instance=configuracao)
    
    return render(request, 'telegram/settings.html', {'form': form})

# ----------------- INTEGRAÇÃO BOT TELEGRAM -----------------

def enviar_mensagem_telegram(chat_id, texto):
    """Função utilitária para enviar mensagem via API do Telegram"""
    # 1. Tenta pegar do banco de dados (Interface)
    configuracao = TelegramSettings.get_settings()
    token = configuracao.bot_token
    
    # 2. Fallback: Tenta pegar do .env
    if not token:
        token = settings.TELEGRAM_BOT_TOKEN
        
    if not token:
        print("Erro: Token do Telegram não configurado (nem no BD, nem no .env)")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        'chat_id': chat_id,
        'text': texto,
        'parse_mode': 'HTML'
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return response.status == 200
    except Exception as e:
        print(f"Erro na API do Telegram: {e}")
        return False

@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook_view(request):
    """
    Endpoint que receberá todas as mensagens que os alunos enviarem para o bot.
    O Telegram fará um POST nesta URL.
    """
    try:
        payload = json.loads(request.body)
        
        # Verifica se o payload contém uma mensagem
        if 'message' in payload:
            chat_id = payload['message']['chat']['id']
            texto_recebido = payload['message'].get('text', '').strip()
            
            # --- ROTEAMENTO DE COMANDOS ---
            if texto_recebido.startswith('/start'):
                resposta = "🤖 Olá! Eu sou o Assistente Acadêmico.\n\nUse o comando /noticias para ver os últimos avisos da sua turma."
                enviar_mensagem_telegram(chat_id, resposta)

            elif texto_recebido.startswith('/noticias'):
                try:
                    # 1. Identificar de qual turma é esse grupo/usuário
                    grupo = TelegramGroup.objects.get(id_telegram=chat_id, ativo=True)
                    # 2. Buscar as últimas 5 notícias da turma
                    noticias = Noticia.objects.filter(idturma=grupo.turma).order_by('-dtnoticia')[:5]
                    
                    if noticias.exists():
                        resposta = f"📰 <b>Últimas notícias de {grupo.turma.idcompcurricular.nmcompcurricular}:</b>\n\n"
                        for n in noticias:
                            resposta += f"🔸 <b>{n.titulo}</b> ({n.dtnoticia.strftime('%d/%m/%Y')})\n{n.desc_noticia}\n\n"
                    else:
                        resposta = "Não há notícias cadastradas para esta turma no momento."
                        
                except TelegramGroup.DoesNotExist:
                    resposta = "⚠️ Este chat não está vinculado a nenhuma turma no sistema."
                
                # Responde ao aluno e registra no AuditLog
                sucesso = enviar_mensagem_telegram(chat_id, resposta)
                if sucesso and 'grupo' in locals():
                    TelegramAuditLog.objects.create(
                        tipo='MSG', 
                        telegram_group=grupo, 
                        descricao=f"Comando /noticias acionado.", 
                        sucesso=True
                    )

        # O Telegram exige que sempre retornemos 200 OK, senão ele tenta reenviar
        return JsonResponse({"status": "ok"})
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return JsonResponse({"status": "error"}, status=500)
