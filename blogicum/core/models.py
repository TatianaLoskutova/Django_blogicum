from django.db import models


class BasePublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        blank=False,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
        verbose_name='Опубликовано',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True
        ordering = ('-created_at',)
