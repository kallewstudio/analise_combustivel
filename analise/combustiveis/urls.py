from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('combustiveis/', views.combustiveis, name='combustiveis'),
    path('combustiveis/produto/<str:produto>/', views.combustiveis, name='filtrar_combustivel'),
]