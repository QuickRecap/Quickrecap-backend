# Generated by Django 3.2.23 on 2024-10-04 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickrecap_app', '0010_auto_20241004_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='puntos',
            field=models.IntegerField(default=0),
        ),
    ]