# Generated by Django 2.2.5 on 2019-09-24 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='no_entry',
            field=models.BooleanField(default=False),
        ),
    ]
