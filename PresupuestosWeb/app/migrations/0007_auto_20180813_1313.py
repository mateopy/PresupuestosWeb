# Generated by Django 2.0.7 on 2018-08-13 17:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20180811_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notapedido',
            name='fecha',
            field=models.DateField(default=datetime.datetime.now, verbose_name='Fecha'),
        ),
    ]
