from django.db import models

# run manage.py makemigrations test2 && manage.py migrate to add to db


class Student(models.Model):
    first = models.CharField(max_length=30)
    last = models.CharField(max_length=30)
    student_num = models.PositiveIntegerField()
    homeroom = models.CharField(max_length=3)

    def __str__(self):
        return "{0}, {1}, {2}, {3}".format(self.first, self.last, self.student_num, self.homeroom)


class Service(models.Model):
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    cat_herding = models.DecimalField(max_digits=5, decimal_places=1)
    surgery = models.DecimalField(max_digits=5, decimal_places=1)
    sleeping = models.DecimalField(max_digits=5, decimal_places=1)
