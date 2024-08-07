# Generated by Django 3.2.3 on 2021-06-07 13:38

from django.db import migrations, models
import django.db.models.deletion
import kasdeutsch_bot.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('about', models.CharField(default='О конкурсе', max_length=50, verbose_name='Текст кнопки "О конкурсе"')),
                ('update', models.CharField(default='Обновить', max_length=50, verbose_name='Текст кнопки "Обновить"')),
                ('back', models.CharField(default='Назад', max_length=50, verbose_name='Текст кнопки "Назад"')),
                ('show_bio', models.CharField(default='Биография', max_length=50, verbose_name='Текст кнопки "Показать биографию"')),
                ('hide_bio', models.CharField(default='Скрыть биографию', max_length=50, verbose_name='Текст кнопки "Скрыть биографию"')),
                ('vote', models.CharField(default='Проголосовать!', max_length=50, verbose_name='Текст кнопки "Проголосовать"')),
                ('next_photo', models.CharField(default='>', max_length=50, verbose_name='Текст кнопки следующей фотографии')),
                ('prev_photo', models.CharField(default='<', max_length=50, verbose_name='Текст кнопки предыдущей фотографии')),
                ('was_checked', models.CharField(default='Ваш голос за эту модель был учтён!', max_length=50, verbose_name='Текст кнопки "Проголосовать", когда голос был учтён у текущей модели')),
                ('was_checked_in_this_nomination', models.CharField(default='Вы уже проголосовали за модель в этой номинации!', max_length=50, verbose_name='Текст кнопки "Проголосовать", когда голос был учтён у другой модели в этой категории')),
                ('chose_nomination', models.CharField(default='Выберите номинацию, в которой хотите проголосовать. У вас есть один голос в каждой номинации.', max_length=255, verbose_name='Текст меню выбора номинации')),
                ('no_competition', models.CharField(default='Нет активных конкурсов.', max_length=255, verbose_name='Текст меню когда конкурс отсутствует')),
                ('update_menu', models.CharField(default='Пожалуйста, обновите информацию о конкурсе!', max_length=255, verbose_name='Текст меню обновления конкурса')),
                ('already_voted', models.CharField(default='Ваш голос уже был учтён!', max_length=255, verbose_name='Текст всплывающего окна, когда голос учтён')),
                ('votes', models.CharField(default='голосов', max_length=255, verbose_name='Текст кандидата когда человек проголосовал')),
                ('votess', models.CharField(default='голосов, включая ваш', max_length=255, verbose_name='Текст кандидата когда человек проголосовал, включая его голос')),
                ('candidates', models.CharField(default='Кандидаты номинации', max_length=255, verbose_name='Текст меню списка кандидатов')),
                ('no_competition_image', models.ImageField(upload_to='', validators=[kasdeutsch_bot.models.validate_image], verbose_name='Фото для сообщения "Нет соревнования"')),
                ('update_menu_image', models.ImageField(upload_to='', validators=[kasdeutsch_bot.models.validate_image], verbose_name='Фото для меню обновления конкурса')),
                ('default_model_photo', models.ImageField(upload_to='', validators=[kasdeutsch_bot.models.validate_image], verbose_name='Дефолтное фото кандидата')),
            ],
            options={
                'verbose_name': 'Настройки',
                'verbose_name_plural': 'настройки',
            },
        ),
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('is_active', models.BooleanField(blank=True, default=False, verbose_name='Активный')),
                ('about', models.TextField(blank=True, default='', verbose_name='О конкурсе')),
                ('image', models.ImageField(upload_to='', validators=[kasdeutsch_bot.models.validate_image], verbose_name='Фото')),
            ],
            options={
                'verbose_name': 'Конкурс',
                'verbose_name_plural': 'конкурсы',
            },
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200, verbose_name='Имя')),
                ('second_name', models.CharField(default='', max_length=200, verbose_name='Фамилия')),
                ('last_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Отчество')),
                ('description', models.TextField(blank=True, max_length=1000, null=True, verbose_name='Биография')),
            ],
            options={
                'verbose_name': 'Модель',
                'verbose_name_plural': 'модели',
            },
        ),
        migrations.CreateModel(
            name='Nomination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
                ('image', models.ImageField(default='demo_nomination1234.png', upload_to='', validators=[kasdeutsch_bot.models.validate_image], verbose_name='Фото')),
                ('competition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='kasdeutsch_bot.competition', verbose_name='Конкурс:')),
            ],
            options={
                'verbose_name': 'номинацию',
                'verbose_name_plural': 'номинации',
            },
        ),
        migrations.CreateModel(
            name='TelegramChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.CharField(max_length=128, unique=True)),
                ('type', models.CharField(choices=[('private', 'private'), ('group', 'group'), ('supergroup', 'supergroup'), ('channel', 'channel')], max_length=128)),
                ('title', models.CharField(blank=True, max_length=512, null=True)),
                ('username', models.CharField(blank=True, max_length=128, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.CharField(max_length=128, unique=True)),
                ('is_bot', models.BooleanField(default=False)),
                ('username', models.CharField(blank=True, max_length=128, null=True)),
                ('first_name', models.CharField(db_collation='utf8mb4_general_ci', max_length=255)),
                ('last_name', models.CharField(blank=True, db_collation='utf8mb4_general_ci', max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(blank=True, default=0, verbose_name='Рейтинг')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kasdeutsch_bot.model', verbose_name='Модель')),
                ('nomination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kasdeutsch_bot.nomination', verbose_name='Номинация')),
            ],
            options={
                'verbose_name': 'Голосование',
                'verbose_name_plural': 'голосования',
                'ordering': ['-rating'],
            },
        ),
        migrations.CreateModel(
            name='UserVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kasdeutsch_bot.model')),
                ('nomination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kasdeutsch_bot.nomination')),
                ('tg_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kasdeutsch_bot.telegramuser')),
            ],
            options={
                'verbose_name': 'Голос',
                'verbose_name_plural': 'голоса',
                'unique_together': {('tg_user', 'nomination')},
            },
        ),
        migrations.AddField(
            model_name='telegramuser',
            name='votes',
            field=models.ManyToManyField(through='kasdeutsch_bot.UserVote', to='kasdeutsch_bot.Nomination'),
        ),
        migrations.AddField(
            model_name='model',
            name='nominations',
            field=models.ManyToManyField(through='kasdeutsch_bot.Vote', to='kasdeutsch_bot.Nomination', verbose_name='Номинации'),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='', validators=[kasdeutsch_bot.models.validate_image], verbose_name='Фото')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kasdeutsch_bot.model')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'изображения',
            },
        ),
        migrations.CreateModel(
            name='TelegramState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('memory', models.TextField(blank=True, null=True, verbose_name='Memory in JSON format')),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('telegram_chat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='telegram_states', to='kasdeutsch_bot.telegramchat')),
                ('telegram_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='telegram_states', to='kasdeutsch_bot.telegramuser')),
            ],
            options={
                'unique_together': {('telegram_user', 'telegram_chat')},
            },
        ),
    ]
