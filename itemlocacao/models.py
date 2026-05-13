from django.db import models
from django.core.exceptions import ValidationError
from item.models import Item
from locacao.models import Locacao

class ItemLocacao(models.Model):
    locacao = models.ForeignKey(Locacao, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.item.get_tipo_display()} - {self.quantidade}"

    def clean(self):
        # Bloqueia edição se locação já finalizada
        if self.locacao.status == 'finalizada':
            raise ValidationError("Não é possível editar itens de uma locação já finalizada.")

        # Se quantidade não foi informada, deixa o form do views.py tratar
        if not self.quantidade or not self.item_id:
            return

        # Valida estoque disponível
        if self.pk:
            anterior = ItemLocacao.objects.get(pk=self.pk)
            disponivel = self.item.quantidade_estoque + anterior.quantidade
        else:
            disponivel = self.item.quantidade_estoque

        if self.quantidade > disponivel:
            raise ValidationError(
                f"Estoque insuficiente! Disponível: {disponivel} unidade(s) de {self.item.get_tipo_display()}."
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # roda o clean() antes de salvar
        if not self.pk:
            self.item.quantidade_estoque -= self.quantidade
            self.item.save()
        else:
            anterior = ItemLocacao.objects.get(pk=self.pk)
            diferenca = self.quantidade - anterior.quantidade
            self.item.quantidade_estoque -= diferenca
            self.item.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Só devolve estoque se locação ainda ativa
        if self.locacao.status == 'ativa':
            self.item.quantidade_estoque += self.quantidade
            self.item.save()
        super().delete(*args, **kwargs)