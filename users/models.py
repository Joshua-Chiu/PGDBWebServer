from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    autofocus = models.IntegerField(default=1, choices=[(1, 'Service'), (2, 'Athletics'), (3, 'Fine Arts'), (4, 'Scholar T1'), (5, 'Scholar T2')])

    def __str__(self):
        return self.first_name + " " + self.last_name
