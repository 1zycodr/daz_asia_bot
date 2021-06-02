from django.db import models
from django.db.models import CASCADE

from django_tgbot.models import AbstractTelegramUser, AbstractTelegramChat, AbstractTelegramState


class TelegramUser(AbstractTelegramUser):
    voted = models.BooleanField(verbose_name='Проголосовал', default=False, blank=True)


class TelegramChat(AbstractTelegramChat):
    pass


class TelegramState(AbstractTelegramState):
    telegram_user = models.ForeignKey(TelegramUser, related_name='telegram_states', on_delete=CASCADE, blank=True, null=True)
    telegram_chat = models.ForeignKey(TelegramChat, related_name='telegram_states', on_delete=CASCADE, blank=True, null=True)

    class Meta:
        unique_together = ('telegram_user', 'telegram_chat')


class Nomination(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название', unique=True)

    class Meta:
        verbose_name = 'номинацию'
        verbose_name_plural = 'номинации'
    
    def __str__(self) -> str:
        return self.name

    def get_votes(self):
        votes = Vote.objects.filter(nomination=self)
        votes = ['#' + str(vote.model) for vote in votes]
        return "\n".join(votes)


class Vote(models.Model):
    model = models.ForeignKey('Model', on_delete=models.CASCADE, verbose_name='Модель')
    nomination = models.ForeignKey(Nomination, on_delete=models.CASCADE, verbose_name='Номинация')
    rating = models.IntegerField(default=0, blank=True, verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Голосование'
        verbose_name_plural = 'голосования'
        ordering = ['-rating']

    def __str__(self) -> str:
        return self.nomination.name


class Model(models.Model):
    # nominations = models.ManyToManyField(Nomination, verbose_name='Номинации')
    nominations = models.ManyToManyField(Nomination, through='Vote', verbose_name='Номинации')
    
    first_name = models.CharField(max_length=200, verbose_name='Имя')
    second_name = models.CharField(max_length=200, verbose_name='Фамилия', null=True, blank=True)
    last_name = models.CharField(max_length=200, verbose_name='Отчество', null=True, blank=True)

    description = models.TextField(verbose_name='Биография', null=True, blank=True)

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'модели'

    def __str__(self) -> str:
        show_str = f'#{self.id} {self.first_name}'

        if self.second_name:
            show_str += ' ' + self.second_name
        
        if self.last_name:
            show_str += ' ' + self.last_name

        return show_str


class Image(models.Model):
    image = models.ImageField(verbose_name='Фото')
    model = models.ForeignKey(Model, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'изображения'

    def __str__(self) -> str:
        return f'Фото модели #{self.model.id}'