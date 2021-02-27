from sqlalchemy import Column, create_engine, String, Integer, DateTime
from flask_sqlalchemy import SQLAlchemy
import json
import os


database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


"""APP"""


class Month(db.Model):
    __tablename__ = "months"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    name_de = db.Column(db.String(), nullable=False)
    name_en = db.Column(db.String(), nullable=False)
    # Debugging printout formatting
    def __repr__(self):
        return f'<Month {self.id} {self.name_de}>'

class DataHubCountries(db.Model):
    __tablename__ = "data_hub_countries"
    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String())
    official_name_english = db.Column(db.String())
    iso3166_1_alpha_2 = db.Column(db.String())
    iso316_1_alpha_3 = db.Column(db.String())
    dial = db.Column(db.String())
    iso4217_currency_aplhabetic_code = db.Column(db.String())
    iso4217_currency_country_name = db.Column(db.String())
    iso4217_currency_name = db.Column(db.String())
    capital = db.Column(db.String())
    continent = db.Column(db.String())
    tld = db.Column(db.String())
    # Debugging printout formatting
    def __repr__(self):
        return f'<DataHubCountries {self.id} {self.country_name}>'

class CountriesTranslate(db.Model):
    __tablename__ = "countries_translate"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(), nullable=False)
    en = db.Column(db.String(), nullable=False)
    de = db.Column(db.String(), nullable=False)
    # Debugging printout formatting
    def __repr__(self):
        return f'<CountriesTranslate {self.id} {self.code}>'

class Cities(db.Model):
    __tablename__ = "ctities"
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(), nullable=False)
    city_ascii = db.Column(db.String(), nullable=False)
    country = db.Column(db.String())
    iso2 = db.Column(db.String(), nullable=False)
    state = db.Column(db.String())
    # Debugging printout formatting
    def __repr__(self):
        return f'<Cities {self.id} {self.city}>'


class ReiseKlima(db.Model):
    __tablename__ = "reise_klima"
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(), nullable=False)
    # Debugging printout formatting
    def __repr__(self):
        return f'<ReiseKlima {self.id} {self.destination}>'

class CovidCountries(db.Model):
    __tablename__ = "covid_countries"
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(), nullable=False)
    slug = db.Column(db.String(), nullable=False)
    iso2 = db.Column(db.String(), nullable=False)
    # Debugging printout formatting
    def __repr__(self):
        return f'<CovidCountries {self.id} {self.country}>'


"""USERDATA"""


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False)
    name = db.Column(db.String())
    location_iso2 = db.Column(db.String())
    user_history = db.relationship('UserHistory', backref='user', lazy=True)
    # Debugging printout formatting
    def __repr__(self):
        return f'<User {self.id} {self.email}>'

class UserHistory(db.Model):
    __tablename__ = "user_history"
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Debugging printout formatting
    def __repr__(self):
        return f'<UserHistory {self.id} {self.destination}>'

"""TODOS"""


#Parent table for todos list
class Todo_List(db.Model):
    __tablename__ = "todos_list"
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos = db.relationship('Todo', backref='list', lazy=True)
    #Debugging printout formatting
    def __repr__(self):
        return f'<Todo {self.id} {self.list_name}>'

#Child table for todos -> one to many relationship
class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos_list_id = db.Column(db.Integer, db.ForeignKey('todos_list.id'),
                    nullable=False)
    #Debugging printout formatting
    def __repr__(self):
        return f'<Todo {self.id} {self.decription}>'
