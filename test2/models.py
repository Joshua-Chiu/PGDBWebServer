from django.db import models

# run manage.py makemigrations test2 && manage.py migrate to add to db
# manage.py shell then from Test2.models import some stuff
# Students.objects .all() .filter(first='')

class Student(models.Model):
    first = models.CharField(max_length=30)
    last = models.CharField(max_length=30)
    student_num = models.PositiveIntegerField()
    homeroom = models.CharField(max_length=2)


class Service(models.Model):
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    cat_herding = models.DecimalField(max_digits=5, decimal_places=1)
    surgery = models.DecimalField(max_digits=5, decimal_places=1)
    sleeping = models.DecimalField(max_digits=5, decimal_places=1)
