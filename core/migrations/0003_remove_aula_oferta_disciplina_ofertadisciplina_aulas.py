# Generated by Django 5.0.6 on 2024-06-11 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_aula_dia_da_semana'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aula',
            name='oferta_disciplina',
        ),
        migrations.AddField(
            model_name='ofertadisciplina',
            name='aulas',
            field=models.ManyToManyField(to='core.aula'),
        ),
    ]