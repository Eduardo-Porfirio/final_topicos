from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from periodo_letivo.models import PeriodoLetivo
from turma.models import Turma
from noticia.models import Noticia

@login_required
def dashboard_view(request):
    context = {
        'total_periodos': PeriodoLetivo.objects.count(),
        'total_turmas': Turma.objects.filter(flstatus=True).count(),
        'total_noticias': Noticia.objects.count(),
        'noticias_recentes': Noticia.objects.all().order_by('-dtnoticia')[:5],
    }
    return render(request, 'dashboard.html', context)
