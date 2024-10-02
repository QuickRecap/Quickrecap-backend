# Generated by Django 3.2.23 on 2024-10-01 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickrecap_app', '0008_auto_20241001_0816'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Pregunta',
            new_name='Enunciado',
        ),
        migrations.RenameField(
            model_name='actividad',
            old_name='categoria',
            new_name='tipo_actividad',
        ),
        migrations.RenameField(
            model_name='opcion',
            old_name='pregunta',
            new_name='enun_id',
        ),
        migrations.AlterField(
            model_name='opcion',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
