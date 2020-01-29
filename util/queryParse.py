from data.models import Student, Grade, Grade_8, Grade_9, Grade_10, Grade_11, Grade_12
from itertools import zip_longest
from django.db.models import Q


def parseQuery(query):
    try:
        query = query.replace(": ", ":")
        items = {} # filters like grade:12
        single_terms = [] # single like names or numbers
        # split by spaces into attributes
        for i in query.split(' '):
            term = i.split(':')
            # if length is not 2 it doesn't have a ':'
            if len(term) == 1:
                single_terms.append(term[0])
            elif len(term) == 2:
                items[term[0]] = term[1]
            else:
                continue

        students = Student.objects.all()

        # filter by active student and assume only active if not specified
        if not "active" in items or items["active"] == "yes":
            students = students.filter(active=True)
        elif items["active"] == "no":
            print("a")
            students = students.filter(active=False)

        if "active" in items:
            del items["active"]

        for t in single_terms:
            if t.isalpha():
                print(t)
                students = students.filter(Q(first__icontains=query) | Q(last__icontains=query))
            elif t.isdigit():
                students = students.filter(student_num=int(t))

        # iterate through every parameter pc/icon.pnair and check if it exists or is a student attr
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

            # grade00_term0
            elif k[:5] == "grade" and k[7:12] == "_term":
                grade = int(k[5:7])
                term = int(k[12:13])
                if v == "GE":
                    students = students.filter(**{f"grade_{grade}__term{term}_GE": True})
                elif v == "honour":
                    students = students.filter(**{f"grade_{grade}___term{term}_avg__gte": 79.5})
                elif v == "principalslist":
                    new_students = students
                    for s in students:
                        grade_obj = s.get_grade(grade)
                        if not getattr(grade_obj, f"term{term}_avg") >= getattr(grade_obj, f"plist_T{term}") and \
                                not grade_obj.isnull_SC:
                            new_students = new_students.exclude(id=s.id)
                    students = new_students

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
                        grade_object = s.get_grade(grade)
                        if not grade_object.honourroll and not grade_object.isnull_SC:
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
                        if not grade.honourroll or grade.isnull_SC:
                            new_students = new_students.exclude(id=s.id)
                    elif type == "principalslist":
                        if not grade.principalslist or grade.isnull_SC:
                            new_students = new_students.exclude(id=s.id)
                    elif "ST" in type:
                        points_num = int(type[0])
                        if not points_num == 5:
                            if not len(grade.points_set.filter(type__catagory="AT")) == points_num:
                                new_students = new_students.exclude(id=s.id)
                        else:
                            if not len(grade.points_set.filter(type__catagory="AT")) >= 5:
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
        raise e
        return Student.objects.none()
