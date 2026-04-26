from django.contrib import admin
from .models import Locacao
from itemlocacao.models import ItemLocacao

class ItemLocacaoInline(admin.TabularInline):
    model = ItemLocacao
    extra = 1

    def save_new(self, form, commit=True):
        return form.save(commit=commit)

    def save_existing(self, form, instance, commit=True):
        return form.save(commit=commit)

    def delete_queryset(self, request, queryset):
        for item_locacao in queryset:
            if item_locacao.locacao.status == 'ativa':
                item_locacao.item.quantidade_estoque += item_locacao.quantidade
                item_locacao.item.save()
        queryset.delete()

@admin.register(Locacao)
class LocacaoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'data_inicio', 'data_fim', 'preco_total', 'status']
    list_filter = ['status', 'data_inicio']
    search_fields = ['cliente__nome']
    ordering = ['-data_inicio']
    inlines = [ItemLocacaoInline]
    autocomplete_fields = ['cliente']
    readonly_fields = ['preco_total']  # não deixa editar manualmente
    actions = ['finalizar_locacoes']

    def save_related(self, request, form, formsets, change):
        # Salva os itens e depois recalcula o preço total
        super().save_related(request, form, formsets, change)
        form.instance.calcular_preco_total()

    def finalizar_locacoes(self, request, queryset):
        for locacao in queryset:
            locacao.finalizar()
        self.message_user(request, "Locações finalizadas e estoque devolvido!")
    finalizar_locacoes.short_description = "Finalizar locações selecionadas"