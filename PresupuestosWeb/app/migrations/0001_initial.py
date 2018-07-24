# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-23 16:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Articulo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20)),
                ('descripcion', models.CharField(max_length=50)),
                ('codigoBarras', models.CharField(max_length=50)),
                ('precio', models.FloatField(default=0)),
                ('observaciones', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='CategoriaArticulo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Dependencia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='NotaPedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(verbose_name='Fecha')),
                ('nroPedido', models.IntegerField()),
                ('precioAproximado', models.FloatField(default=0)),
                ('descripcionUso', models.CharField(max_length=200)),
                ('destino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dependencia_destino', to='app.Dependencia')),
                ('origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dependencia_origen', to='app.Dependencia')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NotaPedido_Detalle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Articulo')),
                ('notaPedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.NotaPedido')),
            ],
        ),
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
                ('codigo', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TipoArticulo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='dependencia',
            name='sucursal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Sucursal'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='categoria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.CategoriaArticulo'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='tipoArticulo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.TipoArticulo'),
        ),
    ]
