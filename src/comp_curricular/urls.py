from django.urls import path
from . import views

urlpatterns = [
    path('',views.comp_curricular_view),
    path('consultar/',views.consultar_comp_curricular_view),
]