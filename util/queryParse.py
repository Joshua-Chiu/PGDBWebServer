from data.models import Student, Grade
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
                if hasattr(Student, k):
                    val = "{0}__icontains".format(k)
                    # print(val, v)
                    students = students.filter(**{val: v})
                else:
                    # pretend there is a grade attribute
                    if k == 'grade':
                        students = students.filter(cur_grade_num=int(v))

                    # grade_00_year
                    elif k[:6] == "grade_" and k[8:] == "_year":
                        grade = int(k[6:8])
                        grades = Grade.objects.filter(start_year=int(v)).filter(grade=grade)
                        students_with_grade = [g.Student for g in grades]
                        for s in students:
                            if not s in students_with_grade:
                                students = students.exclude(id=s.id)

                    # award: or award_12:
                    elif "award" in k:
                        if "_" in k:
                            grade = int(k.split("_")[1])
                            grades = [grade]
                        else:
                            grades = [8, 9, 10, 11, 12]
                            grade = 0

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
                                if not s.grade_set.get(grade=(grade or int(s.cur_grade_num))).honourroll:
                                    new_students = new_students.exclude(id=s.id)

                        students = new_students

                    elif k == 'annual_cert':
                        new_students = students

                        type, grade_num = v.split("_")
                        for s in students:
                            grade = s.get_grade(int(grade_num))
                            if type == "SE":
                                if not (grade.SE_total > 9.5 and grade_set.certificates_set.first().service):
                                    new_students = new_students.exclude(id=s.id)
                            elif type == "AT":
                                if not (grade.AT_total > 9.5 and grade_set.certificates_set.first().athletics):
                                    new_students = new_students.exclude(id=s.id)
                            elif type == "FA":
                                if not (grade.FA_total > 9.5 and grade_set.certificates_set.first().fine_arts):
                                    new_students = new_students.exclude(id=s.id)

                            elif type == "honourroll":
                                if not (grade.honourroll and grade_set.certificates_set.first().honour):
                                    new_students = new_students.exclude(id=s.id)
                            elif type == "principalslist":
                                if not (grade.principalslist and grade_set.certificates_set.first().honour):
                                    new_students = new_students.exclude(id=s.id)

                        students = new_students

        return students
    except Exception as e:
        print(f"oh no failed to parse query: {query}")
        print(e)
        raise e
        return Student.objects.none()
