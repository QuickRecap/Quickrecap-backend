# Generated by Django 3.2.23 on 2024-09-19 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quickrecap_app', '0004_reporteerror'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
