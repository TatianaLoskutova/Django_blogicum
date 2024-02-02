from django.db import models
from django.contrib.auth import get_user_model

from core.models import BasePublishedModel

User = get_user_model()


class Category(BasePublishedModel):
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Заголовок',
    )
    description = models.TextField(blank=False, verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        blank=False,
        help_text=(
            'Идентификатор страницы для URL;'
            ' разрешены символы латиницы, цифры, дефис и подчёркивание.'
        ),
        verbose_name='Идентификатор',
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BasePublishedModel):
    name = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Название места',
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BasePublishedModel):
    title = models.CharField(
        max_length=256,
        blank=False,
        verbose_name='Заголовок',
    )
    text = models.TextField(blank=False, verbose_name='Текст')
    pub_date = models.DateTimeField(
        blank=False,
        help_text=(
            'Если установить дату и время в будущем — можно делать'
            ' отложенные публикации.'
        ),
        verbose_name='Дата и время публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField('Фото', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(blank=False, verbose_name='Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=False,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        verbose_name='Добавлено',
    )

    class Meta:
        verbose_name = 'комментарии'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text
