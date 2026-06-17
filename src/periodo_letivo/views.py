import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import PeriodoLetivo
from .forms import PeriodoLetivoForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from django.db.models import Q

@login_required
def list_periodos_view(request):
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    periodos = PeriodoLetivo.objects.all().order_by('-dtinicial')

    if search_query:
        periodos = periodos.filter(nmperiodo__icontains=search_query)

    if status_filter:
        is_active = status_filter == '1'
        periodos = periodos.filter(status=is_active)

    context = {
        'periodos': periodos,
        'filters': {
            'q': search_query,
            'status': status_filter,
        }
    }
    return render(request, 'periodo_letivo/list.html', context)

@login_required
def create_periodo_view(request):
    if request.method == 'POST':
        form = PeriodoLetivoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_periodos')
    else:
        form = PeriodoLetivoForm()
    return render(request, 'periodo_letivo/form.html', {'form': form, 'title': 'Novo Período Letivo'})

@login_required
def edit_periodo_view(request, pk):
    periodo = get_object_or_404(PeriodoLetivo, pk=pk)
    if request.method == 'POST':
        form = PeriodoLetivoForm(request.POST, instance=periodo)
        if form.is_valid():
            form.save()
            return redirect('list_periodos')
    else:
        form = PeriodoLetivoForm(instance=periodo)
    return render(request, 'periodo_letivo/form.html', {'form': form, 'title': 'Editar Período Letivo'})

@login_required
def delete_periodo_view(request, pk):
    periodo = get_object_or_404(PeriodoLetivo, pk=pk)
    if request.method == 'POST':
        periodo.delete()
        return redirect('list_periodos')
    return render(request, 'periodo_letivo/confirm_delete.html', {'obj': periodo})


def consultar_periodo_letivo_view(request):
    periodos = PeriodoLetivo.objects.filter(status=True)
    if periodos.exists():
        periodos_list = list(periodos.values())
        return JsonResponse(periodos_list, safe=False)
    else:
        return JsonResponse({"erro": "Nenhum período letivo ativo encontrado."}, status=404)
    
@csrf_exempt    
def inserir_periodo_letivo_view(request):

    if request.method == 'POST':    
        if not request.body:
            return JsonResponse({'erro': 'Corpo da requisição vazio'}, status=400)
        body = json.loads(request.body)

        if not body.get('nmperiodo') or not body.get('dtinicial') or not body.get('dtfinal'):
            return JsonResponse({'erro': 'Campos obrigatórios: nmperiodo, dtinicial, dtfinal'}, status=400)
        novo_periodo = PeriodoLetivo(
            nmperiodo=body.get('nmperiodo'),
            dtinicial=body.get('dtinicial'),
            dtfinal=body.get('dtfinal'),
            status=body.get('status', False)
        )
        novo_periodo.save()

        return JsonResponse({"message": "Período Letivo inserido com sucesso.", "id": novo_periodo.idperiodoletivo})   
    return JsonResponse({
        'erro': 'Método não permitido'}, status=405)

@csrf_exempt
def encerrar_periodo_letivo_view(request, nome):
    if request.method == 'PUT':
        if not PeriodoLetivo.objects.filter(nmperiodo=nome,status=True).exists():
            return JsonResponse({'erro': 'Período Letivo não encontrado'}, status=404)
        periodo_letivo = PeriodoLetivo.objects.get(nmperiodo=nome, status=True)
        periodo_letivo.status = False
        periodo_letivo.save()
        return JsonResponse({"message": "Período Letivo encerrado com sucesso."})
    return JsonResponse({
        'erro': 'Método não permitido'}, status=405)      

@csrf_exempt
def inicia_periodo_letivo_view(request, nome):
    if request.method == 'PUT':
        if not PeriodoLetivo.objects.filter(nmperiodo=nome,status=False).exists():
            return JsonResponse({'erro': 'Período Letivo não encontrado'}, status=404)
        periodo_letivo = PeriodoLetivo.objects.get(nmperiodo=nome, status=False)
        periodo_letivo.status = True
        periodo_letivo.save()
        return JsonResponse({"message": "Período Letivo iniciado com sucesso."})
    return JsonResponse({
        'erro': 'Método não permitido'}, status=405) 