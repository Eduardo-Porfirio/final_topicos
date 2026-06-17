from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import TelegramGroup, TelegramAuditLog
from django.db.models import Count
from turma.models import Turma
from comp_curricular.models import ComponenteCurricular

@login_required
def telegram_management_view(request):
    # Coletando métricas reais do banco de dados
    total_grupos = TelegramGroup.objects.count()
    grupos_ativos = TelegramGroup.objects.filter(ativo=True).count()
    
    # Contagem de mensagens enviadas via logs
    total_mensagens = TelegramAuditLog.objects.filter(tipo='MSG', sucesso=True).count()
    
    # Soma de membros em todos os grupos (conforme última sincronização)
    total_usuarios = sum(g.total_membros for g in TelegramGroup.objects.all())
    
    # Últimos logs para exibição na tela
    ultimos_logs = TelegramAuditLog.objects.all()[:5]

    context = {
        'total_grupos': total_grupos,
        'total_mensagens': total_mensagens,
        'total_usuarios': total_usuarios,
        'grupos_ativos': grupos_ativos,
        'ultimos_logs': ultimos_logs,
    }
    return render(request, 'telegram/management.html', context)

@login_required
def telegram_disparos_view(request):
    # Passando turmas e componentes para o select do mockup
    turmas = Turma.objects.all()
    componentes = ComponenteCurricular.objects.all()
    
    context = {
        'turmas': turmas,
        'componentes': componentes,
    }
    return render(request, 'telegram/disparos.html', context)
