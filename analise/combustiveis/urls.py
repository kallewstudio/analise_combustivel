from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tratar_dados/', views.upload_file, name='upload_file'),
    path('exibir_dados/<str:nome_arquivo>/', views.exibir_dados, name='exibir_dados'),
]