from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import ComponenteCurricular
from .models import PeriodoLetivo
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required

@login_required
def list_comp_curricular_view(request):
    componentes = ComponenteCurricular.objects.all().select_related('idperiodoletivo')
    return render(request, 'comp_curricular/list.html', {'componentes': componentes})

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