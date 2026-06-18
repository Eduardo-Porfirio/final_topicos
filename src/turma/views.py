from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Turma
from .forms import TurmaForm

from django.db.models import Q
from comp_curricular.models import ComponenteCurricular

@login_required
def list_turmas_view(request):
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    comp_filter = request.GET.get('componente', '')

    turmas = Turma.objects.all().select_related('idcompcurricular')

    if search_query:
        # Busca por matrícula ou nome do componente
        turmas = turmas.filter(
            Q(matricula__icontains=search_query) | 
            Q(idcompcurricular__nmcompcurricular__icontains=search_query)
        )

    if status_filter:
        is_active = status_filter == '1'
        turmas = turmas.filter(flstatus=is_active)

    if comp_filter:
        turmas = turmas.filter(idcompcurricular_id=comp_filter)

    componentes = ComponenteCurricular.objects.all().order_by('nmcompcurricular')

    context = {
        'turmas': turmas,
        'componentes': componentes,
        'filters': {
            'q': search_query,
            'status': status_filter,
            'componente': comp_filter,
        }
    }
    return render(request, 'turma/list.html', context)

@login_required
def create_turma_view(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_turmas')
    else:
        form = TurmaForm()
    return render(request, 'turma/form.html', {'form': form, 'title': 'Nova Turma'})

@login_required
def edit_turma_view(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            form.save()
            return redirect('list_turmas')
    else:
        form = TurmaForm(instance=turma)
    return render(request, 'turma/form.html', {'form': form, 'title': 'Editar Turma'})

@login_required
def delete_turma_view(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    if request.method == 'POST':
        turma.delete()
        return redirect('list_turmas')
    return render(request, 'turma/confirm_delete.html', {'obj': turma})

@login_required
def list_alunos_by_turma_view(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    alunos = turma.alunos.all()
    context = {
        'turma': turma,
        'alunos': alunos
    }
    return render(request, 'turma/alunos_list.html', context)
