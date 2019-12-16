#!/bin/env python
import sys
import csv
from math import ceil
import io
import shutil


class Student:
    def __init__(self, courses):
        self.courses = courses

    def __getitem__(self, item):
        return self.courses[0][item]


def write_students(students):
    csvfile = io.StringIO
    writer = csv.writer(csvfile)

    for s in students:
        row = (
            s["Student Number"],
            s["Student Legal Last Name"],
            s["Student Legal First Name"],
            s["Grade"],
            s["Homeroom"],
            str(len(s.courses)),
            str(s.average),
        )
        writer.writerow(row)


def roll_convert(csvfile, excluded_classes):
    """ take in original csv and create honour roll, plist, and GE roll"""
    reader = csv.DictReader(csvfile, delimiter=",", quotechar="\"")

    last_student = ""
    students = []
    for row in reader:
        if row["School Name"] != "Point Grey Secondary":
            continue

        if row["Course Code"] in excluded_classes:
            continue

        if row["Mark"] == "NM":
            continue

        # create a student object with a list of all courses of that student
        if row["Student Number"] == last_student:
            students[-1].courses.append(row)
        else:
            # make a new student with the courses
            students.append(Student([row]))
            last_student = row["Student Number"]

    honour_roll = []
    GE_roll = []

    # iterate through list of list of student classes
    for student in students:
        # exclude students with <59.5 for everything
        if any(c["Mark"] in ["I", ""] or int(c["Mark"]) < 59.5 for c in student.courses):
            continue

        # loop through courses and calculate average
        average = 0
        GE = True
        for course in student.courses:
            average += int(course["Mark"])
            if not course["Study Habit"] in ["G", "E"]:
                GE = False
        average /= len(student.courses)

        student.average = average
        if average > 79.5:
            honour_roll.append(student)
        if GE:
            GE_roll.append(student)

    top = sorted(honour_roll, key=lambda student: student.average)  # sort by average
    top = list(reversed(top))[:ceil(len(honour_roll) / 10)]  # take the top ten percent
    # print([s.courses[0]["Student Legal First Name"] for s in top])
    # print([s["Student Legal First Name"] for s in GE_roll])

    GE_file = write_students(GE_roll)
    honour_file = write_students(honour_roll)
    plist_file = write_students(top)

    return {"GE Roll": GE_file, "Honour Roll": honour_file, "Plist Roll": plist_file}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("needs filename argument")

    filename = sys.argv[1]
    with open(filename) as file:
        files = roll_convert(file, [])

        for name, buf in files.items():
            with open(name, 'w') as f:
                buf.seek(0)
                shutil.copyfileobj(buf, f)
