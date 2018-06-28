from django.db import models

# run manage.py makemigrations test2 && manage.py migrate to add to db


class Student(models.Model):
    first = models.CharField(max_length=30)
    last = models.CharField(max_length=30)
    legal = models.CharField(max_length=30)
    student_num = models.PositiveIntegerField()
    homeroom = models.CharField(max_length=3)
    sex = models.CharField(max_length=1)
    date_added = models.DateField()
    last_modified = models.DateField(auto_now=True)

    def __str__(self):
        return "{0}, {1}, {2}".format(self.first, self.last, self.student_num)


class Grade(models.Model):
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.SmallIntegerField()
    start_year = models.SmallIntegerField()
    anecdote = models.CharField(max_length=300, blank=True)

    SE_total = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    AT_total = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    FA_total = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    SC_total = models.DecimalField(max_digits=5, decimal_places=3, null=True)

    def __str__(self):
        return f"{self.grade} {self.start_year}"


class Points(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    type = models.CharField(max_length=2)
    code = models.SmallIntegerField()
    amount = models.DecimalField(max_digits=5, decimal_places=1)

    def __str__(self):
        return f"{self.type} {self.code} {self.amount}"


class Scholar(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    term1 = models.DecimalField(max_digits=7, decimal_places=5)
    term2 = models.DecimalField(max_digits=7, decimal_places=5)

    def __str__(self):
        return f"T1 {self.term1} T2 {self.term2}"


class PointCodes(models.Model):
    type = models.CharField(max_length=2)
    code = models.SmallIntegerField()
    description = models.CharField(max_length=20)


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
