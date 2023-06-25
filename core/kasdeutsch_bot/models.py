from django.db import models
from django.db.models import CASCADE
from requests.sessions import default_headers
from django.core.exceptions import ValidationError
from django_tgbot.models import AbstractTelegramUser, AbstractTelegramChat, AbstractTelegramState


def validate_image(image):
    if image.file.size > 2097152:
        raise ValidationError('Размер картинки слишком большой (> 2 МБ)')
    elif image.file.size < 51200:
        raise ValidationError('Размер картинки слишком маленький (< 50 КБ)')


class TelegramUser(AbstractTelegramUser):
    votes = models.ManyToManyField('Nomination', through='UserVote')
    first_name = models.CharField(max_length=255, db_collation='utf8mb4_general_ci')
    last_name = models.CharField(max_length=255, db_collation='utf8mb4_general_ci', blank=True, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self) -> str:
        res = super().__str__().replace('None', '').replace('(@)', '')
        res = res[:-1] + ((', ' + self.phone_number) if self.phone_number else '') + res[-1]
        return res


class UserVote(models.Model):
    tg_user = models.ForeignKey('TelegramUser', on_delete=models.CASCADE)
    nomination = models.ForeignKey('Nomination', on_delete=models.CASCADE)
    model = models.ForeignKey('Model', on_delete=models.CASCADE)
    vote_date = models.DateTimeField(verbose_name='Время голосования', auto_now_add=True, blank=True)
    
    class Meta:
        unique_together = ('tg_user', 'nomination')
        verbose_name = 'Голос'
        verbose_name_plural = 'голоса'

    def __str__(self) -> str:
        res = 'Голос #' + str(self.id)
        return res
    
    def date(self):
        return self.vote_date.strftime('%Y-%m-%d %H:%M')


class TelegramChat(AbstractTelegramChat):
    pass


class TelegramState(AbstractTelegramState):
    telegram_user = models.ForeignKey(TelegramUser, related_name='telegram_states', on_delete=CASCADE, blank=True, null=True)
    telegram_chat = models.ForeignKey(TelegramChat, related_name='telegram_states', on_delete=CASCADE, blank=True, null=True)
    request_phone_number_message_id = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        unique_together = ('telegram_user', 'telegram_chat')


class Nomination(models.Model):
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Конкурс:')

    name = models.CharField(max_length=100, verbose_name='Название', unique=True)
    description = models.TextField(default='Кандидаты номинации', verbose_name='Текст номинации')

    image = models.ImageField(verbose_name='Фото', default='demo_nomination1234.png', validators=[validate_image])

    class Meta:
        verbose_name = 'номинация'
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

    description = models.TextField(verbose_name='Биография', null=True, blank=True, max_length=1000)

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'модели'

    def __str__(self) -> str:
        show_str = f"{self.second_name + ' ' if self.second_name is not None else ''}{self.first_name}"

        if self.last_name:
            show_str += ' ' + self.last_name

        return show_str

    def fullname(self):
        return str(self)


class Competition(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    is_active = models.BooleanField(verbose_name='Активный', default=False, blank=True)    
    about = models.TextField(verbose_name='О конкурсе', default='', blank=True)
    image = models.ImageField(verbose_name='Фото', validators=[validate_image])
    image_about = models.ImageField(verbose_name='About photo', null=True, blank=False)
    class Meta:
        verbose_name = 'Конкурс'
        verbose_name_plural = 'конкурсы'

    def __str__(self) -> str:
        return f"{self.title} ({'активен' if self.is_active else 'не активен'})"

    def clean(self, *args, **kwargs):
        model = self.__class__
        if model.objects.filter(is_active=True).exists() and self.is_active and model.objects.filter(is_active=True).first() != self:
            raise ValidationError("Только один конкурс может быть активным!")
        super().clean(*args, **kwargs)


        
class Image(models.Model):
    image = models.ImageField(verbose_name='Фото', validators=[validate_image])
    model = models.ForeignKey(Model, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'изображения'

    def __str__(self) -> str:
        return f'Фото кандидата #{self.model.id}'


class BotContent(models.Model):
    about = models.CharField(verbose_name='Текст кнопки "О конкурсе"', max_length=50, default='О конкурсе')
    update = models.CharField(verbose_name='Текст кнопки "Обновить"', max_length=50, default='Обновить')
    back = models.CharField(verbose_name='Текст кнопки "Назад"', max_length=50, default='Назад')
    show_bio = models.CharField(verbose_name='Текст кнопки "Показать биографию"', max_length=50, default='Биография')
    hide_bio = models.CharField(verbose_name='Текст кнопки "Скрыть биографию"', max_length=50, default='Скрыть биографию')
    vote = models.CharField(verbose_name='Текст кнопки "Проголосовать"', max_length=50, default='Проголосовать!')
    next_photo = models.CharField(verbose_name='Текст кнопки следующей фотографии', max_length=50, default='>')
    prev_photo = models.CharField(verbose_name='Текст кнопки предыдущей фотографии', max_length=50, default='<')
    was_checked = models.CharField(verbose_name='Текст кнопки "Проголосовать", когда голос был учтён у текущей модели', max_length=50, default='Ваш голос за эту модель был учтён!')
    was_checked_in_this_nomination = models.CharField(verbose_name='Текст кнопки "Проголосовать", когда голос был учтён у другой модели в этой категории', max_length=50, default='Вы уже проголосовали за модель в этой номинации!')
    chose_nomination = models.CharField(verbose_name='Текст меню выбора номинации', max_length=255, default='Выберите номинацию, в которой хотите проголосовать. У вас есть один голос в каждой номинации.')
    no_competition = models.CharField(verbose_name='Текст меню когда конкурс отсутствует', max_length=255, default='Нет активных конкурсов.')
    update_menu = models.CharField(verbose_name='Текст меню обновления конкурса', max_length=255, default='Пожалуйста, обновите информацию о конкурсе!')
    already_voted = models.CharField(verbose_name='Текст всплывающего окна, когда голос учтён', max_length=255, default='Ваш голос уже был учтён!')
    votes = models.CharField(verbose_name='Текст кандидата когда человек проголосовал', max_length=255, default='голосов')
    votess = models.CharField(verbose_name='Текст кандидата когда человек проголосовал, включая его голос', max_length=255, default='голосов, включая ваш')
    candidates = models.CharField(verbose_name='Текст меню списка кандидатов', max_length=255, default='Кандидаты номинации')
    send_contact_text = models.CharField(verbose_name='Текст всплывающего окна запроса номера телефона', max_length=255, default='Вы должны отправить свой контакт перед голосованием!')
    share_contact = models.CharField(verbose_name='Текст кнопки "Поделиться контактом"', max_length=255, default='Поделиться контактом')
    no_competition_image = models.ImageField(verbose_name='Фото для сообщения "Нет соревнования"', validators=[validate_image])
    update_menu_image = models.ImageField(verbose_name='Фото для меню обновления конкурса', validators=[validate_image])
    default_model_photo = models.ImageField(verbose_name='Дефолтное фото кандидата', validators=[validate_image])

    class Meta:
        verbose_name = 'Настройки'
        verbose_name_plural = 'настройки'

    def __str__(self) -> str:
        return 'Настройки'
