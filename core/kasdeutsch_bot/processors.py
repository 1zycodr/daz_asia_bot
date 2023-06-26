from django_tgbot.decorators import processor
from django_tgbot.state_manager import message_types, update_types, state_types
from django_tgbot.types.update import Update
from django_tgbot.types.message import Message
from .bot import state_manager
from .models import TelegramChat, TelegramState, TelegramUser
from .bot import TelegramBot
from .senders import send_start_message, send_unk_com_message, \
    send_nomination_models, send_model, process_next_photo, \
    process_prev_photo, send_already_voted, process_vote, \
    send_about, process_biography   
from .callback_types import CallbackTypes

state_manager.set_default_update_types(update_types.Message)

available_options = {
    '/start': send_start_message
}


def dispatch(bot: TelegramBot, message: Message, chat_id, tg_user):
    if message.type() == message_types.Contact:
        if tg_user is not None:
            if message.contact.user_id == tg_user.telegram_id:
                tg_user.phone_number = message.contact.get_phone_number()
                tg_user.save()
        try:
            bot.deleteMessage(chat_id, message.reply_to_message.message_id)
        except AttributeError:
            try:
                bot.deleteMessage(chat_id, TelegramState.objects.get(
                    telegram_user=tg_user,
                    telegram_chat=TelegramChat.objects.get(telegram_id=chat_id)
                ).request_phone_number_message_id)
            except (TelegramState.DoesNotExist, TelegramChat.DoesNotExist):
                print('Error')

    try:
        available_options[message.get_text()](bot, chat_id, message.get_message_id())
    except KeyError:
        send_unk_com_message(bot, chat_id, message.get_message_id())


def dispatch_callback(bot: TelegramBot, callback, chat_id, tg_user):
    callback_data = callback.get_data()
    
    if callback_data is None:
        bot.answerCallbackQuery(callback.get_id(), 'Invalid callback!')
        return

    callback_type, callback_answ_data, err = CallbackTypes.get_type(callback_data)

    if err is None: 
        if callback_type == CallbackTypes.NOMINATION:
            send_nomination_models(bot, chat_id, callback.get_message().get_message_id(),\
                callback_answ_data, tg_user)
        elif callback_type == CallbackTypes.MODEL:
            send_model(bot, chat_id, callback.get_message().get_message_id(),\
                callback_answ_data, tg_user)
        elif callback_type == CallbackTypes.START: 
            send_start_message(bot, chat_id, callback.get_message().get_message_id(), send=False)
        elif callback_type == CallbackTypes.NEXT_PHOTO:
            process_next_photo(bot, chat_id, callback.get_message().get_message_id(), \
                callback_answ_data, tg_user)
        elif callback_type == CallbackTypes.PREV_PHOTO:
            process_prev_photo(bot, chat_id, callback.get_message().get_message_id(), \
                callback_answ_data, tg_user)
        elif callback_type == CallbackTypes.ALREADY_VOTED:
            send_already_voted(bot, callback.get_id())
        elif callback_type == CallbackTypes.VOTE:
            process_vote(bot, chat_id, callback.get_id(), callback.get_message().get_message_id(), \
                callback_answ_data, tg_user)
        elif callback_type == CallbackTypes.ABOUT:
            send_about(bot, chat_id, callback.get_message().get_message_id())
        elif callback_type == CallbackTypes.BIOGRAPHY:
            process_biography(bot, chat_id, callback.get_message().get_message_id(), \
                callback_answ_data, tg_user)
    else:
        print('\n\n' + '-' * 15 + 'ERROR' + '-' * 15)
        print(err + "\n\n")        
    
    bot.answerCallbackQuery(callback.get_id())


@processor(state_manager, from_states=state_types.All, message_types=[message_types.Text, \
    message_types.Video, message_types.Audio, message_types.Voice, message_types.Sticker, message_types.Animation,\
    message_types.Document, message_types.Poll, message_types.Location, message_types.Contact, message_types.Photo])
def start_message(bot: TelegramBot, update: Update, state: TelegramState):
    chat, message, user = update.get_chat(), \
        update.get_message(), update.get_user()
    
    if chat is None or message is None or user is None:
        return

    try:
        tg_user = TelegramUser.objects.filter(telegram_id=user.get_id())[0]
    except IndexError: 
        tg_user = None

    dispatch(bot, message, chat.get_id(), tg_user)


@processor(state_manager, from_states=state_types.All, update_types=[update_types.CallbackQuery])
def handle_callback_query(bot: TelegramBot, update, state):
    cb_data, chat, user = update.get_callback_query(), \
        update.get_chat(), update.get_user()

    if cb_data is None or chat is None or user is None:
        return

    try:
        tg_user = TelegramUser.objects.filter(telegram_id=user.get_id())[0]
    except IndexError: 
        tg_user = None
        
    dispatch_callback(bot, cb_data, chat.get_id(), tg_user)