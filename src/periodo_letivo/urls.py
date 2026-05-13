from django.urls import path
from . import views

urlpatterns = [
    path('',views.periodo_letivo_view),
    path('consultar/',views.consultar_periodo_letivo_view),
    path('inserir/',views.inserir_periodo_letivo_view),
    path('encerrar/<str:nome>/',views.encerrar_periodo_letivo_view),
    path('iniciar/<str:nome>/',views.inicia_periodo_letivo_view),
]