from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'bairro', 'endereco']
    search_fields = ['nome', 'bairro']
    ordering = ['nome']