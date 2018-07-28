# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-28 21:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20180728_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articulo',
            name='unidadMedida',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.UnidadMedida'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notapedido',
            name='departamentoDestino',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='pedido_departamento_destino', to='app.DepartamentoSucursal'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notapedido',
            name='departamentoOrigen',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='pedido_departamento_origen', to='app.DepartamentoSucursal'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notaremision',
            name='departamentoDestino',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='remision_departamento_destino', to='app.DepartamentoSucursal'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notaremision',
            name='departamentoOrigen',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='remision_departamento_origen', to='app.DepartamentoSucursal'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recepcion',
            name='departamentoDestino',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='recepcion_departamento_destino', to='app.DepartamentoSucursal'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recepcion',
            name='departamentoOrigen',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='recepcion_departamento_origen', to='app.DepartamentoSucursal'),
            preserve_default=False,
        ),
    ]