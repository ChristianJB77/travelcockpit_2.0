from sqlalchemy import Column, String, Integer, create_engine
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

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


"""Classes"""


class Month(db.Model):
    __tablename__ = "months"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    name_de = db.Column(db.String(), nullable=False)
    name_en = db.Column(db.String(), nullable=False)
    # Debugging printout formatting
    def __repr__(self):
        return f'<Month {self.id} {self.name_de}>'


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
    todos_list_id = db.Column(db.Integer, db.ForeignKey('todos_list.id'), nullable=False)
    #Debugging printout formatting
    def __repr__(self):
        return f'<Todo {self.id} {self.decription}>'
