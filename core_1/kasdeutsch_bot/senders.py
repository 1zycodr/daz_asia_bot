from django.db.models.lookups import In
from django_tgbot.types.inlinekeyboardbutton import InlineKeyboardButton
from django_tgbot.types.inlinekeyboardmarkup import InlineKeyboardMarkup
from django_tgbot.types.keyboardbutton import KeyboardButton
from django_tgbot.types.replykeyboardmarkup import ReplyKeyboardMarkup
from django_tgbot.types.replykeyboardremove import ReplyKeyboardRemove
from django_tgbot.types.inputmedia import InputMediaPhoto
from .models import Nomination, TelegramUser, Vote, Model, Image, UserVote
from .callback_types import CallbackTypes 
from .utils import check_vote

def send_start_message(bot, chat_id):
    buttons = []
    
    for nomination in Nomination.objects.all():
        buttons.append([InlineKeyboardButton.a(
            nomination.name, 
            callback_data=CallbackTypes.set_nomination(nomination.id)
        )])

    buttons.append([InlineKeyboardButton.a(
        'О конкурсе',
        callback_data=CallbackTypes.ABOUT
    )])

    bot.sendMessage(
        chat_id,
        text='Выберите номинацию, в которой хотите проголосовать. У вас есть один голос в каждой номинации.', 
        reply_markup=InlineKeyboardMarkup.a(buttons)
    )


def send_already_voted(bot, callback_id):
    bot.answerCallbackQuery(
        callback_id, 
        text='Ваш голос за эту модель уже был учтён!'
    )


def send_unk_com_message(bot, chat_id):
    bot.sendMessage(
        chat_id, 
        text='Команда не распознана!'
    )


def send_about(bot, chat_id):
    print('ABOUT')
    bot.sendMessage(
        chat_id, 
        text="""Внимание: голосование!
Подводятся итоги фотоконкурса «Самая красивая немка Казахстана», организатором которого выступила редакция Республиканской немецкой газеты «Deutsche Allgemeine Zeitung».
Участницы конкурса: девушки из числа активистов клубов немецкой молодёжи Казахстана.
Предлагаем Вам познакомиться с фотографиями участниц и сведениями из их биографий с учетом семейных традиций, участия в общественной жизни этноса, владения немецким языком.
Голосование будет проходить с 1 по 10 июня 2021 года через Telegram-канал.
Победительница получит в награду сувенирную тарель, любезно предоставленную руководителем университетского объединения «WIUIM» д-ром Андреем Шнитковски.
Отдай свой голос!""", 
        reply_markup=InlineKeyboardMarkup.a([[InlineKeyboardButton.a('К номинациям', callback_data=CallbackTypes.START)]])
    )


def send_nomination_models(bot, chat_id, nomination_id, tg_user):
    buttons = []

    voted, user_vote = check_vote(tg_user, nomination_id)

    for vote in Vote.objects.filter(nomination_id=nomination_id):
        model_name = str(vote.model)

        if voted:
            if user_vote.model.id == vote.model.id: 
                model_name += f' ({vote.rating} проголосовавших, включая вас)'
            else:
                model_name += f' ({vote.rating} проголосовавших)'

        buttons.append([InlineKeyboardButton.a(
            model_name,
            callback_data=CallbackTypes.set_model(vote.model.id, nomination_id)
        )])

    buttons.append([InlineKeyboardButton.a(
        'О конкурсе', 
        callback_data=CallbackTypes.ABOUT
    )])

    bot.sendMessage(
        chat_id,
        text='Модели номинации "' + Nomination.objects.get(id=nomination_id).name + '":', 
        reply_markup=InlineKeyboardMarkup.a(buttons)
    )


def send_model(bot, chat_id, data, tg_user):
    buttons = []
    
    model_id, nomination_id = data 

    model = Model.objects.get(id=model_id)
    photos = Image.objects.filter(model=model)

    voted, user_vote = check_vote(tg_user, nomination_id)
    
    if len(photos) == 0:
        photo = '/media/default_photo.jpg'
    else:
        photo = photos[0].image.url

    if len(photos) > 1:
        buttons.append([InlineKeyboardButton.a(
            '>', 
            callback_data=CallbackTypes.set_next_photo(model_id, 0, nomination_id)
        )])
    
    if not voted:
        buttons.append([InlineKeyboardButton.a(
            'Проголосовать!', 
            callback_data=CallbackTypes.set_vote(model_id, 0, nomination_id)
        )])
    elif user_vote.model.id == model_id:
        buttons.append([InlineKeyboardButton.a(
            'Ваш голос за эту модель был учтён!', 
            callback_data=CallbackTypes.set_already_voted()
        )])


    buttons.append([InlineKeyboardButton.a(
        'К номинациям', 
        callback_data=CallbackTypes.START
    )])

    buttons.append([InlineKeyboardButton.a(
        'О конкурсе', 
        callback_data=CallbackTypes.ABOUT
    )])

    bot.sendMessage(
        chat_id, 
        str(model)
    )

    bot.sendPhoto(
        chat_id, 
        caption=model.description,
        photo='https://1bot.wiedergeburt.kz/' + photo, 
        reply_markup=InlineKeyboardMarkup.a(buttons)
    )


def process_next_photo(bot, chat_id, message_id, data, tg_user):
    buttons = []
    
    model_id, photo_ind, nomination_id = data
    photo_ind += 1

    model = Model.objects.get(id=model_id)
    photos = Image.objects.filter(model=model)

    photo = photos[photo_ind].image.url

    photo_buttons = [InlineKeyboardButton.a(
        '<', 
        callback_data=CallbackTypes.set_prev_photo(model_id, photo_ind, nomination_id)
    )]

    if len(photos) - 1 != photo_ind:
        photo_buttons.append(InlineKeyboardButton.a(
            '>',
            callback_data=CallbackTypes.set_next_photo(model_id, photo_ind, nomination_id)
        ))

    buttons.append(photo_buttons)
    
    voted, user_vote = check_vote(tg_user, nomination_id)

    if not voted:
        buttons.append([InlineKeyboardButton.a(
            'Проголосовать!', 
            callback_data=CallbackTypes.set_vote(model_id, photo_ind, nomination_id)
        )])
    elif user_vote.model.id == model_id:
        buttons.append([InlineKeyboardButton.a(
            'Ваш голос за эту модель был учтён!', 
            callback_data=CallbackTypes.set_already_voted()
        )])

    buttons.append([InlineKeyboardButton.a(
        'К номинациям', 
        callback_data=CallbackTypes.START
    )])
    
    buttons.append([InlineKeyboardButton.a(
        'О конкурсе', 
        callback_data=CallbackTypes.ABOUT
    )])

    bot.editMessageMedia(
        chat_id=chat_id, 
        message_id=message_id,
        media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + photo, model.description), 
        reply_markup=InlineKeyboardMarkup.a(buttons)
    )


def process_prev_photo(bot, chat_id, message_id, data, tg_user):
    buttons = []
    
    model_id, photo_ind, nomination_id = data
    photo_ind -= 1

    model = Model.objects.get(id=model_id)
    photos = Image.objects.filter(model=model)

    photo = photos[photo_ind].image.url

    photo_buttons = [InlineKeyboardButton.a(
        '>', 
        callback_data=CallbackTypes.set_next_photo(model_id, photo_ind, nomination_id)
    )]

    if photo_ind != 0:
        photo_buttons.append(InlineKeyboardButton.a(
            '<',
            callback_data=CallbackTypes.set_prev_photo(model_id, photo_ind, nomination_id)
        ))
    
    buttons.append(photo_buttons[::-1])

    voted, user_vote = check_vote(tg_user, nomination_id)

    if not voted:
        buttons.append([InlineKeyboardButton.a(
            'Проголосовать!', 
            callback_data=CallbackTypes.set_vote(model_id, photo_ind, nomination_id)
        )])
    elif user_vote.model.id == model_id:
        buttons.append([InlineKeyboardButton.a(
            'Ваш голос за эту модель был учтён!', 
            callback_data=CallbackTypes.set_already_voted()
        )])

    buttons.append([InlineKeyboardButton.a(
        'К номинациям', 
        callback_data=CallbackTypes.START
    )])
    
    buttons.append([InlineKeyboardButton.a(
        'К номинациям', 
        callback_data=CallbackTypes.ABOUT
    )])

    bot.editMessageMedia(
        chat_id=chat_id, 
        message_id=message_id,
        media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + photo, model.description), 
        reply_markup=InlineKeyboardMarkup.a(buttons)
    )


def process_vote(bot, chat_id, message_id, data, tg_user):
    buttons = []
    
    model_id, photo_ind, nomination_id = data

    model = Model.objects.get(id=model_id)
    photos = Image.objects.filter(model=model)

    photo = photos[photo_ind].image.url
    photo_buttons = []


    if photo_ind != 0:
        photo_buttons.append(InlineKeyboardButton.a(
            '<',
            callback_data=CallbackTypes.set_prev_photo(model_id, photo_ind, nomination_id)
        ))
    
    if photo_ind != len(photos) - 1:
        photo_buttons.append(InlineKeyboardButton.a(
            '>', 
            callback_data=CallbackTypes.set_next_photo(model_id, photo_ind, nomination_id)
        ))

    buttons.append(photo_buttons)
    nomination = Nomination.objects.get(id=nomination_id)

    voted, user_vote = check_vote(tg_user, nomination_id)

    if not voted:
        vote, _ = Vote.objects.get_or_create(
            model=model, 
            nomination=nomination
        )    
        vote.rating += 1
        vote.save()
        
        user_vote = UserVote.objects.create(
            tg_user=TelegramUser.objects.get(telegram_id=tg_user.telegram_id),
            nomination=nomination, 
            model=model
        )
        user_vote.save()

        buttons.append([InlineKeyboardButton.a(
            'Ваш голос за эту модель был учтён!', 
            callback_data=CallbackTypes.set_already_voted()
        )])

    else:
        buttons.append([InlineKeyboardButton.a(
            'Вы уже проголосовали за модель в этой номинации!', 
            callback_data=CallbackTypes.set_already_voted()
        )])
    

    buttons.append([InlineKeyboardButton.a(
        'К номинациям', 
        callback_data=CallbackTypes.START
    )])
    
    buttons.append([InlineKeyboardButton.a(
        'О конкурсе', 
        callback_data=CallbackTypes.ABOUT
    )])

    bot.editMessageMedia(
        chat_id=chat_id, 
        message_id=message_id,
        media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + photo, model.description), 
        reply_markup=InlineKeyboardMarkup.a(buttons)
    )