# Generated by Django 3.2.3 on 2021-07-05 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kasdeutsch_bot', '0003_alter_model_second_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
