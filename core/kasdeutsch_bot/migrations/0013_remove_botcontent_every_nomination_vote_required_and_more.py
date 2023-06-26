# Generated by Django 4.2.2 on 2023-06-26 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kasdeutsch_bot', '0012_botcontent_every_nomination_vote_required'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botcontent',
            name='every_nomination_vote_required',
        ),
        migrations.AddField(
            model_name='competition',
            name='every_nomination_vote_required',
            field=models.BooleanField(default=False, verbose_name='Необходимо голосовать в каждой номинации'),
        ),
        migrations.AddField(
            model_name='uservote',
            name='credited',
            field=models.BooleanField(default=False, verbose_name='Активен ли голос (учитывается при условии голосования во всех номинациях)'),
        ),
    ]