# Generated by Django 2.2.13 on 2021-05-06 10:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_accesscontrol_identifier'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='permissions',
            new_name='accesscontrol',
        ),
    ]
