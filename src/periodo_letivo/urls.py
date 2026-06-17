from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_periodos_view, name='list_periodos'),
    path('consultar/', views.consultar_periodo_letivo_view, name='consultar_periodo_letivo'),
    path('inserir/', views.inserir_periodo_letivo_view, name='inserir_periodo_letivo'),
    path('encerrar/<str:nome>/', views.encerrar_periodo_letivo_view, name='encerrar_periodo_letivo'),
    path('iniciar/<str:nome>/', views.inicia_periodo_letivo_view, name='iniciar_periodo_letivo'),
]