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
    preco_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    observacoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa')

    def __str__(self):
        return f"Locação - {self.cliente.nome} ({self.data_inicio})"

    def calcular_preco_total(self):
        total = sum(
            item.preco_unitario * item.quantidade
            for item in self.items.all()
        )
        self.preco_total = total
        self.save()

    def finalizar(self):
        if self.status == 'ativa':
            for item_locacao in self.items.all():
                item_locacao.item.quantidade_estoque += item_locacao.quantidade
                item_locacao.item.save()
            self.calcular_preco_total()
            self.status = 'finalizada'
            self.save()