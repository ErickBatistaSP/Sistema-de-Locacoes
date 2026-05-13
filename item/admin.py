from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['get_tipo_display_col', 'quantidade_estoque']
    search_fields = ['tipo']
    list_filter = ['tipo']
    ordering = ['tipo']

    def get_tipo_display_col(self, obj):
        return obj.get_tipo_display()
    get_tipo_display_col.short_description = 'Tipo'