# Generated by Django 2.2.7 on 2019-11-28 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20191128_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='homeroom_char',
            field=models.CharField(default='#', max_length=1, verbose_name='Homeroom letter'),
        ),
    ]
