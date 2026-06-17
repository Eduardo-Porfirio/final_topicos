from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Turma

@login_required
def list_turmas_view(request):
    turmas = Turma.objects.all().select_related('idcompcurricular')
    return render(request, 'turma/list.html', {'turmas': turmas})
