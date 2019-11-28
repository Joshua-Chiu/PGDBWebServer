# Generated by Django 2.2.7 on 2019-11-28 19:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grade_10',
            fields=[
                ('grade_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='data.Grade')),
            ],
            bases=('data.grade',),
        ),
        migrations.CreateModel(
            name='Grade_11',
            fields=[
                ('grade_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='data.Grade')),
            ],
            bases=('data.grade',),
        ),
        migrations.CreateModel(
            name='Grade_12',
            fields=[
                ('grade_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='data.Grade')),
            ],
            bases=('data.grade',),
        ),
        migrations.CreateModel(
            name='Grade_8',
            fields=[
                ('grade_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='data.Grade')),
            ],
            bases=('data.grade',),
        ),
        migrations.CreateModel(
            name='Grade_9',
            fields=[
                ('grade_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='data.Grade')),
            ],
            bases=('data.grade',),
        ),
        migrations.RemoveField(
            model_name='certificates',
            name='Grade',
        ),
        migrations.RemoveField(
            model_name='scholar',
            name='Grade',
        ),
        migrations.AlterModelOptions(
            name='pointcodes',
            options={'ordering': ['catagory', 'code']},
        ),
        migrations.RemoveField(
            model_name='grade',
            name='Student',
        ),
        migrations.RemoveField(
            model_name='student',
            name='homeroom',
        ),
        migrations.AddField(
            model_name='grade',
            name='AT_total',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='grade',
            name='FA_total',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='grade',
            name='SC_total',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='grade',
            name='SE_total',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='grade',
            name='_term1_avg',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='grade',
            name='_term2_avg',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='points',
            name='entered_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='student',
            name='cur_grade_num',
            field=models.IntegerField(default=0, verbose_name='current grade'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='goldplus_pin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='student',
            name='homeroom_char',
            field=models.CharField(default='X', max_length=1, verbose_name='Homeroom letter'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='silver_pin',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='plistcutoff',
            name='year',
            field=models.IntegerField(choices=[(1984, '1984 → 1985'), (1985, '1985 → 1986'), (1986, '1986 → 1987'), (1987, '1987 → 1988'), (1988, '1988 → 1989'), (1989, '1989 → 1990'), (1990, '1990 → 1991'), (1991, '1991 → 1992'), (1992, '1992 → 1993'), (1993, '1993 → 1994'), (1994, '1994 → 1995'), (1995, '1995 → 1996'), (1996, '1996 → 1997'), (1997, '1997 → 1998'), (1998, '1998 → 1999'), (1999, '1999 → 2000'), (2000, '2000 → 2001'), (2001, '2001 → 2002'), (2002, '2002 → 2003'), (2003, '2003 → 2004'), (2004, '2004 → 2005'), (2005, '2005 → 2006'), (2006, '2006 → 2007'), (2007, '2007 → 2008'), (2008, '2008 → 2009'), (2009, '2009 → 2010'), (2010, '2010 → 2011'), (2011, '2011 → 2012'), (2012, '2012 → 2013'), (2013, '2013 → 2014'), (2014, '2014 → 2015'), (2015, '2015 → 2016'), (2016, '2016 → 2017'), (2017, '2017 → 2018'), (2018, '2018 → 2019'), (2019, '2019 → 2020')], default=2019),
        ),
        migrations.AlterField(
            model_name='pointcodes',
            name='description',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='student',
            name='grad_year',
            field=models.IntegerField(help_text='Year of Graduation', verbose_name='Grad Year'),
        ),
        migrations.AlterField(
            model_name='student',
            name='sex',
            field=models.CharField(help_text='This field accepts any letter of the alphabet', max_length=1, verbose_name='Sex'),
        ),
        migrations.AlterField(
            model_name='student',
            name='student_num',
            field=models.PositiveIntegerField(help_text='This number must be unique as it is used to identify students', unique=True, verbose_name='Student Number'),
        ),
        migrations.DeleteModel(
            name='Awards',
        ),
        migrations.DeleteModel(
            name='Certificates',
        ),
        migrations.DeleteModel(
            name='Scholar',
        ),
        migrations.AddField(
            model_name='student',
            name='grade_10',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Grade_10'),
        ),
        migrations.AddField(
            model_name='student',
            name='grade_11',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Grade_11'),
        ),
        migrations.AddField(
            model_name='student',
            name='grade_12',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Grade_12'),
        ),
        migrations.AddField(
            model_name='student',
            name='grade_8',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Grade_8'),
        ),
        migrations.AddField(
            model_name='student',
            name='grade_9',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Grade_9'),
        ),
    ]
