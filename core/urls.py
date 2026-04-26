from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Clientes
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/novo/', views.cliente_criar, name='cliente_criar'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path('clientes/<int:pk>/deletar/', views.cliente_deletar, name='cliente_deletar'),

    # Itens
    path('itens/', views.itens_list, name='itens_list'),
    path('itens/novo/', views.item_criar, name='item_criar'),
    path('itens/<int:pk>/editar/', views.item_editar, name='item_editar'),
    path('itens/<int:pk>/deletar/', views.item_deletar, name='item_deletar'),

    # Locações
    path('locacoes/', views.locacoes_list, name='locacoes_list'),
    path('locacoes/nova/', views.locacao_criar, name='locacao_criar'),
    path('locacoes/<int:pk>/', views.locacao_detalhe, name='locacao_detalhe'),
    path('locacoes/<int:pk>/editar/', views.locacao_editar, name='locacao_editar'),
    path('locacoes/<int:pk>/finalizar/', views.locacao_finalizar, name='locacao_finalizar'),
]
