import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Noticia

@require_http_methods(["GET"])
def consultar_todas_noticias(request):
    noticias = list(Noticia.objects.all().values())
    if not noticias:
        return JsonResponse([], safe=False, status=200)
    return JsonResponse(noticias, safe=False, status=200)

@require_http_methods(["GET"])
def consultar_noticia_por_turma(request, id):
    # Nota: No diagrama, a busca seria por idturma. 
    # Aqui mantive a lógica de buscar por ID da notícia conforme seu código anterior, 
    # mas ajustado para o novo nome do campo idnoticia.
    try:
        noticia = list(Noticia.objects.filter(idnoticia=id).values())
        if not noticia:
             return JsonResponse({"erro": "Notícia não encontrada."}, status=404)
        return JsonResponse(noticia[0], safe=False, status=200)
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)

@csrf_exempt
@require_http_methods(['POST'])
def cadastrar_noticia_view(request):
    try:
        data = json.loads(request.body)
        
        nova_noticia = Noticia.objects.create(
            dtnoticia=data.get('dtnoticia'),
            titulo=data.get('titulo'),
            desc_noticia=data.get('desc_noticia'),
            flenvio=data.get('flenvio', False),
            idturma_id=data.get('idturma')
        )
        
        return JsonResponse({
            "mensagem": "Notícia cadastrada com sucesso!",
            "id": nova_noticia.idnoticia
        }, status=201)
        
    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)
