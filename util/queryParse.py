from data.models import Student, Grade, Grade_8, Grade_9, Grade_10, Grade_11, Grade_12
from itertools import zip_longest


def parseQuery(query):
    try:
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

            # iterate through every parameter pair and check if it exists or is a student attr
            for k, v in items.items():
                # pretend there is a grade attribute
                if k == 'grade':
                    students = students.filter(cur_grade_num=int(v))

                # grade_00_year
                elif k[:6] == "grade_" and k[8:] == "_year":
                    grade = int(k[6:8])
                    # grades = Grade.objects.filter(start_year=int(v)).filter(grade=grade)
                    grades = globals()[f"Grade_{grade}"].objects.filter(start_year=int(v))
                    students_with_grade = [g.student for g in grades]
                    for s in students:
                        if not s in students_with_grade:
                            students = students.exclude(id=s.id)

                # award: or award_12:
                elif "award" in k:
                    # set the allowed grade for an award to be won in to a specific grade or default to all
                    if "_" in k:
                        grade = int(k.split("_")[1])
                        grades = [grade]
                        print(grade)
                    else:
                        grades = [8, 9, 10, 11, 12]
                        grade = 0

                    # go through each student and see if the grade they won the award in is correct
                    new_students = students
                    if v == "silver":
                        for s in students:
                            if not s.silver_pin in grades:
                                new_students = new_students.exclude(id=s.id)
                    elif v == "gold":
                        for s in students:
                            if not s.gold_pin in grades:
                                new_students = new_students.exclude(id=s.id)
                    elif v == "goldplus":
                        for s in students:
                            if not s.goldPlus_pin in grades:
                                new_students = new_students.exclude(id=s.id)
                    elif v == "platinum":
                        for s in students:
                            if not s.platinum_pin in grades:
                                new_students = new_students.exclude(id=s.id)
                    elif v == "bigblock":
                        for s in students:
                            if not s.bigblock_award in grades:
                                new_students = new_students.exclude(id=s.id)
                    elif v == "honourroll":
                        for s in students:
                            if not s.get_grade(grade or int(s.cur_grade_num)).honourroll:
                                new_students = new_students.exclude(id=s.id)

                    students = new_students

                elif k == 'annual_cert':
                    new_students = students

                    type, grade_num = v.split("_")
                    for s in students:
                        grade = s.get_grade(int(grade_num))
                        if type == "SE":
                            if not (grade.SE_total > 9.5 and not grade.isnull_SE):
                                new_students = new_students.exclude(id=s.id)
                        elif type == "AT":
                            if not (grade.AT_total > 9.5 and not grade.isnull_AT):
                                new_students = new_students.exclude(id=s.id)
                        elif type == "FA":
                            if not (grade.FA_total > 9.5 and not grade.isnull_FA):
                                new_students = new_students.exclude(id=s.id)

                        elif type == "honourroll":
                            if not (grade.honourroll and not grade.isnull_honour):
                                new_students = new_students.exclude(id=s.id)
                        elif type == "principalslist":
                            if not (grade.principalslist and not grade.isnull_plist):
                                new_students = new_students.exclude(id=s.id)

                    students = new_students

                elif hasattr(Student, k):
                    val = "{0}__icontains".format(k)
                    # print(val, v)
                    students = students.filter(**{val: v})

        return students
    except Exception as e:
        print(f"oh no! failed to parse query: {query}")
        print(e)
        raise e # TODO remove
        return Student.objects.none()
