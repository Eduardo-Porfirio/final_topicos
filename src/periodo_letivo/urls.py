from django.urls import path
from . import views

urlpatterns = [
    path('',views.periodo_letivo_view),
    
]