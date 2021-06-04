from django.db.models.lookups import In
from django_tgbot.types.inlinekeyboardbutton import InlineKeyboardButton
from django_tgbot.types.inlinekeyboardmarkup import InlineKeyboardMarkup
from django_tgbot.types.keyboardbutton import KeyboardButton
from django_tgbot.types.replykeyboardmarkup import ReplyKeyboardMarkup
from django_tgbot.types.replykeyboardremove import ReplyKeyboardRemove
from django_tgbot.types.inputmedia import InputMediaPhoto
from .models import Nomination, TelegramUser, Vote, \
    Model, Image, UserVote, Competition, BotContent
from .callback_types import CallbackTypes 
from .utils import check_vote


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
                'https://1bot.wiedergeburt.kz' + competition.image.url, 
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

                if voted:
                    if user_vote.model.id == vote.model.id: 
                        model_name += f' ({int(vote.rating / total_rating * 100)}% {bot_content.votess})'
                    else:
                        model_name += f' ({int(vote.rating / total_rating * 100)}% {bot_content.votes})'

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
                    f'{bot_content.candidates} "' + Nomination.objects.get(id=nomination_id).name + '":'),
                reply_markup=InlineKeyboardMarkup.a(buttons)
            )
        else:
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image, 
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
                photo = bot_content.default_model_photo
            else:
                photo = photos[0].image.url

            if len(photos) > 1:
                buttons.append([InlineKeyboardButton.a(
                    bot_content.next_photo, 
                    callback_data=CallbackTypes.set_next_photo(model_id, 0, nomination_id, 0)
                )])

            buttons.append([InlineKeyboardButton.a(
                bot_content.show_bio,
                callback_data=CallbackTypes.set_bio(model_id, 0, nomination_id, 0)
            )])
            
            if not voted:
                buttons.append([InlineKeyboardButton.a(
                    bot_content.vote, 
                    callback_data=CallbackTypes.set_vote(model_id, 0, nomination_id, 0)
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
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image, 
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
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image, 
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
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image, 
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


def process_vote(bot, chat_id, message_id, data, tg_user):
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

            photo = photos[photo_ind].image.url
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
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image, 
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
                photo = bot_content.default_model_photo
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
                media=InputMediaPhoto.a('photo', 'https://1bot.wiedergeburt.kz' + photo, 
                    str(model) + (f'\n{model.description}' if status == 1 else '')),
                reply_markup=InlineKeyboardMarkup.a(buttons)
            )
            
        else:
            bot.editMessageMedia(
                chat_id=chat_id, 
                message_id=message_id,
                media=InputMediaPhoto.a('photo', bot_content.update_menu_image, 
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