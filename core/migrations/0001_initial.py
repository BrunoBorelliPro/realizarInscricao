# Generated by Django 5.0.6 on 2024-06-06 16:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aluno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Sala',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Turma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Disciplina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('pre_requisitos', models.ManyToManyField(blank=True, null=True, to='core.disciplina')),
            ],
        ),
        migrations.CreateModel(
            name='ListaDeEspera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aluno', models.ManyToManyField(blank=True, null=True, to='core.aluno')),
                ('disciplina', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.disciplina')),
            ],
        ),
        migrations.CreateModel(
            name='OfertaDisciplina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.disciplina')),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.turma')),
            ],
        ),
        migrations.CreateModel(
            name='Participacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.aluno')),
                ('orferta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ofertadisciplina')),
            ],
        ),
        migrations.CreateModel(
            name='Aula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horario_inicio', models.TimeField()),
                ('sala', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.sala')),
            ],
        ),
    ]
