from django.test import TestCase
from .models import Student, Points, PlistCutoff, PointCodes
from users.models import CustomUser

fixtures = ["random_data.json"]


class StudentTestCase(TestCase):
    def setUp(self):
        Student.objects.create(
            first="Andrea ",
            last=" Aard vark",
            legal="Anne",
            sex="F ",
            student_num=1234567,
            grad_year=2020,
            cur_grade_num=11,
            homeroom_str=" X",
            active=True,
        )

    def test_students_info(self):
        # Testing Student biographical info sanitation
        andrea = Student.objects.get(student_num=1234567)
        self.assertEqual(andrea.first, "Andrea")
        self.assertEqual(andrea.last, "Aard vark")
        self.assertEqual(andrea.legal, "Anne")
        self.assertEqual(andrea.sex, "F")
        self.assertEqual(andrea.grade_12.start_year, 2019)
        self.assertEqual(andrea.homeroom, "11X")

    def test_student_changes(self):
        # Testing changes to student
        andrea = Student.objects.get(student_num=1234567)
        andrea.grad_year = 2021
        andrea.save()
        self.assertEqual(andrea.grade_12.start_year, 2020)


class PointsCodesTestCase(TestCase):
    def setUp(self):
        PointCodes.objects.create(
            catagory="AT",
            code=12,
            description="Point Code Test Case",
        )

    def test_pointcodes(self):
        AT12 = PointCodes.objects.get(code=12, catagory="AT")
        self.assertEqual(AT12.__str__(), "Point Code Test Case (AT12)")
