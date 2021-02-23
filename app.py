# Libraries
import json
import os
from flask import Flask, render_template, request, redirect, jsonify, \
                    abort, url_for, session, _request_ctx_stack
from flask_cors import CORS
from six.moves.urllib.parse import urlencode
import sys
import datetime

# Constants for Auth0 from constants.py, secret keys stores as config variables
import auth.constants as constants
# Database model
from database.models import setup_db, db, Todo_List, Todo, Month, User, \
                            UserHistory
# Auth0 authentication
from auth.auth import AuthError, requires_auth, requires_auth_rbac, auther

# My features
from features.input_classifier import check, loc_class


def create_app(test_config=None):
    # Init app functions
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


    """Auth0 login / logout"""


    # Start side to guide user to login/register
    @app.route('/')
    def index():
        #Get current month for go warm on
        current_month = datetime.datetime.now().month
        month_de = Month.query.filter(Month.number == current_month).one()
        month_de_str = month_de.name_de
        go_warm = "https://www.reise-klima.de/urlaub/" + month_de_str
        return render_template("index.html", go_warm=go_warm)


    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL,
                                        audience=AUTH0_AUDIENCE)


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
        # Store user email in session
        session[constants.USER_EMAIL] = userinfo["email"]
        email = session['user_email']

        ### If user is new, add to users table
        res = User.query.filter(User.email == email).one_or_none()
        # Location information not available for manual account
        try:
            loc = userinfo['locale']
        except:
            loc = None

        if res == None:
            try:
                user = User(email=session['user_email'], name=userinfo['name'],
                            location_iso2=loc)
                db.session.add(user)
                db.session.commit()
            except:
                db.session.rollback()
            finally:
                db.session.close()

        res = User.query.filter(User.email == email).one()
        user_id = res.id
        session[constants.USER_ID] = user_id

        return redirect('/home')


    @app.route('/logout')
    def logout():
        session.clear()
        params = {'returnTo': url_for('index', _external=True),
                    'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


    """APP"""


    @app.route('/home', methods=['GET', 'POST'])
    @requires_auth
    def home(jwt):
        # Get user permission, empty if user not actively got permissions
        session[constants.PERMISSION] = jwt['permissions']
        # Check if user with or without RBAC
        print("#### permission @home ", jwt["permissions"])

        if request.method == "GET":
            #Get current month for go warm on
            current_month = datetime.datetime.now().month
            month_de = Month.query.filter(Month.number == current_month).one()
            month_de_str = month_de.name_de
            go_warm = "https://www.reise-klima.de/urlaub/" + month_de_str
            return render_template("home.html", go_warm=go_warm)

        # POST
        else:
            # Get current user_id
            user_id = session['user_id']
            #User input check, must be text
            #Formatting and classification with check function
            destination = request.form.get("destination")
            dest = check(destination)
            print('#### DEST: ', dest)
            if not dest:
                return render_template("home.html", number=1,
                                    message="Please provide TRAVEL DESTINATION")

            #Get language switch value (English or German)
            switch = request.form.get("language")
            #Get location classes dictionary
            loc_classes = loc_class(dest)
            print('#### loc_classes: ', loc_classes)
            #Post default language to dropdwon on my dashboard
            # if loc_classes['language'] == 'german':
            #     options = ["German", "English"]
            # else:
            #     options = ["English", "German"]


        return render_template('home.html')

    @app.route("/vision")
    def vision():
        return render_template("vision.html")

    @app.route("/contact")
    def contact():
        return render_template("contact.html")


    """TODOS"""


    # Todo App main site / index
    @app.route("/dashboard")
    @requires_auth
    def dashboard(jwt):
        return redirect(url_for('get_todo_list', todos_list_id=1))

    # New task
    @app.route("/todos/create", methods=['POST'])
    @requires_auth_rbac('post:task')
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


    # Delete task
    @app.route("/todos/<todo_id>/delete", methods=['DELETE'])
    @requires_auth_rbac('delete:task')
    def delete_todo(jwt, todo_id):
        try:
            Todo.query.filter_by(id=todo_id).delete()
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({ 'success': True })


    # Check completed task
    @app.route("/todos/<todo_id>/set-completed", methods=['POST'])
    @requires_auth_rbac('post:task-completed')
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


    ## LISTS
    # New list
    @app.route("/lists/create", methods=['POST'])
    @requires_auth_rbac('post:task')
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


    # Delete list and its children"
    @app.route("/lists/<list_id>/delete", methods=['DELETE'])
    @requires_auth_rbac('delete:task')
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


    # Check completed list and its children
    @app.route("/lists/<list_id>/set-completed", methods=['POST'])
    @requires_auth_rbac('post:task-completed')
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


    # Todo list view
    @app.route('/lists/<todos_list_id>')
    @requires_auth
    def get_todo_list(jwt, todos_list_id):
        todo_lists = Todo_List.query.order_by('id').all()
        active_todo_list = Todo_List.query.get(todos_list_id)
        todos = Todo.query.filter_by(todos_list_id=todos_list_id).order_by('id').all()
        # Get Auth0 userinfo
        userinfo=session[os.environ['PROFILE_KEY']]
        userinfo_pretty = json.dumps(session[constants.JWT_PAYLOAD])

        return render_template("dashboard.html", lists=todo_lists,
                                active_todo_list=active_todo_list, data=todos,
                                userinfo=userinfo,
                                userinfo_pretty=userinfo_pretty)


    return app

app = create_app()

if __name__ == '__main__':
    app.run()
