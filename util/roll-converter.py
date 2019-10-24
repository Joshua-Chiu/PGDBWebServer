import sys

def roll_convert(file):
    reader = csv.DictReader(csvfile, delimiter=",", quotechar="\"")

    last_student = ""
    students = []
    for row in reader:
        if all([c in row["whatever"] for c in ["a", "b"]])

        if row["Student Number"] == last_student:
            students[-1].append(row)
        else:
            students.append([row])
            last_student = row["Student Number"]

    for student in students:
        if students["School Name"] != "Point Grey":
            continue


if __name__ == "__main__":
    if len(sys.args) != 2:
        print("needs filename argument")

    filename = sys.argv[1]
    with open(filename) as file:
        files = roll_convert(file)
