from .models import Nomination, UserVote, \
    Competition, Vote, TelegramState, TelegramChat


def check_vote(tg_user, nomination_id):
    try:
        competition = Competition.objects.filter(is_active=True)
        if competition.exists():
            competition = competition.first()
            nominations = Nomination.objects.filter(competition=competition)
            if nomination_id in [nom.id for nom in nominations]:
                user_vote = UserVote.objects.get(
                    tg_user__telegram_id=tg_user.telegram_id,
                    nomination_id=nomination_id
                )
                voted = True
            else:
                return False, None
        else:
            return False, None
    except UserVote.DoesNotExist:
        voted = False
        user_vote = None

    return voted, user_vote


def is_only_one_in_nomination(nomination_id):
    votes = Vote.objects.filter(nomination_id=nomination_id)
    return len(votes) == 1


def delete_request_phone_message(bot, tg_user, chat_id):
    try:
        chat_state = TelegramState.objects.get(
            telegram_user = tg_user,
            telegram_chat = TelegramChat.objects.get(telegram_id=chat_id)
        )
    except (TelegramState.DoesNotExist, TelegramChat.DoesNotExist):
        chat_state = None
        print('yoN')

    if chat_state:
        if chat_state.request_phone_number_message_id != '':
            bot.deleteMessage(chat_id, chat_state.request_phone_number_message_id)
        

def delete_request_phone_message_decorator(func):
    def wrap(*args, **kwargs):
        try:
            bot = args[0]
            chat_id = args[1]
            tg_user = args[-1]
            delete_request_phone_message(bot, tg_user, chat_id)
        except:
            pass
        return func(*args, **kwargs)
    return wrap
