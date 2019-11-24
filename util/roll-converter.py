#!/bin/env python
import sys
import csv
from math import ceil

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

        # group all rows of the same student into a list
        if row["Student Number"] == last_student:
            students[-1].append(row)
        else:
            students.append([row])
            last_student = row["Student Number"]

    honour_roll = []
    GE_roll = []

    # iterate through list of list of student classes
    for student in students:
        # exclude students with <59.5 for everything
        for c in student: 
            if c["Mark"] != "I":
                print(int(c["Mark"]))

        if any(int(c["Mark"] == "I" or c["Mark"]) < 59.5 for c in student):
            continue

        average = 0
        GE = True
        for course in student:
            average += int(course["Mark"])
            if not course["Study Habit"] in ["G", "E"]:
                GE = False

        if average > 79.5:
            honour_roll += student
        if GE:
            GE_roll += student

    print(honour_roll)
    # take out top 10% of students from honour to be plist
    top = sorted(honour_roll, key=lambda student: int(student["Mark"]))[:ceil(len(honour_roll)/10)]
    print(top)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("needs filename argument")

    filename = sys.argv[1]
    with open(filename) as file:
        files = roll_convert(file, [])
