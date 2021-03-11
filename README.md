# Travel Cockpit 2.0
#### Full Stack Web Developer CAPSTONE PROJECT
To finally be able to deploy my own web app, I took this Nanondegree. Based on my CS50 final project Flask app 'Travel Cockpit', I have rebuild the entire app to finally deploy it for desktop and mobile usage. As well added a travel suggestion blog functionality to share our personal 'travel secrets'.

## URL
https://travelcockpit.herokuapp.com/

## Purpose
As passionate travelers my wife and me were continuously looking for a central
Travel Cockpit to get all essential information necessary to plan a trip in one
tool or view. To avoid the tedious googling for each source and forgetting
always at least one important info.
Then especially in COVID-19 times it was waste of time to prepare long time
planned trips.
As nothing similar is existing, I have developed a Travel Cockpit, which makes
a spontaneous trip planning easy and efficient.

## Concept
User can search for his desired travel destination or get a suggestion of currently
warm places on the planet. The destination can be a country (German/English), city (English) or for a good
luck search any place/region.
To get inspired for new, but less mainstream targets, the user can browse the 'Travel Secrets'. The blog is managed by 2 roles: Manager (can create/edit/delete own secrets), Director (all rights).
Based on the user's search a desktop consisting of tailored widgets and direct link buttons appear. As the main target is to inform the user with all essential travel information in one view or one direct click away.

This Web (HTML) based dashboard, which works on a Smart TV, Desktop and mobile
device focuses the European and especially German traveler. Therefore the dashboard
search function works in German and English with language specific travel links.

### Functionality
Auth0 user authetification, Gunicorn WSGI, Flask API/web server with HTML/CSS frontend, Postgres SQL database and custom Python functions.


## Frontend
- HTML pages with Bootstrap powered styling and own customization in CSS
- Conditional logic for a smart and flexible HTML to adapt on existing content
with Jinja
- Icons from Font Awesome
- Background pictures from private picture collection


## Backend

### Installing Dependencies Local

#### Python 3.9.0

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)
Buildpack for Heroku deployment is included with file 'runtime.txt'

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

#### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

#### Environment variables
(Git Bash terminal)

All necessary secret keys, AUTH0 variables and JWT are stored in setup.sh. The file is added in the project commit comments and for confidentiality not uploaded to Git Hub.

```bash
source setup.sh
```

#### Running the server

From within your work directory first ensure you are working using your created virtual environment and run flask server, which is running on debug mode:

```bash
python app.py
```

#### Setup your own Auth0 3rd party authentification

1. Create a new Auth0 Account
2. Select a unique tenant domain
3. Create a new, regular web application
4. Create a new API
    - in API Settings:
        - Enable RBAC
        - Enable Add Permissions in the Access Token
5. Create new API permissions (Permission, Description):
    - `get:history-all`, Read user history of all users
    - `delete:master`, Delete selected blog post of any Manager
    - `patch:master`, Edit selected blog of any Manager
    - `delete:own`, Delete own blog post
    - `patch:own`, Edit own blog post
    - `post:blog` Post new blog post
    - `get:blog`, Read all bog posts

6. Create new roles for:
    - Manager
        - can perform all actions, except: `patch:master`, `delte:master`
    - Director
        - can perform all actions

## Testing with unittest

### Database setup for testing

Setup Postgres database:
```
dropdb travel_cockpit_test
createdb travel_cockpit_test
```
The first time you run the tests, omit the dropdb command.

With Postgres running and created database, restore a database using the 'database/210308_travel_cockpit.sql.backup' file provided. From the main work folder in terminal run:
```bash
pg_restore -U postgres --dbname=travel_cockpit_test --verbose database/travel_cockpit_test.sql
```
### Run tests

Run command in work directory (42 tests)
```
python test_app.py
```

All tests are kept in that file and should be maintained as updates are made to app functionality.

## API Reference



## Hosting - Deploying to Heroku

### Create Heroku app
In order to create the Heroku app run:
```bash
heroku create travel_cockpit
```
The output will include a git url for your Heroku application (heroku_git_url). Copy this!

Add git remote for Heroku to local repository, using the git url obtained from the last step, in terminal run: 
```bash
git remote add heroku heroku_git_url
```

### Add postgresql add on as app database
Heroku has an addon for apps for a postgresql database instance. Run this code in order to create the database and connect it to the application: 
```bash
heroku addons:create heroku-postgresql:hobby-dev --app travel_cockpit
```
Run:
```bash
heroku config --app travel_cockpit
```
in order to check the configuration variables in Heroku.

### Set configuration variables
In the browser, go to your Heroku Dashboard and access your application's settings. Reveal your config variables and start adding all the required environment variables for your project, which are stored in setup.sh.

### Push app to deploy 
```bash
git push heroku master
```

## Authors
Christian Johann Bayerle
Based on the Udacity Nanodegree 'Full Stack Web Development'

## Acknowledgements
Thanks to Udacity
 
 
Concept & Copyrights by Christian Johann Bayerle
