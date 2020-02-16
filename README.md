# Point Grey Awards Database

[![Build Status](https://travis-ci.com/Joshua-Chiu/PGDBWebServer.svg?branch=master)](https://travis-ci.com/Joshua-Chiu/PGDBWebServer)
[![Release](https://img.shields.io/github/v/release/Joshua-Chiu/PGDBWebServer.svg)](https://github.com/Joshua-Chiu/PGDBWebServer/releases)
[![License](https://img.shields.io/github/license/Joshua-Chiu/PGDBWebServer.svg)](https://github.com/Joshua-Chiu/PGDBWebServer/blob/master/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Joshua-Chiu/PGDBWebServer)](https://github.com/Joshua-Chiu/PGDBWebServer/commits)

A database custom built for Point Grey Secondary for managing and storing student information for generating award recipients.

## Getting Started

- [Development Instructions](https://github.com/Joshua-Chiu/PGDBWebServer/wiki/Development-Server-Installation) These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
- [Deployment Instructions](https://github.com/Joshua-Chiu/PGDBWebServer/wiki/Deployment-Server-Installation) These instructions will get you a copy of the project up and running on a live system.

Software Manual: Available under the HELP tab once you connect to the server.

## Built With

* [Python](https://www.python.org/downloads/) - The Programming Language
* [Django](https://docs.djangoproject.com/en/2.2/) - The web framework for perfectionists with deadlines.
* [MySQL](https://dev.mysql.com/downloads/mysql/) - SQL Database

## Contributing

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    > 
    > A paragraph describing what changed and its impact."
    

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
* J. Chan

## Todo list

- [ ] modular non hard-coded way of making awards/pins and point catagories so more can be added/removed easily
- [ ] fix last modified date on Student so it updates when points are added
- [ ] have the archive thing import/export plists
- [ ] make the Points constructor create PointCodes if missing
- [ ] in xml make ids of objects attributes instead of child tags e.g. `<student student_num=1234>`, `<grade grade=12>`
- [ ] allow search to filter by T1 or T2 averages greater than a value
- [ ] make a button to download pgdb file archive of students and delete them at the same time
- [ ] make sure incorrect inputs from users like files or forms don't cause crashes
- [ ] when doing searches avoid python for-loops and properties; try to use sql queries instead
