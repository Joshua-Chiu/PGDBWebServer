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

    def __str__(self):
        return "{0}, {1}, {2}".format(self.first, self.last, self.student_num)


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
        for point in self.points_set.filter(type="SE"):
            total += point.amount
        return total

    @property
    def AT_total(self):
        total = 0
        for point in self.points_set.filter(type="AT"):
            total += point.amount
        return total

    @property
    def FA_total(self):
        total = 0
        for point in self.points_set.filter(type="FA"):
            total += point.amount
        return total

    @property
    def SC_total(self):
        total = 0
        term1 = self.scholar_set.all()[0].term1
        term2 = self.scholar_set.all()[0].term2
        
        if term1 > 95.5:
            total += 6
        elif term1 > 91.5:
            total += 5
        elif term1 > 87.5:
            total += 4
        elif term1 > 83.5:
            total += 3
        elif term1 > 79.5:
            total += 2
            
        if term2 > 95.5:
            total += 6
        elif term2 > 91.5:
            total += 5
        elif term2 > 87.5:
            total += 4
        elif term2 > 83.5:
            total += 3
        elif term2 > 79.5:
            total += 2

        return total

    # SE_total = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    # AT_total = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    # FA_total = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    # SC_total = models.DecimalField(max_digits=5, decimal_places=3, null=True)

    def __str__(self):
        return f"{self.grade} {self.start_year}"


class Points(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    type = models.CharField(max_length=2)
    code = models.SmallIntegerField()
    amount = models.DecimalField(max_digits=6, decimal_places=3)

    def __str__(self):
        return f"{self.type} {self.code} {self.amount}"


class Scholar(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    term1 = models.DecimalField(max_digits=8, decimal_places=5, null=True)
    term2 = models.DecimalField(max_digits=8, decimal_places=5, null=True)

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
