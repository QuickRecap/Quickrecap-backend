# Generated by Django 3.2.23 on 2024-10-15 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quickrecap_app', '0015_actividad_rated'),
    ]

    operations = [
        migrations.CreateModel(
            name='GapEnunciado',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('texto_completo', models.TextField()),
                ('texto_con_huecos', models.TextField()),
                ('actividad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quickrecap_app.actividad')),
            ],
        ),
        migrations.CreateModel(
            name='GapRespuesta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('texto', models.CharField(max_length=255)),
                ('posicion', models.IntegerField()),
                ('gap_enunciado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quickrecap_app.gapenunciado')),
            ],
        ),
    ]
