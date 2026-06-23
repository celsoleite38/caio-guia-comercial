"""
Modelo de Avaliação para o sistema de ratings de anúncios.
Este arquivo contém o modelo Rating que será adicionado ao models.py
"""

# Adicionar este modelo ao arquivo listings/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Rating(models.Model):
    """
    Modelo para armazenar avaliações (estrelas) e comentários dos usuários
    sobre anúncios/profissionais/lojas.
    """
    listing = models.ForeignKey(
        'Listing',
        on_delete=models.CASCADE,
        related_name='ratings',
        help_text='Anúncio sendo avaliado'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings_given',
        help_text='Usuário que fez a avaliação'
    )
    stars = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Número de estrelas (1-5)'
    )
    comment = models.CharField(
        max_length=200,
        blank=True,
        help_text='Comentário opcional (até 200 caracteres)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        # Garante que cada usuário pode avaliar um anúncio apenas uma vez
        unique_together = ('listing', 'user')
        indexes = [
            models.Index(fields=['listing', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.listing.business_name} ({self.stars}⭐)'
