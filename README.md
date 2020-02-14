# Point Grey Awards Database

[![Build Status](https://travis-ci.com/Joshua-Chiu/PGDBWebServer.svg?branch=master)](https://travis-ci.com/Joshua-Chiu/PGDBWebServer)


A database custom built for PGSS for managing and storing student information for generating award recipients.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

System packages:
* Python ≥ 3.6
* mariaDB, MySQL or PostgresSQL

### Installation

A step by step series of examples that tell you how to get a development env running

Create the PGDB database
```
create databse PGDB;
```

Create user in the SQL database
```
CREATE USER 'pgadmin'@'localhost' IDENTIFIED BY '2.718281';
GRANT ALL PRIVILEGES ON PGDB.* TO 'pgadmin'@'localhost';
```

Install all python dependencies
```
pip install -r requirements.txt
```

Migrate columns to your SQL database
```
python manage.py migrate
```

Run the development server
```
python manage.py runserver
```

The output should be
```
    System check identified no issues (0 silenced).
    December 14, 2019 - 16:12:27
    Django version 2.2.7, using settings 'PGDBWebServer.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.
```

Manual: Available under the HELP page

## Deployment

Set ```Debug = False``` in settings.py

## Built With

* [Python](https://www.python.org/downloads/) - The Programming Language
* [Django](https://docs.djangoproject.com/en/2.2/) - The web framework for perfectionists with deadlines.
* [MySQL](https://dev.mysql.com/downloads/mysql/) - SQL Database

## Contributing

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    > 
    > A paragraph describing what changed and its impact."
    
### Code of Conduct

#### Our Pledge

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to making participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, gender identity and expression, level of experience,
nationality, personal appearance, race, religion, or sexual identity and
orientation.

#### Our Standards

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or
advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic
  address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

#### Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable
behavior and are expected to take appropriate and fair corrective action in
response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or
reject comments, commits, code, wiki edits, issues, and other contributions
that are not aligned to this Code of Conduct, or to ban temporarily or
permanently any contributor for other behaviors that they deem inappropriate,
threatening, offensive, or harmful.

#### Scope

This Code of Conduct applies both within project spaces and in public spaces
when an individual is representing the project or its community. Examples of
representing a project or community include using an official project e-mail
address, posting via an official social media account, or acting as an appointed
representative at an online or offline event. Representation of a project may be
further defined and clarified by project maintainers.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/Joshua-Chiu/PGDBWebServer/tags). 

## Authors

* **Mason Anderson** - *Django/Server side development* - [mason-anderson](https://github.com/mason-anderson)
* **Joshua Chiu** - *HTML/CSS UI frontend development* - [Joshua-Chiu](https://github.com/Joshua-Chiu)

See also the list of [contributors](https://github.com/Joshua-Chiu/PGDBWebServer/contributors) who participated in this project.

## License

This project is licensed under the terms of the MIT license.

## Acknowledgments

* N. Petheriotis

## Todo list

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

## Helpful Information

WDB .csv:

* only known way to convert to csv is to open in libreoffice
* convert the csv to pgdb with converter.py
* must contain only one grade

Students enter the system through:

* admin creation
* admin csv import (students only)
* .pgdb upload (students and their points)
* test data adding script

Points enter the system through:

* .pgdb import
* student_info page entry
* direct entry
* direct entry csv upload
