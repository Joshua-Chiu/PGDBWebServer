# Point Grey Awards Database

## Instructions to run

System packages:

* python ≥ 3.6
* mariadb

python packages:
refer to requirements.txt
* django
* django-mathfilters
* django-import-export
* dj-database-url
* django-session-security
* mysqlclient
* whitenoise

* create databse `PGDB`
* create user `pgadmin` with password `2.71828`
* `python manage.py migrate`
* `python manage.py defaultGroups`

## Things that should be fixed at some point

- [ ] turn homeroom attribute in student class into 2 seperate grade and homeroom attributes and make homeroom a string for special classes
- [ ] remove that giant js library from the repo
- [ ] make creating a student from admin acutally work and make grade objects for it
- [ ] modular non hard-coded way of making awards/pins and point catagories so more can be added/removed easily
- [ ] fix last modified date on Student so it updates when points are added
- [ ] remove Scholar class and make it's attributes part of Grade
- [ ] instead of Grade pointing to a student have the Student class have five grade attributes this is difficult because many things want to iterate over a list of grades
- [ ] have the archive thing import/export plists
- [ ] make the Points constructor create PointCodes if missing
- [ ] in xml make ids of objects attributes instead of child tags e.g. <student student_num=1234>, <grade grade=12>
- [ ] allow search to filter by T1 or T2 averages greater than a value
- [ ] allow students to be kept in the database but marked as inactive so they don't show up in searches or other stuff unless it's explicitly enabled
- [ ] make a button to download pgdb file archive of students and delete them at the same time
- [ ] make sure incorrect inputs from users like files or text don't cause crashes
- [ ] when doing searches avoid python for-loops and properties; try to use sql queries instead

## helpful information

wdb csvs:

* only known way to convert to csv is to open in libreoffice
* convert the csv to pgdb with converter.py
* must contain only one grade

students enter the system through:

* admin creation
* admin csv import (students only)
* .pgdb upload (students and their points)
* test data adding script

points enter the system through:

* .pgdb import
* direct entry
* direct entry csv upload
