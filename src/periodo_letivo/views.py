import json
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import PeriodoLetivo
from django.views.decorators.csrf import csrf_exempt



# Create your views here.
def periodo_letivo_view(request):
    return HttpResponse("Período Letivo")


def consultar_periodo_letivo_view(request):
    periodo_letivo = PeriodoLetivo.objects.filter(status = True)
    periodo_letivo = list(periodo_letivo.values())
    if periodo_letivo:
        return HttpResponse(f"Período Letivo: {periodo_letivo[0]['nmperiodo']}")
    else:
        return HttpResponse("Nenhum período letivo encontrado.")
    
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