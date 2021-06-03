from .models import UserVote

def check_vote(tg_user, nomination_id):
    try:
        user_vote = UserVote.objects.get(
            tg_user__telegram_id=tg_user.telegram_id,
            nomination_id=nomination_id
        )
        voted = True
    except UserVote.DoesNotExist:
        voted = False
        user_vote = None

    return voted, user_vote