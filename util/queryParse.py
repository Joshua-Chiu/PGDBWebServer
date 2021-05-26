from data.models import Student, Grade_8, Grade_9, Grade_10, Grade_11, Grade_12
from itertools import zip_longest
from django.db.models import Q
from django.http import QueryDict


def get_year_keys(dict):
    '''checks if there are grade_XX_year:0000 keys'''
    for key, val in dict.items():
        if key[:6] == "grade_" and key[8:] == "_year":
            return key
    return False


def get_term_keys(dict):
    '''checks if there are grade_XX_term:X keys'''
    for key, val in dict.items():
        if key[:6] == "grade_" and key[8:] == "_term":
            return key
    return False


def get_point_keys(dict):
    '''checks if there are grade_XX_point:XX_X keys'''
    for key, val in dict.items():
        if key[:6] == "grade_" and key[8:] == "_point":
            return key
    return False


def get_grad_keys(dict):
    '''checks if there are grad award keys'''
    for key, val in dict.items():
        if "award" in key:
            return key
    return False


def parseQuery(query):
    try:
        if ":" not in query:
            query = query.split()
            if len(query) == 1 and query[0].isdigit():
                return Student.objects.filter(student_num=query[0])
            elif len(query) == 1:
                return Student.objects.filter(Q(first__icontains=query[0]) | Q(last__icontains=query[0]))
            elif len(query) >= 2:
                return Student.objects.filter(Q(first=query[0]) | Q(legal=query[0]), last=query[1])
            else:
                return QueryDict('', mutable=True)  # return no students

        query = query.replace(": ", ":")
        print(f"Processing query: {query}")
        items = {}  # filters like grade:12
        for i in query.split():
            items[i.split(":")[0]] = i.split(":")[1]
        print(items)

        # Filtering Active students
        if items.get("active", "both") == "yes":  # query active students only, default query active only
            students = Student.objects.filter(active=True)
        elif items.get("active", "both") == "no":
            students = Student.objects.filter(active=False)
        else:
            students = Student.objects.all()

        # Process grade keys
        if "grade" in items:
            if items['grade'].isdigit:
                students = students.filter(cur_grade_num=int(items['grade']))

        # Process year keys
        if get_year_keys(items):
            key = get_year_keys(items)
            year = items[key]
            grade = int(key[6:8])
            grades = globals()[f"Grade_{grade}"].objects.filter(start_year=int(year))
            students_with_grade = [g.student for g in grades]
            for s in students:
                if not s in students_with_grade:
                    students = students.exclude(id=s.id)

        # Process grade term keys
        if get_term_keys(items):
            key = get_term_keys
            grade = int(key[5:7])
            term = int(key[12:13])
            v = items.get(key)
            if v == "GE":
                students = students.filter(**{f"grade_{grade}__term{term}_GE": True})
            elif v == "honour":
                students = students.filter(**{f"grade_{grade}___term{term}_avg__gte": 79.5})
                students = students.filter(**{f"grade_{grade}__isnull_term{term}": False})

                # exclude students on plist
                new_students = students
                for s in students:
                    grade_obj = s.get_grade(grade)
                    if not getattr(grade_obj, f"term{term}_avg") < getattr(grade_obj, f"plist_T{term}"):
                        new_students = new_students.exclude(id=s.id)
                students = new_students

            elif v == "principalslist":
                students = students.filter(**{f"grade_{grade}__isnull_term{term}": False})
                new_students = students
                for s in students:
                    grade_obj = s.get_grade(grade)
                    if not getattr(grade_obj, f"term{term}_avg") >= getattr(grade_obj, f"plist_T{term}") and \
                            not grade_obj.isnull_SC:
                        new_students = new_students.exclude(id=s.id)
                students = new_students

        # Process annual_certs
        if "annual_cert" in items:
            new_students = students
            v = items['annual_cert']

            type, grade_num = v.split("_")
            for s in students:
                grade = s.get_grade(int(grade_num))
                if type == "SE":
                    if not (grade.SE_total >= 9.5 and not grade.isnull_SE):
                        new_students = new_students.exclude(id=s.id)
                elif type == "AT":
                    if not (grade.AT_total >= 9.5 and not grade.isnull_AT):
                        new_students = new_students.exclude(id=s.id)
                elif type == "FA":
                    if not (grade.FA_total >= 9.5 and not grade.isnull_FA):
                        new_students = new_students.exclude(id=s.id)

                elif type == "honourroll":
                    if (not grade.honourroll or grade.isnull_SC) or grade.principalslist:
                        new_students = new_students.exclude(id=s.id)
                elif type == "principalslist":
                    if not grade.principalslist or grade.isnull_SC:
                        new_students = new_students.exclude(id=s.id)
                elif "ST" in type:
                    if type[0].isdigit():
                        points_num = int(type[0])
                        if not len(grade.points_set.filter(type__catagory="AT")) == points_num:
                            new_students = new_students.exclude(id=s.id)
                    else:
                        if type[0] == "3+":
                            if not len(grade.points_set.filter(type__catagory="AT")) >= 3:
                                new_students = new_students.exclude(id=s.id)
                        else:
                            if not len(grade.points_set.filter(type__catagory="AT")) >= 5:
                                new_students = new_students.exclude(id=s.id)

            students = new_students

        # Process grad_reports
        if get_grad_keys(items):
            k = get_grad_keys(items)
            v = items[get_grad_keys(items)]
            #  set the allowed grade for an award to be won in to a specific grade or default to all
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

        # Process lookup reverse requests:
        if get_point_keys(items):
            key = get_point_keys(items)
            val = items[key].split("_")
            grade = int(key[6:8])

            for s in students:
                g = s.get_grade(grade)
                if not g.points_set.filter(type__catagory=val[0], type__code=val[1]).exists():
                    students = students.exclude(id=s.id)





        # lookup by attributes - won't be implemented

        return students
    except Exception as e:
        print(f"oh no! failed to parse query: {query}")
        print(e)
        raise e
        # return Student.objects.none()
