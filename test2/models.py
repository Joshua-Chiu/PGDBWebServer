from django.db import models

# run manage.py makemigrations test2 && manage.py migrate to add to db


class Student(models.Model):
    first = models.CharField(max_length=30)
    last = models.CharField(max_length=30)
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
    end_year = models.SmallIntegerField()
    anecdote = models.SlugField(max_length=300, blank=True)


class Points(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    type = models.CharField(max_length=2)
    amount = models.DecimalField(max_digits=5, decimal_places=1)


class Scholar(models.Model):
    Grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    term1 = models.DecimalField(max_digits=7, decimal_places=5)
    term2 = models.DecimalField(max_digits=7, decimal_places=5)
