# Generated by Django 4.2.2 on 2023-06-25 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kasdeutsch_bot', '0010_competition_image_about'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='image_about',
            field=models.ImageField(null=True, upload_to='', verbose_name='About photo'),
        ),
    ]