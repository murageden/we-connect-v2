# WE CONNECT API 
[![Build Status](https://travis-ci.org/murageden/we-connect-v2.svg?branch=develop)](https://travis-ci.org/murageden/we-connect-v2) [![Coverage Status](https://coveralls.io/repos/github/murageden/we-connect-v2/badge.svg?branch=develop&service=github)](https://coveralls.io/github/murageden/we-connect-v2?branch=develop&service=github) [![Maintainability](https://api.codeclimate.com/v1/badges/8e5f9631a29feae850ba/maintainability)](https://codeclimate.com/github/murageden/we-connect-v2/maintainability)

## About
WeConnect provides a platform that brings businesses and individuals together. This platform creates awareness for businesses and gives the users the ability to write reviews about the businesses they have interacted with


## Documentation
See full documentation [here](https://weconnnect.docs.apiary.io/)


## Installation
### Required
* Git: [Installing Git on Linux, Mac OS X and Windows](https://gist.github.com/derhuerst/1b15ff4652a867391f03)
* Python 3.*: [Python Download and Installation Instructions](https://www.ics.uci.edu/~pattis/common/handouts/pythoneclipsejava/python.html)
* Pip: [Python & pip Windows installation](https://github.com/BurntSushi/nfldb/wiki/Python-&-pip-Windows-installatio)
* Virtualenv: [Installation — virtualenv 15.1.0 documentation](https://virtualenv.pypa.io/en/stable/installation/)
* Postgresql: [Installing Postgresql on Ubuntu 16.04](https://tecadmin.net/install-postgresql-server-on-ubuntu/)*
	* [PostgreSQL installation guide- Windows](http://www.postgresqltutorial.com/install-postgresql/) *
    * [PostgreSQL installation on Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04) *

    * _This example focuses on installation on Windows and Ubuntu, just as an example of how to install it on other OS's_

### Initialize a Local Repository
Run `git init` on a terminal


### Clone This Repository
Run `git clone https://github.com/murageden/we-connect-v2.git`

Run `cd we-connect-v2/`


### Set up Virtual Environment
Run the following code on a Windows terminal:

```bash
virtualenv --python=python3 venv

source venv/Scripts/activate
```
or if on Linux/Unix terminal:

```bash
virtualenv --python=python3 venv

source venv/bin/activate
```


### Install Requirements
Run `pip install -r requirements.txt`


### Run the API on Localhost
```bash
export FLASK_APP=api/routes.py

export APP_CONFIGURATION=development

export APP_SECRET=yourlongsecretkey

export DATABASE_URL=your_postgres_development_database_url

python3

>> from api.models import db

>> db.create_all()

flask run
```


The API has the following endpoints working:

* Users Endpoints:

Method | Endpoint URL | Description
|:---:|:---:|:---:|
`POST` | `/api/v2/auth/register` | Creates a new user account
`POST` | `/api/v2/auth/login` | Logs in a user
`POST` | `/api/v2/auth/logout` | Logs out a user
`POST` | `/api/v2/auth/reset-password` | Resets a user password
`POST` | `/api/v2/get-reset-token` | Returns an access token to use to reset a password


* Businesses Endpoints:

Method | Endpoint URL | Description
|:---:|:---:|:---:|
`POST` | `/api/v2/businesses` | Registers a business
`PUT` | `/api/v2/businesses/<businessId>` | Modify a business profile
`DELETE` | `/api/v2/businesses/<businessId>` | Deletes a business profile
`GET` | `/api/v2/businesses/<businessId>` | Retrieve a single business with this id
`GET` | `/api/v2/businesses` | Retrieve a list of all registered businesses
`GET` | `/api/v2/businesses/search?q=name&category=cat&location=loc` | Retrieve businesses via search function by passing name, category and location

* Reviews Endpoints:

Method | Endpoint URL | Description
|:---:|:---:|:---:|
`POST` | `/api/v2/businesses/<businessId>/reviews` | Create a review for a business
`GET` | `/api/v2/businesses/<businessId>/reviews` | Retrieve reviews for a business with this id

