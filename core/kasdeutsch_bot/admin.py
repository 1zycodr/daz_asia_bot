from django.contrib import admin
from django.db.models.constraints import CheckConstraint
from .models import TelegramState, TelegramChat, \
    TelegramUser, Model, Nomination, Image, Vote, \
    UserVote, Competition, BotContent

# admin.site.register(TelegramState)
# admin.site.register(TelegramChat)
admin.site.register(TelegramUser)
admin.site.register(UserVote)

class ModelImagesInline(admin.StackedInline):
    model = Image
    extra = 0

class ModelVotesInline(admin.StackedInline):
    model = Vote
    extra = 0

    def get_formset(self, request, obj, **kwargs):
        formset = super(ModelVotesInline, self).get_formset(request, obj, **kwargs)
        widget = formset.form.base_fields['nomination'].widget
        widget.can_add_related = False
        widget.can_change_related = False
        return formset

class ModelAdmin(admin.ModelAdmin):
    inlines = [ModelImagesInline, ModelVotesInline]


class NominationModelsInline(admin.StackedInline):
    model = Model.nominations.through
    extra = 0
    fields = ['model', 'nomination', 'rating']

class NominationAdmin(admin.ModelAdmin):
    inlines = [NominationModelsInline]


class CompetitionNominationsInline(admin.StackedInline):
    model = Nomination
    extra = 0

class CompetitionAdmin(admin.ModelAdmin):
    inlines = [CompetitionNominationsInline]


admin.site.register(Model, ModelAdmin)
admin.site.register(Nomination, NominationAdmin)
admin.site.register(Image)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(BotContent)