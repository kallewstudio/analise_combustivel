from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tratar_dados/', views.upload_file, name='upload_file'),
    path('filtrar_dados/', views.filtrar_dados, name='filtrar_dados'),
]
