from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_comp_curricular_view, name='list_comp_curricular'),
    path('old/', views.comp_curricular_view, name='comp_curricular_view'),
    path('consultar/', views.consultar_comp_curricular_view, name='consultar_comp_curricular'),
    path('inserir/', views.inserir_comp_curricular_view, name='inserir_comp_curricular'),
]