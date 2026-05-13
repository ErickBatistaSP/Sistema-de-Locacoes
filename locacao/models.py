from django.db import models
from cliente.models import Cliente

class Locacao(models.Model):
    STATUS_CHOICES = (
        ('ativa', 'Ativa'),
        ('finalizada', 'Finalizada'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    preco_total = models.DecimalField(max_digits=10, decimal_places=2, default=None, null= True, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa')

    # Endereço de entrega
    endereco_rua = models.CharField(max_length=200, blank=True, null=True)
    endereco_numero = models.CharField(max_length=20, blank=True, null=True)
    endereco_bairro = models.CharField(max_length=100, blank=True, null=True)
    endereco_referencia = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Locação - {self.cliente.nome} ({self.data_inicio})"

    def finalizar(self):
        if self.status == 'ativa':
            # Devolve estoque dos itens individuais
            for item_locacao in self.items.all():
                item_locacao.item.quantidade_estoque += item_locacao.quantidade
                item_locacao.item.save()
            # Devolve estoque dos combos
            for combo_locacao in self.combos.all():
                combo_locacao.devolver_estoque()
            self.status = 'finalizada'
            self.save()