from django.db import models
import math
import datetime
# run manage.py makemigrations test2 && manage.py migrate to add to db


class PlistCutoff(models.Model):
    YEAR_CHOICES = [(r,r) for r in range(1984, datetime.date.today().year+1)]
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

    def __str__(self):
        return str(self.year) + "'s Principal list cutoffs"


class Student(models.Model):
    first = models.CharField(max_length=30)
    last = models.CharField(max_length=30)
    legal = models.CharField(max_length=30)
    student_num = models.PositiveIntegerField()
    homeroom = models.CharField(max_length=3)
    sex = models.CharField(max_length=1)
    date_added = models.DateField()
    last_modified = models.DateField(auto_now=True)

    # please help me there are far too many functions and i just keep adding more

    def get_cumulative_SE(self, current_grade):
        total = 0
        for grade in self.grade_set.all():
            if grade.grade <= current_grade:
                total += grade.SE_total
        return total

    def get_cumulative_AT(self, current_grade):
        total = 0
        for grade in self.grade_set.all():
            if grade.grade <= current_grade:
                total += grade.AT_total
        return total

    def get_cumulative_FA(self, current_grade):
        total = 0
        for grade in self.grade_set.all():
            if grade.grade <= current_grade:
                total += grade.FA_total
        return total

    def get_cumulative_SC(self, current_grade):
        total = 0
        for grade in self.grade_set.all():
            if grade.grade <= current_grade:
                total += grade.SC_total
        return total

    @property
    def SE_11_total(self):
        total = self.grade_set.get(grade=11).SE_total
        return total

    @property
    def SE_12_total(self):
        total = self.grade_set.get(grade=12).SE_total
        return total

    @property
    def all_11_12_total(self):
        total = self.SC_11_12_total
        total += self.SE_11_12_total
        total += self.FA_11_12_total
        total += self.SC_11_12_total
        return total

    @property
    def SE_11_12_total(self):
        total = self.grade_set.get(grade=11).SE_total + self.grade_set.get(grade=12).SE_total
        return total

    @property
    def AT_11_12_total(self):
        total = self.grade_set.get(grade=11).AT_total + self.grade_set.get(grade=12).AT_total
        return total

    @property
    def FA_11_12_total(self):
        total = self.grade_set.get(grade=11).FA_total + self.grade_set.get(grade=12).FA_total
        return total

    @property
    def SC_11_12_total(self):
        total = self.grade_set.get(grade=11).SC_total + self.grade_set.get(grade=12).SC_total
        return total

    @property
    def average_11_12(self):
        return (self.grade_set.get(grade=11).scholar_set.all()[0].term1 + self.grade_set.get(grade=11).scholar_set.all()[0].term2 + self.grade_set.get(grade=12).scholar_set.all()[0].term1 + self.grade_set.get(grade=12).scholar_set.all()[0].term2) / 4

    @property
    def silver_pin(self):
        for i in range(8, 12+1):
            if self.get_cumulative_SE(i) > 9.45:
                if self.get_cumulative_SE(i) + self.get_cumulative_AT(i) + self.get_cumulative_FA(i) + self.get_cumulative_SC(i) > 49.45:
                    return i
        return None

    @property
    def gold_pin(self):
        for i in range(8, 12+1):
            if self.get_cumulative_SE(i) > 29.45:
                if self.get_cumulative_SE(i) + self.get_cumulative_AT(i) + self.get_cumulative_FA(i) + self.get_cumulative_SC(i) > 89.45:
                    return i
        return None

    @property
    def goldPlus_pin(self):
        if (self.gold_pin):
            if (self.get_cumulative_SE(11) + self.get_cumulative_AT(11) + self.get_cumulative_FA(11) + self.get_cumulative_SC(11) > 90):
                return 11
        return None

    @property
    def platinum_pin(self):
        if (self.goldPlus_pin):
            if self.get_cumulative_SE(12) + self.get_cumulative_AT(12) + self.get_cumulative_FA(12) + self.get_cumulative_SC(12) > 110:
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


class Grade(models.Model):
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.SmallIntegerField()
    start_year = models.SmallIntegerField()
    anecdote = models.CharField(max_length=300, blank=True)

    @property
    def cumulative_SE(self):
        return self.Student.get_cumulative_SE(self.grade)

    @property
    def cumulative_AT(self):
        return self.Student.get_cumulative_AT(self.grade)

    @property
    def cumulative_FA(self):
        return self.Student.get_cumulative_FA(self.grade)

    @property
    def cumulative_SC(self):
        return self.Student.get_cumulative_SC(self.grade)

    @property
    def SE_total(self):
        total = 0
        for point in self.points_set.filter(type__catagory="SE"):
            total += point.amount
        return float(total)

    @property
    def AT_total(self):
        total = 0
        for point in self.points_set.filter(type__catagory="AT"):
            total += point.amount
        return float(total)

    @property
    def FA_total(self):
        total = 0
        for point in self.points_set.filter(type__catagory="FA"):
            total += point.amount
        return float(total)

    @property
    def SC_total(self):

        def toPoints(avg):
            if avg >= 79.50:
                return math.sqrt(-(79-avg)) + 1.4
            else:
                return 0

        return toPoints(self.scholar_set.all()[0].term1) + toPoints(self.scholar_set.all()[0].term2)

    @property
    def honourrole(self):
        return self.SC_total != 0

    @property
    def principalslist(self):
        return self.scholar_set.all()[0].term1 > PlistCutoff.objects.get(year=self.start_year) and\
               self.scholar_set.all()[0].term2 > PlistCutoff.get(year=self.start_year)

    def __str__(self):
        return f"{self.grade} {self.start_year}"


class PointCodes(models.Model):
    catagory = models.CharField(max_length=2)
    code = models.SmallIntegerField()
    description = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.catagory} {self.code}"


class Points(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    type = models.ForeignKey(PointCodes, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=3)

    def __str__(self):
        return f"{self.type} {self.amount}"


class Scholar(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    term1 = models.DecimalField(max_digits=8, decimal_places=5, null=True)
    term2 = models.DecimalField(max_digits=8, decimal_places=5, null=True)

    def __str__(self):
        return f"T1 {self.term1} T2 {self.term2}"


class Awards(models.Model):
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    silver_pin = models.DateField()
    gold_pin = models.DateField()
    gold_plus = models.DateField()
    platinum_pin = models.DateField()


class Certificates(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    service = models.BooleanField()
    athletics = models.BooleanField()
    honour = models.BooleanField()
    p_list = models.BooleanField()
    fine_arts = models.BooleanField()

