# Generated by Django 3.2.23 on 2024-10-12 00:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quickrecap_app', '0011_user_puntos'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('comentario', models.TextField()),
                ('calificacion', models.IntegerField()),
                ('actividad_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quickrecap_app.actividad')),
            ],
        ),
    ]