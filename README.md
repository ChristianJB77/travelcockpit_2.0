# Travel Cockpit 2.0
#### Full Stack Web Developer CAPSTONE PROJECT
To finally be able to deploy my own web app, I took this Nanondegree. Based on my CS50 final project Flask app 'Travel Cockpit', I have rebuild the entire app to finally deploy it for desktop and mobile usage. As well added a travel suggestion blog functionality to share our personal 'travel secrets'.

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

### Installing Dependencies (local & hosting)

### Local

#### Python 3.9.0

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

#### Environment variables

All necessary secret keys, AUTH0 variables and JWTs are stored in setup.sh.

```bash
python;
```

#### Running the server

From within your work directory first ensure you are working using your created virtual environment and run flask server, which is running on debug mode:

```bash
python app.py;
```






Restore database for testing

 pg_restore -U postgres --dbname=travel_cockpit_test --verbose database/travel_cockpit_test.sql
 
 
 Concept & Copyrights by Christian Johann Bayerle
