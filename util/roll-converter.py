#!/bin/env python
import sys
import csv
from math import ceil
import io
import shutil


class Student:
    def __init__(self, course):
        """create a new student based on a course but doesn't add it to the course list"""
        self.courses = []
        self.GE = True
        self.number = course["Student Number"]
        self.first = course["Student Legal First Name"]
        self.last = course["Student Legal Last Name"]
        self.grade = course["Grade"]
        self.homeroom = course["Homeroom"]

    def __getitem__(self, item):
        return self.courses[0][item]


def write_students(students, add_average=True):
    csvfile = io.StringIO()
    writer = csv.writer(csvfile)

    for s in students:
        row = [
            s.number,
            s.last,
            s.first,
            s.grade,
            s.homeroom,
        ]
        # add average and the number of courses that counted towards it if it exists
        if add_average:
            row.append(str(len(s.courses)))
            row.append(round(s.average, 13))
        writer.writerow(row)

    return csvfile


def roll_convert(csvfile, excluded_courses):
    """ take in original csv and create honour roll, plist, and GE roll"""
    reader = csv.DictReader(csvfile, delimiter=",", quotechar="\"")

    last_student = ""
    students = []
    for row in reader:
        # courses not from pg count for nothing
        if row["School Name"] != "Point Grey Secondary":
            continue

        # get student object or create if missing
        if row["Student Number"] == last_student:
            student = students[-1]
        else:
            student = Student(row)
            students.append(student)
            last_student = row["Student Number"]

        student.GE = student.GE and row["Study Habit"] in ["G", "E", ""]

        if row["Mark"] == "NM":
            continue

        # don't include course if it's in the excluded list
        if any([exclude in row["Course Code"] for exclude in excluded_courses]):
            continue

        # create a student object with a list of all courses of that student
        student.courses.append(row)

    honour_roll = []
    GE_roll = [s for s in students if s.GE]

    # go through all students for honour and plist
    for student in students:
        # exclude students with <59.5 for everything
        if any(c["Mark"] in ["I", ""] or int(c["Mark"]) < 59.5 for c in student.courses):
            continue

        if len(student.courses) < 6:
            continue

        # loop through courses and calculate average
        average = 0
        for course in student.courses:
            average += int(course["Mark"])
        average /= len(student.courses)

        if average > 79.5:
            student.average = average
            honour_roll.append(student)

    top = sorted(honour_roll, key=lambda student: student.average)  # sort by average
    top = list(reversed(top))[:ceil(len(honour_roll) / 10)]  # take the top ten percent
    lowest_highest_avg = top[-1].average
    plist = [s for s in honour_roll if s.average >= lowest_highest_avg]
    # print([s.courses[0]["Student Legal First Name"] for s in top])
    # print([s["Student Legal First Name"] for s in GE_roll])

    GE_file = write_students(GE_roll, False)
    honour_file = write_students(honour_roll)
    plist_file = write_students(plist)

    return {"GE Roll.csv": GE_file, "Honour Roll.csv": honour_file, "Plist Roll.csv": plist_file}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("needs filename argument")

    filename = sys.argv[1]
    with open(filename) as file:
        files = roll_convert(file, ["YBMO", "YCPM", "YIPS"])

        for name, buf in files.items():
            with open(name, 'w') as f:
                buf.seek(0)
                shutil.copyfileobj(buf, f)
