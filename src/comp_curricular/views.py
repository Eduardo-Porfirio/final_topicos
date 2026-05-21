from django.shortcuts import render
from django.http import HttpResponse 
from .models import ComponenteCurricular
from .models import PeriodoLetivo
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.

def comp_curricular_view(request):
    return HttpResponse('Componente Curricular!')

def consultar_comp_curricular_view(request):
    if request.method == 'GET':
        periodo_ativo = PeriodoLetivo.objects.filter(status=True).first()
        print("Período Ativo: ", periodo_ativo)
        if not periodo_ativo:
            return HttpResponse("Nenhum período letivo ativo encontrado.")
        componentes = ComponenteCurricular.objects.filter(idperiodoletivo=periodo_ativo.idperiodoletivo)
        if not componentes:            
            return HttpResponse("Nenhum componente curricular encontrado para o período letivo ativo.")
        componentes_list = list(componentes.values())
        return HttpResponse(f"Componentes Curriculares para o período letivo ativo: {componentes_list}")
    return HttpResponse("Método não permitido.", status=405)

@csrf_exempt
def inserir_comp_curricular_view(request):
    if request.method == 'POST':
        comp_curricular = json.loads(request.body)
        print("Componente Curricular recebido: ", comp_curricular)
        for item in comp_curricular:
            if not item.get('idperiodoletivo') or not item.get('codigo') or not item.get('nmcompcurricular'):
                return HttpResponse("Campos obrigatórios: idperiodoletivo, codigo, nmcompcurricular", status=400)
            novo_comp_curricular = ComponenteCurricular(
                idperiodoletivo_id=item.get('idperiodoletivo'),
                codigo=item.get('codigo'),
                nmcompcurricular=item.get('nmcompcurricular'),
                status=item.get('status', False)
            )
            #novo_comp_curricular.save()
        return HttpResponse("Componente Curricular inserido com sucesso.")
    return HttpResponse("Método não permitido.", status=405)