# Generated by Django 2.0.7 on 2018-09-03 23:26

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20180828_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notapedido',
            name='fecha',
            field=models.DateField(default=datetime.datetime(2018, 9, 3, 23, 26, 18, 733817, tzinfo=utc), verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='notaremision',
            name='fecha',
            field=models.DateField(default=datetime.datetime(2018, 9, 3, 23, 26, 18, 733817, tzinfo=utc), verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='recepcion',
            name='fecha',
            field=models.DateField(default=datetime.datetime(2018, 9, 3, 23, 26, 18, 733817, tzinfo=utc), verbose_name='Fecha'),
        ),
    ]
