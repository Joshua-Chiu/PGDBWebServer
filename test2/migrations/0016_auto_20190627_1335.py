# Generated by Django 2.1.2 on 2019-06-27 20:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test2', '0015_auto_20190627_1331'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plistcutoff',
            old_name='grade_11_t2',
            new_name='grade_11_T2',
        ),
        migrations.RenameField(
            model_name='plistcutoff',
            old_name='grade_8_t2',
            new_name='grade_8_T2',
        ),
    ]