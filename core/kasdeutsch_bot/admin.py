from django.contrib import admin
from django.contrib.admin.models import LogEntry
from import_export.admin import ExportMixin
from import_export import resources
from import_export.fields import Field

from .models import TelegramState, TelegramChat, \
    TelegramUser, Model, Nomination, Image, Vote, \
    UserVote, Competition, BotContent

# admin.site.register(TelegramState)
# admin.site.register(TelegramChat)


class TelegramUserAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'phone_number', 'telegram_id', 'username')

admin.site.register(TelegramUser, TelegramUserAdmin)


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


class UserVoteResource(resources.ModelResource):
    id = Field(
	attribute='pk',
	column_name='ID'
    )
    username = Field(
	attribute='tg_user__username',
	column_name='Username',
    )
    first_name = Field(
        attribute='tg_user__first_name',
        column_name='First Name'
    )
    last_name = Field(
        attribute='tg_user__last_name',
        column_name='Last Name'
    )
    phone_number = Field(
	attribute='tg_user__phone_number',
	column_name='Phone Number'
    )
    nomination = Field(
	attribute='nomination__name',
        column_name='Nomination'
    )
    competition_model = Field(
        attribute='model__fullname', 
        column_name='Participant'
    )
    date = Field(
        attribute='date', 
        column_name='Date'
    )

    class Meta:
        model = UserVote
        exclude = ('tg_user', 'model', 'vote_date')


class UserVoteAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = UserVoteResource
    list_display = ('id', 'tg_user', 'nomination', 'model', 'vote_date')


class LogAdmin(admin.ModelAdmin):
    """Create an admin view of the history/log table"""
    list_display = ('action_time','user','content_type','change_message','is_addition','is_change','is_deletion')
    list_filter = ['action_time','user','content_type']
    ordering = ('-action_time',)
    #We don't want people changing this historical record:
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        #returning false causes table to not show up in admin page :-(
        #I guess we have to allow changing for now
        return True
    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Model, ModelAdmin)
admin.site.register(Nomination, NominationAdmin)
admin.site.register(Image)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(BotContent)
admin.site.register(UserVote, UserVoteAdmin)
admin.site.register(LogEntry, LogAdmin)
