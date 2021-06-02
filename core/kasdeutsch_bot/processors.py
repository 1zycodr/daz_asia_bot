from django_tgbot.decorators import processor
from django_tgbot.state_manager import message_types, update_types, state_types
from django_tgbot.types.update import Update
from django_tgbot.types.message import Message
from .bot import state_manager
from .models import TelegramState, TelegramUser
from .bot import TelegramBot
from .senders import send_start_message, send_unk_com_message, send_nomination_models
from .callback_types import CallbackTypes

state_manager.set_default_update_types(update_types.Message)

available_options = {
    '/start': send_start_message
}

def dispatch(bot: TelegramBot, message: Message, chat_id):
    try:
        available_options[message.get_text()](bot, chat_id)
    except KeyError:
        send_unk_com_message(bot, chat_id)


def dispatch_callback(bot: TelegramBot, callback, chat_id, tg_user):
    callback_data = callback.get_data()
    
    if callback_data is None:
        bot.answerCallbackQuery(callback.get_id(), 'Invalid callback!')
        return

    callback_type, callback_answ_data, err = CallbackTypes.get_type(callback_data)

    if err is None: 
        if callback_type == CallbackTypes.NOMINATION:
            if tg_user:
                send_nomination_models(bot, chat_id, callback_answ_data, voted=tg_user.voted)
            else:
                send_nomination_models(bot, chat_id, callback_answ_data, voted=False)
    else:
        print('\n\n' + '-' * 15 + 'ERROR' + '-' * 15)
        print(err + "\n\n")        
    
    bot.answerCallbackQuery(callback.get_id())


@processor(state_manager, from_states=state_types.All, message_types=[message_types.Text])
def start_message(bot: TelegramBot, update: Update, state: TelegramState):
    chat, message, user = update.get_chat(), \
        update.get_message(), update.get_user()
    
    if chat is None or message is None or user is None:
        return

    dispatch(bot, message, chat.get_id())


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


# @processor(state_manager, from_states=state_types.Reset, message_types=[message_types.Text])
# def send_keyboards(bot: TelegramBot, update: Update, state: TelegramState):
#     chat_id = update.get_chat().get_id()
#     text = str(update.get_message().get_text())

#     if text.lower() in ['normal keyboard', 'regular keyboard']:
#         send_normal_keyboard(bot, chat_id)
#     elif text.lower() in ['inline keyboard']:
#         send_inline_keyboard(bot, chat_id)
#     else:
#         send_options(bot, chat_id)

# def send_normal_keyboard(bot, chat_id):
#     bot.sendMessage(
#         chat_id,
#         text='Here is a keyboard for you!',
#         reply_markup=ReplyKeyboardMarkup.a(
#             one_time_keyboard=True,
#             resize_keyboard=True,
#             keyboard=[
#                 [KeyboardButton.a('Text 1'), KeyboardButton.a('Text 2')],
#                 [KeyboardButton.a('Text 3'), KeyboardButton.a('Text 4')],
#                 [KeyboardButton.a('Text 5')]
#             ]
#         )
#     )


# def send_inline_keyboard(bot, chat_id):
#     bot.sendMessage(
#         chat_id,
#         text='Here is an inline keyboard for you!',
#         reply_markup=InlineKeyboardMarkup.a(
#             inline_keyboard=[
#                 [
#                     InlineKeyboardButton.a('URL Button', url='https://google.com'),
#                     InlineKeyboardButton.a('Callback Button', callback_data='some_callback_data')
#                 ]
#             ]
#         )
#     )


# def send_options(bot, chat_id):
#     bot.sendMessage(
#         chat_id,
#         text='I can send you two different types of keyboards!\nSend me `normal keyboard` or `inline keyboard` and I\'ll make one for you ;)',
#         parse_mode=bot.PARSE_MODE_MARKDOWN
#     )