from django.contrib import admin
from .models import Combo, ComboItem

class ComboItemInline(admin.TabularInline):
    model = ComboItem
    extra = 1

@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    inlines = [ComboItemInline]
