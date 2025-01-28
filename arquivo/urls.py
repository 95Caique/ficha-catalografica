# arquivo/urls.py
from django.urls import path
from . import views

app_name = 'arquivo'

urlpatterns = [
    # URLs definidas
    path('ficha/index', views.index_ficha, name='index_ficha'),
    path('ficha/', views.ficha, name='ficha'),
]
