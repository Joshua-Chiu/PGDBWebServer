#!/bin/env python
import csv
import sys, datetime
import xml.etree.ElementTree as ET
import math

info = {
    "last": 0,
    "first": 1,
    "legal_name": 2,
    "number": 3,
    "homeroom": 4,
    "gender": 5,
    "year_entered": 6,
}

# (type, grade)
points_dict = {
    ("SE", 8): [87, 88, 89, 90, 91, 92, 93],
    ("AT", 8): [94, 95, 96, 97, 98, 99, 100],
    ("FA", 8): [103, 104, 105, 106, 107, 108, 109],
    ("SE", 9): [110, 111, 112, 113, 114, 115, 116],
    ("AT", 9): [117, 118, 119, 120, 121, 122, 123],
    ("FA", 9): [126, 127, 128, 129, 130, 131, 132],
    ("SE", 10): [133, 134, 135, 136, 137, 138, 139],
    ("AT", 10): [140, 141, 142, 143, 144, 145, 146],
    ("FA", 10): [149, 150, 151, 152, 153, 154, 155],
    ("SE", 11): [156, 157, 158, 159, 160, 161, 162],
    ("AT", 11): [163, 164, 165, 166, 167, 168, 169],
    ("FA", 11): [172, 173, 174, 175, 176, 177, 178],
    ("SE", 12): [179, 180, 181, 182, 183, 184, 185],
    ("AT", 12): [186, 187, 188, 189, 190, 191, 192],
    ("FA", 12): [195, 196, 197, 198, 199, 200, 201],
}

# (grade, term)
scholar_dict = {
    (8, 1): 101,
    (8, 2): 102,
    (9, 1): 124,
    (9, 2): 125,
    (10, 1): 147,
    (10, 2): 148,
    (11, 1): 170,
    (11, 2): 171,
    (12, 1): 193,
    (12, 2): 194,
}

anecdote = 81

if len(sys.argv) < 2:
    print("needs filename argument")
    exit()

file = sys.argv[1]


def get_if_exists(index, row):
    if len(row) > index:
        return row[index]
    return ""


def wdb_convert(csvfile, grade_num, start_year):
    reader = csv.reader(csvfile, delimiter=",", quotechar="\"")

    # logic for active
    active = True
    if datetime.datetime.now().month < 7:
        active = datetime.datetime.now().year <= int(start_year + 13 - grade_num)
    else:
        active = datetime.datetime.now().year < int(start_year + 13 - grade_num)


    root = ET.Element("PGDB")
    students = ET.SubElement(root, "students")

    for row in reader:
        student = ET.SubElement(students, "student")

        homeroom = get_if_exists(info["homeroom"], row)
        if not homeroom:
            homeroom = str(grade_num).zfill(2) + "#"

        if homeroom[:2].isdigit():
            homeroom_str = homeroom[2:]
        else:
            homeroom_str = homeroom

        ET.SubElement(student, "number").text = get_if_exists(info["number"], row)
        ET.SubElement(student, "current_grade").text = str(grade_num)
        ET.SubElement(student, "homeroom").text = homeroom_str
        ET.SubElement(student, "first").text = get_if_exists(info["first"], row)
        ET.SubElement(student, "last").text = get_if_exists(info["last"], row)
        ET.SubElement(student, "legal_name").text = get_if_exists(info["legal_name"], row)
        ET.SubElement(student, "sex").text = get_if_exists(info["gender"], row)
        ET.SubElement(student, "grad_year").text = str(start_year + 13 - grade_num)
        ET.SubElement(student, "active").text = "yes" if active else "no"

        grades = ET.SubElement(student, "grades")
        for g in range(8, grade_num + 1):
            grade = ET.SubElement(grades, "grade")

            ET.SubElement(grade, "grade_num").text = str(g)
            ET.SubElement(grade, "start_year").text = str(start_year - (grade_num - g))
            ET.SubElement(grade, "anecdote").text = get_if_exists(anecdote, row)

            ET.SubElement(grade, "AverageT1").text = get_if_exists(scholar_dict[(g, 1)], row) or "0.0"
            ET.SubElement(grade, "AverageT2").text = get_if_exists(scholar_dict[(g, 2)], row) or "0.0"

            points = ET.SubElement(grade, "points")
            for catagory in ["SE", "FA", "AT"]:
                for p_index in points_dict[(catagory, g)]:
                    try:
                        value = float(get_if_exists(p_index, row))
                    except:
                        continue

                    amount = math.floor(value * 1000) / 1000
                    code = round(((value * 1000) % 1) * 100)

                    point = ET.SubElement(points, "point")
                    ET.SubElement(point, "catagory").text = catagory
                    ET.SubElement(point, "code").text = str(code)
                    ET.SubElement(point, "amount").text = str(amount)

    ET.SubElement(root, "plists")

    return ET.tostring(root, encoding="utf-8", method="xml").decode()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("needs filename, grade, and grad year argument")
        exit()
    file = sys.argv[1]
    grade = int(sys.argv[2])
    grad_year = int(sys.argv[3])

    with open(file) as csvfile:
        print(wdb_convert(csvfile, grade, grad_year))
