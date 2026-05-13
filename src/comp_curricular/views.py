from django.shortcuts import render
from django.http import HttpResponse 
from .models import ComponenteCurricular
from .models import PeriodoLetivo
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