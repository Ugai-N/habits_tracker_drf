# Generated by Django 4.2.7 on 2023-11-21 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0005_alter_habit_qty_per_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habit',
            name='period',
            field=models.IntegerField(choices=[(0, 'дней'), (1, 'часов'), (2, 'минут'), (3, 'секунд')], default=0, max_length=150, verbose_name='Интервал'),
        ),
    ]
