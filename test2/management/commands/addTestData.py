from django.core.management.base import BaseCommand
from test2.models import Student
import random as r
import string
from django.utils import timezone

try:
    with open('names.txt') as f:
        M_first = f.readline()[:-1].strip().split()
        F_first = f.readline()[:-1].strip().split()
        last = f.readline()[:-1].strip().split()
except FileNotFoundError: 
    print("names.txt file not in current directory")
    raise FileNotFoundError


# M_first = ['Bob', 'Charlie', 'David', 'Ethan', 'Fred', 'Harry', 'Jeff', 'Larry', 'Michael', 'Terrence']
# F_first = ['Alice', 'Carol', 'Barbara', 'Diana', 'Eleanor']
# last = ['AaAa', 'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'AsDfGhJ', 'Iota', 'Kappa', 'qwerty', 'NAMENAME', 'abaca', "alberton"]

class Command(BaseCommand):
    args = "<amount> <seed>"
    help = "populates the db with test data"

    def add_arguments(self, parser):
        parser.add_argument('amount', nargs='+', type=int)

    def handle(self, *args, **kwargs):
        if len(kwargs["amount"]) > 1:
            r.seed(kwargs["amount"][1])

        for i in range(kwargs["amount"][0]):
            if r.randint(1, len(M_first) + len(F_first)) <= len(M_first):
                student = Student(first=r.choice(M_first), sex='M')
            else:
                student = Student(first=r.choice(F_first), sex='F')
            student.last = last[r.randint(0, len(last) - 1)]
            student.homeroom = "{}{}".format(str(r.randint(8, 12)).zfill(2), r.choice(string.ascii_uppercase))
            student.student_num = r.randint(1, 100000)
            student.date_added = timezone.now()
            student.save()
