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

commands to run:
* `python manage.py migrate`
* `python manage.py defaultGroups`
* create databse `PGDB`
* create database user `pgadmin` with password `2.71828`

## Things that should be fixed at some point

- [ ] modular non hard-coded way of making awards/pins and point catagories so more can be added/removed easily
- [ ] fix last modified date on Student so it updates when points are added
- [ ] have the archive thing import/export plists
- [ ] make the Points constructor create PointCodes if missing
- [ ] in xml make ids of objects attributes instead of child tags e.g. `<student student_num=1234>`, `<grade grade=12>`
- [ ] allow search to filter by T1 or T2 averages greater than a value
- [ ] allow students to be kept in the database but marked as inactive so they don't show up in searches or other stuff unless it's explicitly enabled in the search
- [ ] make a button to download pgdb file archive of students and delete them at the same time
- [ ] make sure incorrect inputs from users like files or forms don't cause crashes
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
* student_info page entry
* direct entry
* direct entry csv upload
