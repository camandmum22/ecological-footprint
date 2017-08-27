# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('descripcion', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='Edificio',
            fields=[
                ('id', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('descripcion', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='Medicion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=20)),
                ('email', models.EmailField(default=b'email@email.com', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ValorVariable_Medicion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valor', models.DecimalField(max_digits=10, decimal_places=2)),
                ('categoria', models.ForeignKey(to='Footprint.Categoria')),
                ('medicion', models.ForeignKey(to='Footprint.Medicion')),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('unidad', models.CharField(max_length=20)),
                ('descripcion', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='Punto_Monitoreo',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True)),
                ('denominacion', models.CharField(max_length=80)),
                ('edificio', models.OneToOneField(primary_key=True, serialize=False, to='Footprint.Edificio')),
            ],
        ),
        migrations.AddField(
            model_name='valorvariable_medicion',
            name='variable',
            field=models.ForeignKey(to='Footprint.Variable'),
        ),
        migrations.AddField(
            model_name='medicion',
            name='punto',
            field=models.ForeignKey(to='Footprint.Punto_Monitoreo'),
        ),
    ]
