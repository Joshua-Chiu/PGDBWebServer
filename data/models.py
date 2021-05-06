from django.db import models
from django.contrib.auth import get_user_model
import math
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
import re


# run manage.py makemigrations data && manage.py migrate to add to db


class PlistCutoff(models.Model):
    def save(self, user=None, *args, **kwargs):
        if self.id is None:
            # log creation
            log = LoggedAction(user=user, message=f"Plist Cutoff: {self.year} → {self.year + 1} created")
            log.save()
        else:
            # log creation
            log = LoggedAction(user=user, message=f"Plist Cutoff: {self.year} → {self.year + 1} changed")
            log.save()

        return super(PlistCutoff, self).save(*args, **kwargs)

    YEAR_CHOICES = [(r, f"{r} → {r + 1}") for r in range(1984, datetime.date.today().year + 1)]
    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year, unique=True)

    grade_8_T1 = models.DecimalField(max_digits=5, decimal_places=3, default=99.999)
    grade_8_T2 = models.DecimalField(max_digits=5, decimal_places=3, default=99.999)

    grade_9_T1 = models.DecimalField(max_digits=5, decimal_places=3, default=99.999)
    grade_9_T2 = models.DecimalField(max_digits=5, decimal_places=3, default=99.999)

    grade_10_T1 = models.DecimalField(max_digits=5, decimal_places=3, default=99.999)
    grade_10_T2 = models.DecimalField(max_digits=5, decimal_places=3, default=99.999)

    grade_11_T1 = models.DecimalField(max_digits=5, decimal_places=3, default=99.999)
    grade_11_T2 = models.DecimalField(max_digits=5, decimal_places=3, default=99.999)

    grade_12_T1 = models.DecimalField(max_digits=5, decimal_places=3, default=99.999)
    grade_12_T2 = models.DecimalField(max_digits=5, decimal_places=3, default=99.999)

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

    term1_GE = models.BooleanField(default=False)
    term2_GE = models.BooleanField(default=False)

    # nullification
    isnull_term1 = models.BooleanField(default=False)
    isnull_term2 = models.BooleanField(default=False)
    isnull_SE = models.BooleanField(default=False)
    isnull_AT = models.BooleanField(default=False)
    isnull_FA = models.BooleanField(default=False)
    isnull_SC = models.BooleanField(default=False)

    @property
    def term1_avg(self):
        return float(self._term1_avg)

    def set_term1_avg(self, avg, user=None):
        if avg != float(self._term1_avg):
            log = LoggedAction(user=user, message=f"term1 average of {self.student} set to {avg}")
            log.save()
            self._term1_avg = Decimal(avg)
            self.calc_SC_total()

    @property
    def term2_avg(self):
        return float(self._term2_avg)

    def set_term2_avg(self, avg, user=None):
        if avg != float(self._term2_avg):
            log = LoggedAction(user=user, message=f"term2 average of {self.student} set to {avg}")
            log.save()
            self._term2_avg = Decimal(avg)
            self.calc_SC_total()

    SE_total = models.DecimalField(max_digits=6, decimal_places=3, null=False, default=0)
    AT_total = models.DecimalField(max_digits=6, decimal_places=3, null=False, default=0)
    FA_total = models.DecimalField(max_digits=6, decimal_places=3, null=False, default=0)
    SC_total = models.DecimalField(max_digits=6, decimal_places=3, null=False, default=0)

    def add_point(self, point, user):
        """adds point recalculate awards and sums"""
        self.points_set.add(point, bulk=False)
        point.save(user)
        self.calc_points_total(point.type.catagory)

    def calc_points_total(self, catagory):
        """update sums for a particialar catagory of point"""
        total = Decimal("0.000")
        for p in self.points_set.filter(type__catagory=catagory):
            total += p.amount
        setattr(self, f"{catagory}_total", total)
        self.save()

    def calc_SC_total(self):
        """calculate points earned from scholar. must me on honor role (>79.5) to earn points"""
        def toPoints(avg):
            if avg >= 79.50:
                return math.sqrt(-(79 - avg)) + 1.4
            else:
                return 0
        self.SC_total = 0
        self.SC_total += Decimal(toPoints(self.term1_avg)) if not self.isnull_term1 else 0
        self.SC_total += Decimal(toPoints(self.term2_avg)) if not self.isnull_term2 else 0
        self.save()

    @property
    def plist_T1(self):
        return PlistCutoff.objects.get(year=self.start_year).getCutoff(self.grade, 1)

    @property
    def plist_T2(self):
        return PlistCutoff.objects.get(year=self.start_year).getCutoff(self.grade, 2)

    @property
    def honourroll(self):
        return (79.45 < self.term1_avg and 79.45 < self.term2_avg) and (self.term1_avg < self.plist_T1 or self.term2_avg < self.plist_T2)

    @property
    def principalslist(self):
        return self.plist_T1 <= self.term1_avg and self.plist_T2 <= self.term2_avg

    @property
    def cumulative_SE(self):
        return self.student.cumulative_SE(self.grade)

    @property
    def cumulative_AT(self):
        return self.student.cumulative_AT(self.grade)

    @property
    def cumulative_FA(self):
        return self.student.cumulative_FA(self.grade)

    def cumulative_SC(self):
        return self.student.cumulative_SC(self.grade)

    ''' Make cached booleans for reports
    class Awards:
        annual_se = True
        annual_at = True
        annual_sc_hr = True
        annual_sc_pl = True
        annual_fa = True
    '''
    @property
    def stu(self):
        return self.grade

# declare Grade_8 through to 12 which inherit from Grade
# this is done so that Student can have 5 oneToOnes of the 'same' type
for i in range(8, 12+1):
    exec(f"class Grade_{i}(Grade): pass")


class Student(models.Model):
    def save(self, user=None, *args, **kwargs):
        self.first = self.first.strip()
        self.last = self.last.strip()
        self.legal = self.legal.strip()
        self.sex = self.sex.strip()
        self.homeroom_str = self.homeroom_str.strip()

        # add grades if missing
        if self.grade_8 is None:
            # log creation
            log = LoggedAction(user=user, message=f"Student: {self.student_num} ({self.first} {self.last}) created")
            log.save()
            for i in range(8, 12+1):
                g = globals()[f"Grade_{i}"](grade=i, start_year=self.grad_year-13+i)
                g.save()
                setattr(self, f"grade_{i}", g)
        else:
            # log creation
            log = LoggedAction(user=user, message=f"Student: {self.student_num} ({self.first} {self.last}) changed")
            log.save()
            for i in range(8, 12+1):
                # print("setattr(getattr(self, f""), "", self.grad_year)" + str(i))
                g = getattr(self, f"grade_{i}")
                g.start_year = (self.grad_year - (12 - i)) - 1
                g.save()

        return super(Student, self).save(*args, **kwargs)

    def delete(self, user=None, *args, **kwargs):
        # log deletion
        log = LoggedAction(user=user, message=f"Student: {self.student_num} ({self.first} {self.last}) deleted")
        log.save()

        # print("delete")
        self.grade_8.delete()
        self.grade_9.delete()
        self.grade_10.delete()
        self.grade_11.delete()
        self.grade_12.delete()
        return super(Student, self).delete(*args, **kwargs)

    first = models.CharField(max_length=30, verbose_name='First Name')
    last = models.CharField(max_length=30, verbose_name='Last Name')
    legal = models.CharField(max_length=30, verbose_name='Legal Name')
    sex = models.CharField(max_length=1, verbose_name="Sex", help_text="This field accepts any letter of the alphabet")
    student_num = models.PositiveIntegerField(verbose_name='Student Number', unique=True,
                                              help_text="This number must be unique as it is used to identify students")
    grad_year = models.IntegerField(verbose_name='Grad Year', help_text="Year of Graduation")
    cur_grade_num = models.IntegerField(verbose_name="current grade")
    homeroom_str = models.CharField(max_length=15, verbose_name="Homeroom", default="#")
    active = models.BooleanField(default=True, verbose_name="Active", help_text="Designates whether this student should be treated as active. Unselect this instead of deleting students.")
    last_modified = models.DateField(auto_now=True)

    grade_12 = models.OneToOneField(Grade_12, on_delete=models.CASCADE, blank=True, null=True)
    grade_11 = models.OneToOneField(Grade_11, on_delete=models.CASCADE, blank=True, null=True)
    grade_10 = models.OneToOneField(Grade_10, on_delete=models.CASCADE, blank=True, null=True)
    grade_9 = models.OneToOneField(Grade_9, on_delete=models.CASCADE, blank=True, null=True)
    grade_8 = models.OneToOneField(Grade_8, on_delete=models.CASCADE, blank=True, null=True)

    @property
    def all_grades(self):
        return [self.grade_8, self.grade_9, self.grade_10, self.grade_11, self.grade_12]

    def get_grade(self, num):
        return getattr(self, f"grade_{num}")

    @property
    def cur_grade(self):
        return getattr(self, f"grade_{self.cur_grade_num}")

    @property
    def homeroom(self):
        return f"{self.cur_grade_num}{self.homeroom_str}"

    # Cumulative returns all points up to a certain grade

    def cumulative_SE(self, i):
        total = 0
        for g in self.all_grades[:i-7]:
            total += g.SE_total
        return total

    def cumulative_AT(self, i):
        total = 0
        for g in self.all_grades[:i-7]:
            total += g.AT_total
        return total

    def cumulative_FA(self, i):
        total = 0
        for g in self.all_grades[:i-7]:
            total += g.FA_total
        return total

    def cumulative_SC(self, i):
        total = 0
        for g in self.all_grades[:i-7]:
            total += g.SC_total
        return total

    @property
    def SE_total(self):
        return self.cumulative_SE(12)

    @property
    def AT_total(self):
        return self.cumulative_AT(12)

    @property
    def FA_total(self):
        return self.cumulative_FA(12)

    @property
    def SC_total(self):
        return self.cumulative_SC(12)

    @property
    def SE_11_12_total(self):
        return self.grade_11.SE_total + self.grade_12.SE_total
    @property
    def AT_11_12_total(self):
        return self.grade_11.AT_total + self.grade_12.AT_total
    @property
    def FA_11_12_total(self):
        return self.grade_11.FA_total + self.grade_12.FA_total
    @property
    def SC_11_12_total(self):
        return self.grade_11.SC_total + self.grade_12.SC_total

    @property
    def all_11_12_total(self):
        return self.SE_11_12_total + self.AT_11_12_total + self.FA_11_12_total + self.SC_11_12_total

    @property
    def silver_pin(self):
        for i in range(8, 12 + 1):
            if self.cumulative_SE(i) > 9.45:
                if self.cumulative_SE(i) + self.cumulative_AT(i) + self.cumulative_FA(
                        i) + self.cumulative_SC(i) > 49.45:
                    return i
        return None

    @property
    def gold_pin(self):
        for i in range(8, 12 + 1):
            if self.cumulative_SE(i) > 29.45:
                if self.cumulative_SE(i) + self.cumulative_AT(i) + self.cumulative_FA(
                        i) + self.cumulative_SC(i) > 89.45:
                    return i
        return None

    @property
    def goldPlus_pin(self):
        if self.gold_pin and self.gold_pin < 11:
            if self.cumulative_SE(10) > 29.5 and self.grade_11.SE_total > 19.5:  # ser grade 11 > 19.5
                return 11
        return None

    @property
    def platinum_pin(self):
        if self.gold_pin:
            if (self.cumulative_SE(12) + self.cumulative_AT(12) + self.cumulative_FA(
                    12) + self.cumulative_SC(12) > 129.5 and self.cumulative_SE(12) > 79.5) and (
                    self.grade_11.SE_total > 19.5 and self.grade_12.SE_total > 19.5):  # ser 11 for
                return 12
        return None

    @property
    def bigblock_award(self):
        for i in range(8, 12 + 1):
            if self.cumulative_AT(i) > 59.45:
                return i
        return None

    def __str__(self):
        return f"{self.last}, {self.first} #{self.student_num} {self.homeroom}"

    ''' Make cached booleans for reports
        class Awards:
            grad_se = True # check in top 30, then only sort the top 30
            grad_at = True
            grad_sc = True
            grad_fa = True
            grad_me = True
    '''
    class Meta:
        ordering = ['active', 'last', 'first']


class PointCodes(models.Model):
    """each object is a possible unique type of point a student can have"""
    catagory = models.CharField(max_length=2)
    code = models.SmallIntegerField()
    description = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.description} ({self.catagory}{self.code})"

    class Meta:
        ordering = ['catagory', 'code']


class Points(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    type = models.ForeignKey(PointCodes, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=3)
    entered_by = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(editable=False)

    def save(self, user=None, *args, **kwargs):
        # On save, update timestamps
        if not self.id:
            self.created = timezone.now()
        else:  # it works but i have no idea why
            # log creation
            log = LoggedAction(user=user or self.entered_by, message=f"Point: {self} added to {self.get_student().first} {self.get_student().last}")
            log.save()
        return super(Points, self).save(*args, **kwargs)

    def delete(self, user=None, *args, **kwargs):
        # log deletion
        log = LoggedAction(user=user, message=f"Point: {self} deleted from {self.get_student().first} {self.get_student().last}")
        log.save()

        return super().delete(*args, **kwargs)


    def get_student(self):
        return getattr(self.Grade, f"grade_{self.Grade.grade}").student

    def __str__(self):
        return f"{self.type} {self.amount}"


class LoggedAction(models.Model):
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    time = models.DateTimeField(auto_now=True)
    message = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user}: {self.message}"


