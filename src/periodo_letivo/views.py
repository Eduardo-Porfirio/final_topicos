from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def periodo_letivo_view(request):
    return HttpResponse("Período Letivo")