from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ComponenteCurricular
from .forms import ComponenteCurricularForm
from django.contrib.auth.decorators import login_required
import json

from django.db.models import Q
from periodo_letivo.models import PeriodoLetivo

from django.core.paginator import Paginator

@login_required
def list_comp_curricular_view(request):
    # Captura parâmetros da URL
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    periodo_filter = request.GET.get('periodo', '')

    # Inicia o queryset base
    componentes_qs = ComponenteCurricular.objects.all().select_related('idperiodoletivo')

    # Aplica busca textual (Nome ou Código)
    if search_query:
        componentes_qs = componentes_qs.filter(
            Q(nmcompcurricular__icontains=search_query) | 
            Q(codigo__icontains=search_query)
        )

    # Aplica filtro de status
    if status_filter:
        is_active = status_filter == '1'
        componentes_qs = componentes_qs.filter(status=is_active)

    # Aplica filtro de período
    if periodo_filter:
        componentes_qs = componentes_qs.filter(idperiodoletivo_id=periodo_filter)

    # Dados para popular os filtros no template
    periodos = PeriodoLetivo.objects.all().order_by('-dtinicial')

    paginator = Paginator(componentes_qs, 5)
    page_number = request.GET.get('page')
    componentes = paginator.get_page(page_number)

    context = {
        'componentes': componentes,
        'periodos': periodos,
        'filters': {
            'q': search_query,
            'status': status_filter,
            'periodo': periodo_filter,
        }
    }
    return render(request, 'comp_curricular/list.html', context)

@login_required
def create_comp_curricular_view(request):
    if request.method == 'POST':
        form = ComponenteCurricularForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_comp_curricular')
    else:
        form = ComponenteCurricularForm()
    return render(request, 'comp_curricular/form.html', {'form': form, 'title': 'Novo Componente Curricular'})

@login_required
def edit_comp_curricular_view(request, pk):
    comp = get_object_or_404(ComponenteCurricular, pk=pk)
    if request.method == 'POST':
        form = ComponenteCurricularForm(request.POST, instance=comp)
        if form.is_valid():
            form.save()
            return redirect('list_comp_curricular')
    else:
        form = ComponenteCurricularForm(instance=comp)
    return render(request, 'comp_curricular/form.html', {'form': form, 'title': 'Editar Componente'})

@login_required
def delete_comp_curricular_view(request, pk):
    comp = get_object_or_404(ComponenteCurricular, pk=pk)
    if request.method == 'POST':
        comp.delete()
        return redirect('list_comp_curricular')
    return render(request, 'comp_curricular/confirm_delete.html', {'obj': comp})

def comp_curricular_view(request):
    return HttpResponse('Componente Curricular!')

def consultar_comp_curricular_view(request):
    if request.method == 'GET':
        periodo_ativo = PeriodoLetivo.objects.filter(status=True).first()
        if not periodo_ativo:
            return JsonResponse({"erro": "Nenhum período letivo ativo encontrado."}, status=404)

        componentes = ComponenteCurricular.objects.filter(idperiodoletivo=periodo_ativo.idperiodoletivo)
        if not componentes:            
            return JsonResponse([], safe=False)

        componentes_list = list(componentes.values())
        return JsonResponse(componentes_list, safe=False)
    return JsonResponse({"erro": "Método não permitido."}, status=405)

@csrf_exempt
def inserir_comp_curricular_view(request):
    if request.method == 'POST':
        try:
            comp_curricular_data = json.loads(request.body)
            # Garantir que tratamos tanto um único objeto quanto uma lista
            if isinstance(comp_curricular_data, dict):
                comp_curricular_data = [comp_curricular_data]

            ids_criados = []
            for item in comp_curricular_data:
                if not item.get('idperiodoletivo') or not item.get('codigo') or not item.get('nmcompcurricular'):
                    return JsonResponse({"erro": "Campos obrigatórios: idperiodoletivo, codigo, nmcompcurricular"}, status=400)

                novo_comp_curricular = ComponenteCurricular(
                    idperiodoletivo_id=item.get('idperiodoletivo'),
                    codigo=item.get('codigo'),
                    nmcompcurricular=item.get('nmcompcurricular'),
                    status=item.get('status', False)
                )
                novo_comp_curricular.save()
                ids_criados.append(novo_comp_curricular.idcompcurricular)

            return JsonResponse({"mensagem": "Componente(s) Curricular(es) inserido(s) com sucesso.", "ids": ids_criados}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"erro": "JSON inválido."}, status=400)
    return JsonResponse({"erro": "Método não permitido."}, status=405)