# Generated by Django 3.2.3 on 2021-08-06 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kasdeutsch_bot', '0009_telegramstate_request_phone_number_message_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='image_about',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='About photo'),
        ),
    ]
