# Generated by Django 3.2.3 on 2021-06-04 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kasdeutsch_bot', '0016_alter_competition_about'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='image',
            field=models.ImageField(default='', upload_to='', verbose_name='Фото'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='nomination',
            name='competition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='kasdeutsch_bot.competition', verbose_name='Конкурс:'),
        ),
    ]
