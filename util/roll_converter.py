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
        self.average = 0.0
        self.number = course["Student Number"]
        self.grade = int(course["Grade"])
        self.term_null = False


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

        # don't include course if it's in the excluded list
        if any([exclude in row["Course Code"] for exclude in excluded_courses]):
            continue

        if not row["Mark"].isnumeric():
            continue
        # create a student object with a list of all courses of that student
        student.courses.append(row)

    # go through all students for honour and plist
    for student in students:
        # loop through courses and calculate average
        average = 0
        for course in student.courses:
            average += int(course["Mark"])

        if student.courses:
            average /= len(student.courses)
        student.average = average

        # mark null if less than 6 courses
        student.term_null = len(student.courses) < 6

    plists = []
    for g in range(8, 13):
        top = [s for s in students if int(s.grade) == g]

        top.sort(key=lambda s: s.average)  # sort by average
        top = list(reversed(top))[:ceil(len(top) / 10)]  # take the top ten percent
        cutoff = top[-1].average
        plists.append((g, cutoff))

    return plists, students
