# Generated by Django 2.0.7 on 2018-08-11 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20180811_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notapedido',
            name='fecha',
            field=models.DateField(verbose_name='Fecha'),
        ),
    ]