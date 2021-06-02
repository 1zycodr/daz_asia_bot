from django_tgbot.types.inlinekeyboardbutton import InlineKeyboardButton
from django_tgbot.types.inlinekeyboardmarkup import InlineKeyboardMarkup
from django_tgbot.types.keyboardbutton import KeyboardButton
from django_tgbot.types.replykeyboardmarkup import ReplyKeyboardMarkup
from django_tgbot.types.replykeyboardremove import ReplyKeyboardRemove
from .models import Nomination, Vote
from .callback_types import CallbackTypes 

def send_start_message(bot, chat_id):
    buttons = []
    
    for nomination in Nomination.objects.all():
        buttons.append([InlineKeyboardButton.a(
            nomination.name, 
            callback_data=CallbackTypes.set_nomination(nomination.id)
        )])

    bot.sendMessage(
        chat_id,
        text='Выберите номинацию, в которой хотите проголосовать. У вас есть один голос.', 
        reply_markup=InlineKeyboardMarkup.a(buttons)
    )


def send_unk_com_message(bot, chat_id):
    bot.sendMessage(
        chat_id, 
        text='Команда не распознана!'
    )


def send_nomination_models(bot, chat_id, nomination_id, voted):
    models_buttons = []

    for vote in Vote.objects.filter(nomination_id=nomination_id):
        model_name = str(vote.model)

        if voted: 
            model_name += f' ({vote.rating} проголосовавших)'

        models_buttons.append([InlineKeyboardButton.a(
            model_name,
            callback_data=CallbackTypes.set_model(vote.model.id)
        )])

    bot.sendMessage(
        chat_id,
        text='Модели номинации ' + Nomination.objects.get(id=nomination_id).name, 
        reply_markup=InlineKeyboardMarkup.a(models_buttons)
    )