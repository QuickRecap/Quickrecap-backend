# Generated by Django 3.2.23 on 2024-09-29 08:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quickrecap_app', '0005_user_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('categoria', models.CharField(choices=[('Flashcards', 'Flashcards'), ('Linkers', 'Linkers'), ('Gaps', 'Gaps'), ('Quiz', 'Quiz')], max_length=10)),
                ('actividad_preguntas', models.JSONField()),
                ('privado', models.BooleanField(default=False)),
                ('tiempo_por_pregunta', models.IntegerField()),
                ('numero_preguntas', models.IntegerField()),
                ('veces_jugado', models.IntegerField(default=0)),
                ('favorito', models.BooleanField(default=False)),
                ('puntuacion_maxima', models.IntegerField(default=0)),
                ('completado', models.BooleanField(default=False)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='reporteerror',
            name='fecha_creacion',
        ),
        migrations.AlterField(
            model_name='reporteerror',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='Pregunta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('enunciado', models.TextField()),
                ('opciones', models.JSONField()),
                ('respuesta_correcta', models.IntegerField()),
                ('actividad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='preguntas', to='quickrecap_app.actividad')),
            ],
        ),
        migrations.CreateModel(
            name='Archivo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('url', models.URLField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
