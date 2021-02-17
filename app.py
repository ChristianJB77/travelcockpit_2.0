# Libraries
import json
import os
from flask import Flask, render_template, request, redirect, jsonify, \
                    abort, url_for, session, _request_ctx_stack
from flask_cors import CORS
from six.moves.urllib.parse import urlencode
import sys

# Constants for Auth0 from constants.py, secret keys stores as config variables
import auth.constants as constants
# Database model
from database.models import setup_db, db_drop_and_create_all, Todo_List, Todo, db
# Auth0 authentication
from auth.auth import AuthError, requires_auth, auther


def create_app(test_config=None):

    app = Flask(__name__)
    app.debug = True
    app.secret_key = os.environ['SECRET_KEY']

    setup_db(app)
    CORS(app)
    #Auth0 initalizing from auth.py
    auth_dict = auther(app)
    auth0 = auth_dict["auth0"]
    AUTH0_CALLBACK_URL = auth_dict["url"]
    AUTH0_AUDIENCE = auth_dict["audi"]
    AUTH0_CLIENT_ID = auth_dict['id']
    

    """Uncomment for re-initalizing database, watch out: Will delete entire db"""


    # db_drop_and_create_all()


    """Auth0 login / logout"""


    @app.route('/')
    def home():
        return render_template('home.html')


    @app.route('/callback')
    def callback_handling():
        # Get authorization token
        token = auth0.authorize_access_token()
        access_token = token['access_token']
        # Store access token in Flask session
        session[constants.ACCESS_TOKEN] = access_token

        resp = auth0.get('userinfo')
        userinfo = resp.json()

        session[constants.JWT_PAYLOAD] = userinfo
        session[os.environ['PROFILE_KEY']] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }

        return redirect('/dashboard')


    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL,
                                        audience=AUTH0_AUDIENCE)


    @app.route('/logout')
    def logout():
        session.clear()
        params = {'returnTo': url_for('home', _external=True),
                    'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


    """TODOS"""

    """Todo App main site / index"""
    @app.route("/dashboard")
    @requires_auth('get:tasks')
    def dashboard(jwt):
        return redirect(url_for('get_todo_list', todos_list_id=1))

    """New task"""
    @app.route("/todos/create", methods=['POST'])
    @requires_auth('post:task')
    def create_todos(jwt):
        #Default error is false
        error = False
        #Site content body dict to store data before database is closed
        body = {}
        try:
            td = request.get_json()['todo_body']
            list_id = request.get_json()['list_id_body']
            todo = Todo(description=td, completed=False, todos_list_id=list_id)
            db.session.add(todo)
            db.session.commit()
            body['id'] =  todo.id
            body['completed'] = todo.completed
            body['description'] = todo.description
            body['todos_list_id'] = todo.todos_list_id
        except:
            #If error, rollback -> Don't insert in database
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            #Best practice to close database after operations
            db.session.close()
        if not error:
            #If no error, then return body dict
            return jsonify(body)


    """Delete task"""
    @app.route("/todos/<todo_id>/delete", methods=['DELETE'])
    @requires_auth('delete:task')
    def delete_todo(jwt, todo_id):
        try:
            Todo.query.filter_by(id=todo_id).delete()
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({ 'success': True })


    """Check completed task"""
    @app.route("/todos/<todo_id>/set-completed", methods=['POST'])
    @requires_auth('post:task-completed')
    def completed_todo(jwt, todo_id):
        try:
            cd = request.get_json()['completed_body']
            todo = Todo.query.get(todo_id)
            todo.completed = cd
            completed = Todo(completed=cd)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return redirect("/dashboard")


    """LISTS"""
    """New list"""
    @app.route("/lists/create", methods=['POST'])
    @requires_auth('post:task')
    def create_lists(jwt):
        #Default error is false
        error = False
        #Site content body dict to store data before database is closed
        body = {}
        try:
            ls = request.get_json()['list_body']
            list = Todo_List(list_name=ls, completed=False)
            db.session.add(list)
            db.session.commit()
            body['id'] =  list.id
            body['completed'] = list.completed
            body['list_name'] = list.list_name
        except:
            #If error, rollback -> Don't insert in database
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            #Best practice to close database after operations
            db.session.close()
        if not error:
            #If no error, then return body dict
            return jsonify(body)


    """Delete list and its children"""
    @app.route("/lists/<list_id>/delete", methods=['DELETE'])
    @requires_auth('delete:task')
    def delete_list(jwt, list_id):
        try:
            list = Todo_List.query.get(list_id)
            #Delete all todos of selected todos list by class relationship
            for todo in list.todos:
                db.session.delete(todo)

            db.session.delete(list)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({ 'success': True })


    """Check completed list and its children"""
    @app.route("/lists/<list_id>/set-completed", methods=['POST'])
    @requires_auth('post:task-completed')
    def completed_list(jwt, list_id):
        try:
            list = Todo_List.query.get(list_id)
            cd = request.get_json()['completed_body']
            #Check all todos of selected todos list by class relationship
            for todo in list.todos:
                todo.completed = cd
                completed = Todo(completed=cd)

            list.completed = cd
            completed = Todo_List(completed=cd)

            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return redirect("/dashboard")


    """Todo list view"""
    @app.route('/lists/<todos_list_id>')
    @requires_auth('get:tasks')
    def get_todo_list(jwt, todos_list_id):
        todo_lists = Todo_List.query.order_by('id').all()
        active_todo_list = Todo_List.query.get(todos_list_id)
        todos = Todo.query.filter_by(todos_list_id=todos_list_id).order_by('id').all()
        # Get Auth0 userinfo
        userinfo=session[os.environ['PROFILE_KEY']]
        userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD])

        return render_template("dashboard.html", lists=todo_lists,
                                active_todo_list=active_todo_list, data=todos,
                                userinfo=userinfo,
                                userinfo_pretty=userinfo_pretty)

    return app

app = create_app()

if __name__ == '__main__':
    app.run()
