from django.urls import path
from . import views

urlpatterns = [
    path('', views.comp_curricular_view, name='comp_curricular_view'),
    path('consultar/', views.consultar_comp_curricular_view, name='consultar_comp_curricular'),
    path('inserir/', views.inserir_comp_curricular_view, name='inserir_comp_curricular'),
]