# Generated by Django 3.2.3 on 2021-08-04 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kasdeutsch_bot', '0007_nomination_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nomination',
            options={'verbose_name': 'номинация', 'verbose_name_plural': 'номинации'},
        ),
        migrations.AlterField(
            model_name='botcontent',
            name='share_contact',
            field=models.CharField(default='Поделиться контактом', max_length=255, verbose_name='Текст кнопки "Поделиться контактом"'),
        ),
        migrations.AlterField(
            model_name='nomination',
            name='description',
            field=models.TextField(default='Кандидаты номинации', verbose_name='Текст номинации'),
        ),
    ]
