# Generated by Django 3.2.19 on 2023-05-26 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_api', '0007_auto_20230526_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='judgement',
            name='firstDuration',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='judgement',
            name='secondDuration',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
