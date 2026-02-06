from django.conf import settings
from django.db import models

class Board(models.Model):
    """
    KanMind board entity.
    - owner: creator of the board
    - members: users that have access to the board
    """
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="boards",
        blank=True,
    )
    class Meta:
        ordering = ["id"]
        verbose_name = "Board"
        verbose_name_plural = "Boards"
    def __str__(self):
        return self.title



