from django.contrib import admin
from django.db.models.constraints import CheckConstraint
from .models import TelegramState, TelegramChat, \
    TelegramUser, Model, Nomination, Image, Vote, UserVote

# admin.site.register(TelegramState)
# admin.site.register(TelegramChat)
#admin.site.register(TelegramUser)
#admin.site.register(UserVote)

class ModelImagesInline(admin.StackedInline):
    model = Image
    extra = 0

class ModelVotesInline(admin.StackedInline):
    model = Vote
    extra = 0


class ModelAdmin(admin.ModelAdmin):
    inlines = [ModelImagesInline, ModelVotesInline]


class NominationModelsInline(admin.StackedInline):
    model = Model.nominations.through
    extra = 0
    fields = ['model', 'nomination', 'rating']

class NominationAdmin(admin.ModelAdmin):
    inlines = [NominationModelsInline]

admin.site.register(Model, ModelAdmin)
admin.site.register(Nomination, NominationAdmin)
admin.site.register(Image)
