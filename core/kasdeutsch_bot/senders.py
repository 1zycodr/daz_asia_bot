from django.db.models import Count
from django_tgbot.types.inlinekeyboardbutton import InlineKeyboardButton
from django_tgbot.types.inlinekeyboardmarkup import InlineKeyboardMarkup
from django_tgbot.types.keyboardbutton import KeyboardButton
from django_tgbot.types.replykeyboardmarkup import ReplyKeyboardMarkup
from django_tgbot.types.inputmedia import InputMediaPhoto
from .models import Nomination, TelegramUser, Vote, \
    Model, Image, UserVote, Competition, BotContent, \
        TelegramChat, TelegramState
from .callback_types import CallbackTypes 
from .utils import check_vote, is_only_one_in_nomination,\
    delete_request_phone_message_decorator


def send_start_message(bot, chat_id, message_id, send=True):
    bot_content = BotContent.objects.all().last()

    buttons = []
    
    competition = Competition.objects.filter(is_active=True)

    if competition.exists():
        competition = competition.first()
        nominations = Nomination.objects.filter(competition=competition)

        for nomination in nominations:
            buttons.append([InlineKeyboardButton.a(
                nomination.name, 
                callback_data=CallbackTypes.set_nomination(nomination.id)
            )])

        buttons.append([InlineKeyboardButton.a(
            bot_content.about,
            callback_data=CallbackTypes.ABOUT
        )])

        if send:
            bot.sendPhoto(
                chat_id,
                caption=bot_content.chose_nomination, 
                photo='https://1bot.wiedergeburt.kz' + competition.image.url,
                reply_markup=InlineKeyboardMarkup.a(buttons)
            )
            bot.deleteMessage(
                chat_id, message_id
            )
        else:
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + competition.image.url, 
                bot_content.chose_nomination),
                reply_markup=InlineKeyboardMarkup.a(buttons)
            )
    else:
        if send:
            bot.sendPhoto(
                chat_id,
                caption=bot_content.no_competition, 
                photo='https://1bot.wiedergeburt.kz' + bot_content.no_competition_image.url,
                reply_markup=InlineKeyboardMarkup.a([[
                    InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
                ]])
            )
            bot.deleteMessage(
                chat_id, message_id
            )
        else:
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + bot_content.no_competition_image.url, 
                bot_content.no_competition),
                reply_markup=InlineKeyboardMarkup.a([[
                    InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
                ]])
            )


def send_already_voted(bot, callback_id):
    bot_content = BotContent.objects.all().last()
    bot.answerCallbackQuery(
        callback_id, 
        text=bot_content.already_voted
    )


def send_should_give_contact(bot, callback_id):
    bot_content = BotContent.objects.all().last()
    bot.answerCallbackQuery(
        callback_id, 
        text=bot_content.send_contact_text
    )


def send_unk_com_message(bot, chat_id, message_id):
    bot.deleteMessage(
        chat_id, 
        message_id
    )


def send_about(bot, chat_id, message_id):
    bot_content = BotContent.objects.all().last()
    competition = Competition.objects.filter(is_active=True)

    if competition.exists():
        competition = competition.first()
        bot.editMessageMedia(
            chat_id=chat_id, 
            message_id=message_id,
            media=InputMediaPhoto.a(
                'photo', 
                'https://1bot.wiedergeburt.kz' + competition.image_about.url,
                competition.about
            ),
            reply_markup=InlineKeyboardMarkup.a([[InlineKeyboardButton.a(bot_content.back, callback_data=CallbackTypes.START)]])
        )
    else:
        bot.editMessageMedia(
            chat_id=chat_id, 
            message_id=message_id,
            media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + bot_content.no_competition_image.url, 
            bot_content.no_competition),
            reply_markup=InlineKeyboardMarkup.a([[
                InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
            ]])
        )

@delete_request_phone_message_decorator
def send_nomination_models(bot, chat_id, message_id, nomination_id, tg_user):
    bot_content = BotContent.objects.all().last()
    competition = Competition.objects.filter(is_active=True)

    if competition.exists():
        competition = competition.first()
        nominations = Nomination.objects.filter(competition=competition)

        if nomination_id in [nom.id for nom in nominations]:
            buttons = []

            voted, user_vote = check_vote(tg_user, nomination_id)

            votes = Vote.objects.filter(nomination_id=nomination_id)

            if not voted:
                votes = votes.order_by('model__second_name')
            else:
                votes = votes.order_by('-rating', 'model__second_name')
                
            total_rating = sum([vote.rating for vote in votes])

            for vote in votes:
                model_name = str(vote.model)

                if voted and total_rating != 0:
                    if user_vote.model.id == vote.model.id: 
                        model_name += f' {vote.rating} {bot_content.votess}'
                        # model_name += ' (%g%s %s)' % (float('%.2f' % (vote.rating / total_rating * 100.0,)), '%', bot_content.votess)
                    else:
                        model_name += f' {vote.rating} {bot_content.votes}'
                        # model_name += ' (%g%s %s)' % (float('%.2f' % (vote.rating / total_rating * 100.0,)), '%', bot_content.votes)

                buttons.append([InlineKeyboardButton.a(
                    model_name,
                    callback_data=CallbackTypes.set_model(vote.model.id, nomination_id)
                )])

            buttons.append([InlineKeyboardButton.a(
                bot_content.back, 
                callback_data=CallbackTypes.START
            )])

            bot.editMessageMedia(
                chat_id=chat_id,
                message_id=message_id,
                media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + Nomination.objects.get(id=nomination_id).image.url, 
                    Nomination.objects.get(pk=nomination_id).description),
                reply_markup=InlineKeyboardMarkup.a(buttons)
            )
        else:
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image.url, 
                bot_content.update_menu),
                reply_markup=InlineKeyboardMarkup.a([[
                    InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
                ]])
            )
    else:
        bot.editMessageMedia(
            chat_id=chat_id, 
            message_id=message_id,
            media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + bot_content.no_competition_image.url, 
            bot_content.no_competition),
            reply_markup=InlineKeyboardMarkup.a([[
                InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
            ]])
        )


def send_model(bot, chat_id, message_id, data, tg_user):
    bot_content = BotContent.objects.all().last()
    competition = Competition.objects.filter(is_active=True)

    if competition.exists():
        competition = competition.first()
        nominations = Nomination.objects.filter(competition=competition)

        model_id, nomination_id = data 

        if nomination_id in [nom.id for nom in nominations]:

            buttons = []

            model = Model.objects.get(id=model_id)
            photos = Image.objects.filter(model=model)

            voted, user_vote = check_vote(tg_user, nomination_id)
            
            if len(photos) == 0:
                photo = bot_content.default_model_photo.url
                photo_ind = -1
            else:
                photo = photos[0].image.url
                photo_ind = 0

            if len(photos) > 1:
                buttons.append([InlineKeyboardButton.a(
                    bot_content.next_photo, 
                    callback_data=CallbackTypes.set_next_photo(model_id, photo_ind, nomination_id, 0)
                )])

            buttons.append([InlineKeyboardButton.a(
                bot_content.show_bio,
                callback_data=CallbackTypes.set_bio(model_id, photo_ind, nomination_id, 0)
            )])
            
            if not is_only_one_in_nomination(nomination_id):
                if not voted:
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.vote, 
                        callback_data=CallbackTypes.set_vote(model_id, photo_ind, nomination_id, 0)
                    )])
                elif user_vote.model.id == model_id:
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.was_checked, 
                        callback_data=CallbackTypes.set_already_voted()
                    )])
                else:
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.was_checked_in_this_nomination, 
                        callback_data=CallbackTypes.set_already_voted()
                    )])

            buttons.append([InlineKeyboardButton.a(
                bot_content.back, 
                callback_data=CallbackTypes.set_nomination(nomination_id)
            )])

            bot.editMessageMedia(
                chat_id=chat_id,
                message_id=message_id,
                media=InputMediaPhoto.a('photo', 
                    'https://1bot.wiedergeburt.kz' + photo, 
                    str(model)
                ),
                reply_markup=InlineKeyboardMarkup.a(buttons)
            )
        else:
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image.url, 
                bot_content.update_menu),
                reply_markup=InlineKeyboardMarkup.a([[
                    InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
                ]])
            )
    else:
        bot.editMessageMedia(
            chat_id=chat_id, 
            message_id=message_id,
            media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + bot_content.no_competition_image.url, 
            bot_content.no_competition),
            reply_markup=InlineKeyboardMarkup.a([[
                InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
            ]])
        )


@delete_request_phone_message_decorator
def process_next_photo(bot, chat_id, message_id, data, tg_user):
    bot_content = BotContent.objects.all().last()
    competition = Competition.objects.filter(is_active=True)

    if competition.exists():
        competition = competition.first()
        nominations = Nomination.objects.filter(competition=competition)

        model_id, photo_ind, nomination_id, status = data

        if nomination_id in [nom.id for nom in nominations]:
            buttons = []
            
            photo_ind += 1

            model = Model.objects.get(id=model_id)
            photos = Image.objects.filter(model=model)

            photo = photos[photo_ind].image.url

            photo_buttons = [InlineKeyboardButton.a(
                bot_content.prev_photo, 
                callback_data=CallbackTypes.set_prev_photo(model_id, photo_ind, nomination_id, status)
            )]

            if len(photos) - 1 != photo_ind:
                photo_buttons.append(InlineKeyboardButton.a(
                    bot_content.next_photo,
                    callback_data=CallbackTypes.set_next_photo(model_id, photo_ind, nomination_id, status)
                ))

            buttons.append(photo_buttons)

            buttons.append([InlineKeyboardButton.a(
                bot_content.show_bio if status == 0 else bot_content.hide_bio,
                callback_data=CallbackTypes.set_bio(model_id, photo_ind, nomination_id, status)
            )])
            
            voted, user_vote = check_vote(tg_user, nomination_id)

            if not is_only_one_in_nomination(nomination_id):
                if not voted:
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.vote, 
                        callback_data=CallbackTypes.set_vote(model_id, photo_ind, nomination_id, status)
                    )])
                elif user_vote.model.id == model_id:
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.was_checked, 
                        callback_data=CallbackTypes.set_already_voted()
                    )])
                else: 
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.was_checked_in_this_nomination, 
                        callback_data=CallbackTypes.set_already_voted()
                    )])

            buttons.append([InlineKeyboardButton.a(
                bot_content.back, 
                callback_data=CallbackTypes.set_nomination(nomination_id)
            )])
            
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + photo, str(model) + (f'\n{model.description}' if status == 1 else '')), 
                reply_markup=InlineKeyboardMarkup.a(buttons)
            )
        else:
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image.url, 
                bot_content.update_menu),
                reply_markup=InlineKeyboardMarkup.a([[
                    InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
                ]])
            )
    else:
        bot.editMessageMedia(
            chat_id=chat_id, 
            message_id=message_id,
            media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + bot_content.no_competition_image.url, 
            bot_content.no_competition),
            reply_markup=InlineKeyboardMarkup.a([[
                InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
            ]])
        )


@delete_request_phone_message_decorator
def process_prev_photo(bot, chat_id, message_id, data, tg_user):
    bot_content = BotContent.objects.all().last()
    competition = Competition.objects.filter(is_active=True)

    if competition.exists():
        competition = competition.first()
        nominations = Nomination.objects.filter(competition=competition)

        model_id, photo_ind, nomination_id, status = data

        if nomination_id in [nom.id for nom in nominations]:
            buttons = []
            
            photo_ind -= 1

            model = Model.objects.get(id=model_id)
            photos = Image.objects.filter(model=model)

            photo = photos[photo_ind].image.url

            photo_buttons = [InlineKeyboardButton.a(
                bot_content.next_photo, 
                callback_data=CallbackTypes.set_next_photo(model_id, photo_ind, nomination_id, status)
            )]

            if photo_ind != 0:
                photo_buttons.append(InlineKeyboardButton.a(
                    bot_content.prev_photo,
                    callback_data=CallbackTypes.set_prev_photo(model_id, photo_ind, nomination_id, status)
                ))
            
            buttons.append(photo_buttons[::-1])

            buttons.append([InlineKeyboardButton.a(
                bot_content.show_bio if status == 0 else bot_content.hide_bio,
                callback_data=CallbackTypes.set_bio(model_id, photo_ind, nomination_id, status)
            )])
            
            voted, user_vote = check_vote(tg_user, nomination_id)

            if not is_only_one_in_nomination(nomination_id):
                if not voted:
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.vote, 
                        callback_data=CallbackTypes.set_vote(model_id, photo_ind, nomination_id, status)
                    )])
                elif user_vote.model.id == model_id:
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.was_checked, 
                        callback_data=CallbackTypes.set_already_voted()
                    )])
                else:
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.was_checked_in_this_nomination, 
                        callback_data=CallbackTypes.set_already_voted()
                    )])

            buttons.append([InlineKeyboardButton.a(
                bot_content.back, 
                callback_data=CallbackTypes.set_nomination(nomination_id)
            )])

            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + photo, str(model) + (f'\n{model.description}' if status == 1 else '')), 
                reply_markup=InlineKeyboardMarkup.a(buttons)
            )
        else:
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image.url, 
                bot_content.update_menu),
                reply_markup=InlineKeyboardMarkup.a([[
                    InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
                ]])
            )
    else:
        bot.editMessageMedia(
            chat_id=chat_id, 
            message_id=message_id,
            media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + bot_content.no_competition_image.url, 
            bot_content.no_competition),
            reply_markup=InlineKeyboardMarkup.a([[
                InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
            ]])
        )


def process_vote(bot, chat_id, callback_id, message_id, data, tg_user: TelegramUser):
    bot_content = BotContent.objects.all().last()
    competition = Competition.objects.filter(is_active=True)

    if competition.exists():
        competition = competition.first()
        nominations = Nomination.objects.filter(competition=competition)

        model_id, photo_ind, nomination_id, status = data

        if nomination_id in [nom.id for nom in nominations]:
            buttons = []
            
            model = Model.objects.get(id=model_id)

            if photo_ind != -1:
                photos = Image.objects.filter(model=model)
                photo = photos[photo_ind].image.url
            else:
                photo = bot_content.default_model_photo.url


            if photo_ind != -1:
                photo_buttons = []
                if photo_ind != 0:
                    photo_buttons.append(InlineKeyboardButton.a(
                        bot_content.prev_photo,
                        callback_data=CallbackTypes.set_prev_photo(model_id, photo_ind, nomination_id, status)
                    ))
                
                if photo_ind != len(photos) - 1:
                    photo_buttons.append(InlineKeyboardButton.a(
                        bot_content.next_photo, 
                        callback_data=CallbackTypes.set_next_photo(model_id, photo_ind, nomination_id, status)
                    ))

                buttons.append(photo_buttons)
                
            buttons.append([InlineKeyboardButton.a(
                bot_content.show_bio if status == 0 else bot_content.hide_bio,
                callback_data=CallbackTypes.set_bio(model_id, photo_ind, nomination_id, status)
            )])

            nomination = Nomination.objects.get(id=nomination_id)

            voted, user_vote = check_vote(tg_user, nomination_id)

            if not voted:

                if tg_user.phone_number is not None:
                    vote, _ = Vote.objects.get_or_create(
                        model=model, 
                        nomination=nomination
                    )

                    user_vote = UserVote.objects.create(
                        tg_user=TelegramUser.objects.get(telegram_id=tg_user.telegram_id),
                        nomination=nomination, 
                        model=model,
                        credited=not competition.every_nomination_vote_required,
                    )
                    user_vote.save()

                    is_voted_all_nominations = False

                    if competition.every_nomination_vote_required:
                        user_votes = UserVote.objects.filter(
                            tg_user=tg_user,
                            nomination__competition=competition,
                            credited=False
                        )
                        current_nominations = competition.nomination_set.all().\
                            annotate(votes_count=Count('vote')).\
                            filter(votes_count__gt=1)
                        is_voted_all_nominations = len(user_votes) == len(current_nominations)
                        if is_voted_all_nominations:
                            for curr_user_vote in user_votes:
                                curr_vote = Vote.objects.get(
                                    model=curr_user_vote.model,
                                    nomination=curr_user_vote.nomination,
                                )
                                curr_user_vote.credited = True
                                curr_vote.rating += 1
                                curr_user_vote.save()
                                curr_vote.save()
                    else:
                        vote.rating += 1
                        vote.save()

                    if is_voted_all_nominations:
                        bot.answerCallbackQuery(
                            callback_id,
                            text=bot_content.was_checked_and_credited,
                            show_alert=True,
                        )
                    else:
                        bot.answerCallbackQuery(
                            callback_id,
                            text=bot_content.was_checked_not_credited,
                            show_alert=True,
                        )
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.was_checked,
                        callback_data=CallbackTypes.set_already_voted()
                    )])
                else:
                    try:
                        chat_state = TelegramState.objects.get(
                            telegram_user=tg_user,
                            telegram_chat=TelegramChat.objects.get(telegram_id=chat_id)
                        )
                    except (TelegramState.DoesNotExist, TelegramChat.DoesNotExist):
                        chat_state = None

                    if chat_state:
                        if chat_state.request_phone_number_message_id != '':
                            bot.deleteMessage(chat_id, chat_state.request_phone_number_message_id)
                    
                        message = bot.sendMessage(
                            chat_id=chat_id, 
                            text=bot_content.send_contact_text,
                            reply_markup=ReplyKeyboardMarkup.a(
                                resize_keyboard=True,
                                keyboard=[
                                    [KeyboardButton.a(bot_content.share_contact, request_contact=True)]
                                ]
                            )
                        )

                        chat_state.request_phone_number_message_id = message.message_id
                        chat_state.save()

                    return
            else:
                if not is_only_one_in_nomination(nomination_id):
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.was_checked_in_this_nomination, 
                        callback_data=CallbackTypes.set_already_voted()
                    )])

            buttons.append([InlineKeyboardButton.a(
                bot_content.back, 
                callback_data=CallbackTypes.set_nomination(nomination_id)
            )])

            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + photo, str(model) + (f'\n{model.description}' if status == 1 else '')), 
                reply_markup=InlineKeyboardMarkup.a(buttons),
            )
        else:
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image.url, 
                bot_content.update_menu),
                reply_markup=InlineKeyboardMarkup.a([[
                    InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
                ]])
            )
    else:
        bot.editMessageMedia(
            chat_id=chat_id, 
            message_id=message_id,
            media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + bot_content.no_competition_image.url, 
            bot_content.no_competition),
            reply_markup=InlineKeyboardMarkup.a([[
                InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
            ]])
        )


@delete_request_phone_message_decorator
def process_biography(bot, chat_id, message_id, data, tg_user):
    bot_content = BotContent.objects.all().last()
    competition = Competition.objects.filter(is_active=True)

    if competition.exists():
        competition = competition.first()
        nominations = Nomination.objects.filter(competition=competition)

        model_id, photo_ind, nomination_id, status = data 

        if nomination_id in [nom.id for nom in nominations]:

            buttons = []

            model = Model.objects.get(id=model_id)
            photos = Image.objects.filter(model=model)

            voted, user_vote = check_vote(tg_user, nomination_id)
            
            if len(photos) == 0:
                photo = bot_content.default_model_photo.url
            else:
                photo = photos[photo_ind].image.url

            photo_buttons = []
            status = 1 if status == 0 else 0 

            if photo_ind > 0 and len(photos) != 1:
                photo_buttons.append(InlineKeyboardButton.a(
                    bot_content.prev_photo, 
                    callback_data=CallbackTypes.set_prev_photo(model_id, photo_ind, nomination_id, status)
                ))

            if len(photos) > 1 and photo_ind < len(photos):
                photo_buttons.append(InlineKeyboardButton.a(
                    bot_content.next_photo, 
                    callback_data=CallbackTypes.set_next_photo(model_id, photo_ind, nomination_id, status)
                ))

            buttons.append(photo_buttons)


            buttons.append([InlineKeyboardButton.a(
                bot_content.show_bio if status == 0 else bot_content.hide_bio,
                callback_data=CallbackTypes.set_bio(model_id, photo_ind, nomination_id, status)
            )])
            
            if not is_only_one_in_nomination(nomination_id):
                if not voted:
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.vote, 
                        callback_data=CallbackTypes.set_vote(model_id, photo_ind, nomination_id, status)
                    )])
                elif user_vote.model.id == model_id:
                    buttons.append([InlineKeyboardButton.a(
                        bot_content.was_checked, 
                        callback_data=CallbackTypes.set_already_voted()
                    )])
                else:
                    if not is_only_one_in_nomination(nomination_id):
                        buttons.append([InlineKeyboardButton.a(
                            bot_content.was_checked_in_this_nomination, 
                            callback_data=CallbackTypes.set_already_voted()
                        )])

            buttons.append([InlineKeyboardButton.a(
                bot_content.back, 
                callback_data=CallbackTypes.set_nomination(nomination_id)
            )])

            bot.editMessageMedia(
                chat_id=chat_id,
                message_id=message_id,
                media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + photo, 
                    str(model) + (f'\n{model.description}' if status == 1 else '')),
                reply_markup=InlineKeyboardMarkup.a(buttons)
            )
            
        else:
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + bot_content.update_menu_image.url, 
                bot_content.update_menu),
                reply_markup=InlineKeyboardMarkup.a([[
                    InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
                ]])
            )
    else:
        bot.editMessageMedia(
            chat_id=chat_id, 
            message_id=message_id,
            media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + bot_content.no_competition_image.url, 
            bot_content.no_competition),
            reply_markup=InlineKeyboardMarkup.a([[
                InlineKeyboardButton.a(bot_content.update, callback_data=CallbackTypes.START)
            ]])
        )
