import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Noticia
from .forms import NoticiaForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from django.db.models import Q
from turma.models import Turma

@login_required
def list_noticias_view(request):
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    turma_filter = request.GET.get('turma', '')

    noticias = Noticia.objects.all().select_related('idturma', 'idturma__idcompcurricular').order_by('-dtnoticia')

    if search_query:
        noticias = noticias.filter(titulo__icontains=search_query)

    if status_filter:
        is_sent = status_filter == '1'
        noticias = noticias.filter(flenvio=is_sent)

    if turma_filter:
        noticias = noticias.filter(idturma_id=turma_filter)

    turmas = Turma.objects.all().select_related('idcompcurricular').order_by('idturma')

    context = {
        'noticias': noticias,
        'turmas': turmas,
        'filters': {
            'q': search_query,
            'status': status_filter,
            'turma': turma_filter,
        }
    }
    return render(request, 'noticia/list.html', context)

@login_required
def create_noticia_view(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_noticias')
    else:
        form = NoticiaForm()
    return render(request, 'noticia/form.html', {'form': form, 'title': 'Nova Notícia'})

@login_required
def edit_noticia_view(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    if request.method == 'POST':
        form = NoticiaForm(request.POST, instance=noticia)
        if form.is_valid():
            form.save()
            return redirect('list_noticias')
    else:
        form = NoticiaForm(instance=noticia)
    return render(request, 'noticia/form.html', {'form': form, 'title': 'Editar Notícia'})

@login_required
def delete_noticia_view(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    if request.method == 'POST':
        noticia.delete()
        return redirect('list_noticias')
    return render(request, 'noticia/confirm_delete.html', {'obj': noticia})

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
