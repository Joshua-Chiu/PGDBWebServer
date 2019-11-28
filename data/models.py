from django.db import models
from django.contrib.auth import get_user_model
import math
import datetime
from django.core.exceptions import ValidationError
import re


# run manage.py makemigrations data && manage.py migrate to add to db


class PlistCutoff(models.Model):
    YEAR_CHOICES = [(r, f"{r} → {r + 1}") for r in range(1984, datetime.date.today().year + 1)]
    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)

    grade_8_T1 = models.DecimalField(max_digits=5, decimal_places=3)
    grade_8_T2 = models.DecimalField(max_digits=5, decimal_places=3)

    grade_9_T1 = models.DecimalField(max_digits=5, decimal_places=3)
    grade_9_T2 = models.DecimalField(max_digits=5, decimal_places=3)

    grade_10_T1 = models.DecimalField(max_digits=5, decimal_places=3)
    grade_10_T2 = models.DecimalField(max_digits=5, decimal_places=3)

    grade_11_T1 = models.DecimalField(max_digits=5, decimal_places=3)
    grade_11_T2 = models.DecimalField(max_digits=5, decimal_places=3)

    grade_12_T1 = models.DecimalField(max_digits=5, decimal_places=3)
    grade_12_T2 = models.DecimalField(max_digits=5, decimal_places=3)

    def getCutoff(self, grade, term):
        return getattr(self, f"grade_{grade}_T{term}")

    def __str__(self):
        # return str(self.year) + "'s Principal list cutoffs"
        return f"{self.year}-{self.year + 1}'s Principal's list cutoffs"

    class Meta:
        verbose_name = 'Principal List Cutoff'
        verbose_name_plural = 'Principal List Cutoffs'


class Grade(models.Model):
    grade = models.SmallIntegerField()
    start_year = models.SmallIntegerField()
    anecdote = models.CharField(max_length=300, blank=True)

    _term1_avg = models.DecimalField(max_digits=6, decimal_places=3, null=False, default=0)
    _term2_avg = models.DecimalField(max_digits=6, decimal_places=3, null=False, default=0)

    @property
    def term1_avg(self):
        return self._term1_avg

    @term1_avg.setter
    def term1_avg(self, avg):
        self._term1_avg = avg
        self.calc_SC_total()

    @property
    def term2_avg(self):
        return self._term2_avg

    @term2_avg.setter
    def term2_avg(self, avg):
        self._term2_avg = avg
        self.calc_SC_total()

    SE_total = models.DecimalField(max_digits=6, decimal_places=3, null=False, default=0)
    AT_total = models.DecimalField(max_digits=6, decimal_places=3, null=False, default=0)
    FA_total = models.DecimalField(max_digits=6, decimal_places=3, null=False, default=0)
    SC_total = models.DecimalField(max_digits=6, decimal_places=3, null=False, default=0)

    def add_point(self, point):
        """adds point recalculate awards and sums"""
        self.point_set.add(point)
        self.calc_points_total(point.type.catagory)

    def calc_points_total(catagory):
        """update sums for a particialar catagory of point"""
        total = 0
        for p in self.point_set.filter(type__catagory="SE"):
            total += p.amount
        setattr(self, f"{catagory}_total", total)

    def calc_SC_total():
        """calculate points earned from scholar. must me on honor role (>79.5) to earn points"""
        def toPoints(avg):
            if avg >= 79.50:
                return math.sqrt(-(79 - avg)) + 1.4
            else:
                return 0
            self.SC_total = toPoints(self.term1_avg) + toPoints(self.term2_avg)


# this is mildly stupid
for i in range(8, 12+1):
    exec(f"class Grade_{i}(Grade): pass")


class Student(models.Model):
    def save(self, *args, **kwargs):
        if self.grade_8 == None:
            for i in range(8, 12+1):
                setattr(self, f"grade_{i}", globals()[f"Grade_{i}"](grade=i, start_year=self.grad_year-13+i))
                getattr(self, f"grade_{i}").save()
                print(getattr(self, f"grade_{i}"))
                print(self.grade_8)
        super(Student, self).save(*args, **kwargs)
        print(self.grade_8)

    first = models.CharField(max_length=30, verbose_name='First Name')
    last = models.CharField(max_length=30, verbose_name='Last Name')
    legal = models.CharField(max_length=30, verbose_name='Legal Name')
    sex = models.CharField(max_length=1, verbose_name="Sex", help_text="This field accepts any letter of the alphabet")
    student_num = models.PositiveIntegerField(verbose_name='Student Number', unique=True,
                                              help_text="This number must be unique as it is used to identify students")
    grad_year = models.IntegerField(verbose_name='Grad Year', help_text="Year of Graduation")
    cur_grade_num = models.IntegerField(verbose_name="current grade")
    homeroom_char = models.CharField(max_length=1, verbose_name="Homeroom letter")
    last_modified = models.DateField(auto_now=True)

    grade_12 = models.OneToOneField(Grade_12, on_delete=models.CASCADE, blank=True, null=True)
    grade_11 = models.OneToOneField(Grade_11, on_delete=models.CASCADE, blank=True, null=True)
    grade_10 = models.OneToOneField(Grade_10, on_delete=models.CASCADE, blank=True, null=True)
    grade_9 = models.OneToOneField(Grade_9, on_delete=models.CASCADE, blank=True, null=True)
    grade_8 = models.OneToOneField(Grade_8, on_delete=models.CASCADE, blank=True, null=True)

    def all_grades(self):
        return [self.grade_12, self.grade_11, self.grade_10, self.grade_9, self.grade_8]
    def get_grade(self, num):
        return getattr(self, f"grade_{num}")
    def cur_grade(self):
        return getattr(self, f"grade_{self.cur_grade_num}")

    # awards
    silver_pin = models.BooleanField(default=False)
    gold_pin = models.BooleanField(default=False)
    goldplus_pin = models.BooleanField(default=False)
    platinum_pin = models.BooleanField(default=False)
    bigblock_award = models.BooleanField(default=False)

    @property
    def homeroom(self):
        return f"{self.cur_grade_num}{self.homeroom_char}"

    @property
    def gold_pin(self):
        for i in range(8, 12 + 1):
            if self.get_cumulative_SE(i) > 29.45:
                if self.get_cumulative_SE(i) + self.get_cumulative_AT(i) + self.get_cumulative_FA(
                        i) + self.get_cumulative_SC(i) > 89.45:
                    return i
        return None

    @property
    def goldPlus_pin(self):
        if self.gold_pin:
            if self.get_cumulative_SE(10) > 29.5 and self.SE_11_total > 19.5:  # ser grade 11 > 19.5
                return 11
        return None

    @property
    def platinum_pin(self):
        if self.gold_pin:
            if (self.get_cumulative_SE(12) + self.get_cumulative_AT(12) + self.get_cumulative_FA(
                    12) + self.get_cumulative_SC(12) > 129.5 and self.get_cumulative_SE(12) > 79.5) and (
                    self.SE_11_total > 19.5 and self.SE_12_total > 19.5):  # ser 11 for
                return 12
        return None

    @property
    def bigblock_award(self):
        for i in range(8, 12 + 1):
            if self.get_cumulative_AT(i) > 59.45:
                return i
        return None

    def __str__(self):
        return "{1}, {0} ({2}, {3})".format(self.first, self.last, self.student_num, self.homeroom)


class PointCodes(models.Model):
    """each object is a posible unique type of point a student can have"""
    catagory = models.CharField(max_length=2)
    code = models.SmallIntegerField()
    description = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.catagory} {self.code}"

    class Meta:
        ordering = ['catagory', 'code']


class Points(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    type = models.ForeignKey(PointCodes, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=3)
    entered_by = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.type} {self.amount}"


# class Scholar(models.Model):
#     Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
#     term1 = models.DecimalField(max_digits=8, decimal_places=5, null=False, default=0)
#     term2 = models.DecimalField(max_digits=8, decimal_places=5, null=False, default=0)

#     def __str__(self):
#         return f"T1 {self.term1} T2 {self.term2}"


# class Awards(models.Model):
#     Student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     silver_pin = models.DateField()
#     gold_pin = models.DateField()
#     gold_plus = models.DateField()
#     platinum_pin = models.DateField()


# class Certificates(models.Model):
#     Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
#     service = models.BooleanField(default=True)
#     athletics = models.BooleanField(default=True)
#     honour = models.BooleanField(default=True)
#     fine_arts = models.BooleanField(default=True)
#     t1 = models.BooleanField(default=True)
#     t2 = models.BooleanField(default=True)
