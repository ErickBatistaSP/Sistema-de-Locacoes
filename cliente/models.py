from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    telefone = models.CharField(max_length=15)
    bairro = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nome', 'telefone'], name='unique_cliente_nome_telefone')
        ]

    def __str__(self):
        return self.nome