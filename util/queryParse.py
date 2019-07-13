from data.models import Student
from itertools import zip_longest

def parseQuery(query):
    students = Student.objects.all()

    # check if there are attribute specifics e.g. first: bob
    if query.count(":") == 0:
        # search first and last if it's letters
        if query.isalpha():
            first = set(Student.objects.filter(first__icontains=query))
            last = set(Student.objects.filter(last__icontains=query))
            students = list(first.union(last))
        # else search student number
        elif query.isdigit():
            students = students.filter(student_num=query)
    else:
        query = query.replace(": ", ":")
        items = {}
        # split by spaces into attributes
        for i in query.split(' '):
            term = i.split(':')
            # if length is not 2 it doesn't have a ':'
            if len(term) != 2:
                continue
            items[term[0]] = term[1]

        # if it's an attribute of student filter by it
        for k, v in items.items():
            if hasattr(Student, k):
                val = "{0}__icontains".format(k)
                # print(val, v)
                students = students.filter(**{val: v})
            else:
                # pretend there is a grade attribute
                if k == 'grade':
                    if len(v) == 1:
                        v = '0' + v
                    # print('homeroom__contains', v)
                    students = students.filter(**{'homeroom__contains': v})
                if k == 'award':
                    new_students = students
                    if v == "silver":
                        for s in students:
                            if not s.silver_pin:
                                new_students = new_students.exclude(id=s.id)
                    if v == "gold":
                        for s in students:
                            if not s.gold_pin:
                                new_students = new_students.exclude(id=s.id)
                    if v == "goldplus":
                        for s in students:
                            if not s.goldPlus_ping:
                                new_students = new_students.exclude(id=s.id)
                    if v == "platinum":
                        for s in students:
                            if not s.platinum_pin:
                                new_students = new_students.exclude(id=s.id)
                    if v == "bigblock":
                        for s in students:
                            if not s.bigblock_award:
                                new_students = new_students.exclude(id=s.id)
                    if v == "honourrole":
                        for s in students:
                            if not s.grade_set.get(grade=s.homeroom[:2]).honourrole:
                                new_students = new_students.exclude(id=s.id)

                    students = new_students

    return students

