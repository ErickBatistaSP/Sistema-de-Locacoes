from django.db import models

class Item(models.Model):
    TIPO_CHOICES = (
        ('cadeira', 'Cadeira'),
        ('mesa', 'Mesa'),
        ('pula_pula-pequeno', 'Pula Pula-pequeno'),
        ('piscina_bolinha', 'Piscina de Bolinha'),
        ('pula_pula-grande', 'Pula Pula-grande'),
    )

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    quantidade_estoque = models.IntegerField()

    def __str__(self):
        return f"{self.get_tipo_display()} ({self.quantidade_estoque} disponíveis)"
