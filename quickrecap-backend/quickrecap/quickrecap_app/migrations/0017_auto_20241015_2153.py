# Generated by Django 3.2.23 on 2024-10-16 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickrecap_app', '0016_gapenunciado_gaprespuesta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gaprespuesta',
            name='texto',
        ),
        migrations.AddField(
            model_name='gaprespuesta',
            name='opciones_correctas',
            field=models.TextField(default='hola'),
        ),
    ]
