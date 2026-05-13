from django.db import models
from item.models import Item
from locacao.models import Locacao

class Combo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nome

class ComboItem(models.Model):
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, related_name='itens')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantidade = models.IntegerField()

    def __str__(self):
        return f"{self.combo.nome} - {self.item.get_tipo_display()} x{self.quantidade}"

class ComboLocacao(models.Model):
    locacao = models.ForeignKey(Locacao, on_delete=models.CASCADE, related_name='combos')
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE)
    quantidade = models.IntegerField()

    def __str__(self):
        return f"{self.combo.nome} x{self.quantidade}"

    def descontar_estoque(self):
        for combo_item in self.combo.itens.all():
            combo_item.item.quantidade_estoque -= combo_item.quantidade * self.quantidade
            combo_item.item.save()

    def devolver_estoque(self):
        for combo_item in self.combo.itens.all():
            combo_item.item.quantidade_estoque += combo_item.quantidade * self.quantidade
            combo_item.item.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.descontar_estoque()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.locacao.status == 'ativa':
            self.devolver_estoque()
        super().delete(*args, **kwargs)