# Point Grey Awards Database

## instructions to run
system packages:
* python>3.6
* mariadb

python packages:
* django
* django-mathfilters
* django-import-export
* dj-database-url
* django-session-security
* mysqlclient
* whitenoise

* create databse `PGDB`
* create user `pgadmin` with password `2.71828`

## things that should be fixed at some point

- [ ] turn homeroom attribute in student class into 2 seperate grade and homeroom letter attributes
- [ ] remove the entirety JQuery from the git repository
- [ ] modular non hard-coded way of making awards/pins and point catagories so more can be added/removed easily
- [ ] fix last modified date on Student so it updates when points are added
- [ ] remove Scholar class and make it's attributes part of Grade
- [ ] instead of Grade pointing to a student have the Student class have five grade attributes
- [ ] have the archive thing import/export plists
- [ ] make the Points constructor create PointCodes if missing
- [ ] in xml make ids of objects attributes instead of child tags e.g. <student student_num=1234>, <grade grade=12>

