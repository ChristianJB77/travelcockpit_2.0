# Libraries
import json
import os
from flask import Flask, render_template, request, redirect, jsonify, \
                    abort, url_for, session, _request_ctx_stack, flash
from flask_cors import CORS
from six.moves.urllib.parse import urlencode
import sys
import datetime
from sqlalchemy import func, desc

# Constants for Auth0 from constants.py, secret keys stores as config variables
import auth.constants as constants
from auth.auth import AuthError, requires_auth, requires_auth_rbac, auther
# Database model
from database.models import setup_db, db, Todo_List, Todo, Month, User, \
                            UserHistory, Secret

# My features
from features.input_classifier import check, loc_class
from features.link_maker import links
from features.weather_widget_maker import weather_widget
from features.covid_widget_maker import covid_widget
from features.info_widget_maker import info_widget
from features.holiday_widget_maker import holiday

def create_app(test_config=None):
    # Init app functions
    app = Flask(__name__)
    app.debug = True
    app.secret_key = os.environ['SECRET_KEY']
    setup_db(app)
    CORS(app)
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                                'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                                'GET,PUT,POST,DELETE,OPTIONS')
        return response
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
        # Location information not available for manual registered account
        try:
            loc = userinfo['locale']
        except:
            loc = None

        if res == None:
            user = User(email=session['user_email'], name=userinfo['name'],
                        location_iso2=loc)
            user.insert()

        res = User.query.filter(User.email == email).one()
        user_id = res.id
        session[constants.USER_ID] = user_id

        return redirect("/home")


    @app.route('/logout')
    def logout():
        session.clear()
        params = {'returnTo': url_for('index', _external=True),
                    'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


    """APP"""

    # View Travel Cockpit's vision / motivation
    @app.route("/vision")
    def get_vision():
        return render_template("vision.html")

    # View contact page
    @app.route("/contact")
    def get_contact():
        return render_template("contact.html")

    # Get destination search and view result in dashboard view
    # GET and POST in common endpoint to share premission check
    @app.route('/home', methods=['GET', 'POST'])
    @requires_auth
    def get_post_home(jwt):
        # Get user permission, empty if user not actively got permissions
        session[constants.PERMISSION] = jwt['permissions']
        permi = jwt['permissions']
        # Check if user with or without RBAC -> Render different navi layout
        # -> Director = delete:master, Manager = delete:own
        print("#### permission @home ", permi)
        if 'delete:own' in permi:
            session[constants.ROLE] = 'Manager'
        if 'delete:master' in permi:
            session[constants.ROLE] = 'Director'

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
            id = session['user_id']
            #User input check, must be text
            #Formatting and classification with check function
            destination = request.form.get("destination")
            dest = check(destination)
            print('#### DEST: ', dest)

            """Get page request for direct links in blog"""
            req = request.args.get('dest', None, type=str)
            print('#### Page request: ', req)

            if not dest:
                return render_template("home.html", number=1,
                                    message="Please provide TRAVEL DESTINATION")

            # Get language switch value (English or German)
            switch = request.form.get("language")
            # Get location classified dictionary
            loc_classes = loc_class(dest)
            print('#### loc_classes: ', loc_classes)

            # Post default language to dropdwon on my dashboard
            if loc_classes['language'] == 'german':
                options = ["German", "English"]
            else:
                options = ["English", "German"]

            # Button links dictionary
            links_dic = links(dest, loc_classes, switch)
            # Weather widget
            weather = weather_widget(loc_classes, switch)
            # Covid19 widget
            covid = covid_widget(loc_classes, switch)
            # Info box widget
            info = info_widget(loc_classes, switch, weather)
            # National holidays widget
            holidays = holiday(loc_classes, switch)
            # Current time
            time = datetime.datetime.now()

            # Destination for search history
            loc = loc_classes["loc_type"]
            if loc == "country":
                history = loc_classes["country_en"]
            elif loc == "big_city":
                history = loc_classes["city"]
            else:
                history = loc_classes["location"]

            # Store user search in user_history
            user_history = UserHistory(
                            destination=history,
                            timestamp=time,
                            user_id=id)
            user_history.insert()

        return render_template("my_dashboard.html", switch=switch,
                                loc_classes=loc_classes, links_dic=links_dic,
                                info=info, options=options, weather=weather,
                                covid=covid, holidays=holidays)


    # View user own history
    @app.route("/history")
    @requires_auth
    def get_history(jwt):
        # Show user's search history
        id = session["user_id"]

        history = UserHistory.query.filter(UserHistory.user_id == id) \
                    .with_entities(UserHistory.destination, \
                    func.count(UserHistory.destination)) \
                    .group_by(UserHistory.destination) \
                    .order_by(func.count(UserHistory.destination).desc()).all()

        return render_template("history.html", rows=history)


    # Master view of all users, only for Manager and Director RBAC roles
    @app.route("/history-all")
    @requires_auth_rbac('get:history-all')
    def get_history_all(jwt):
        hist_all = UserHistory.query \
                    .with_entities(UserHistory.destination, \
                    func.count(UserHistory.destination)) \
                    .group_by(UserHistory.destination) \
                    .order_by(func.count(UserHistory.destination).desc()).all()

        # Get unique user list of listed destinations
        data = []
        for hist in hist_all:
            users = UserHistory.query \
                    .filter(UserHistory.destination == hist[0]).all()

            names = []
            for user in users:
                name = user.users.name
                if name not in names:
                    names.append(name)

            data.append({
                "destination": hist[0],
                "amount": hist[1],
                "names": names
            })

        return render_template("history_all.html", data=data)


    """TRAVEL SECRETS BLOG"""


    # View blog posts USER VIEW
    @app.route("/blog/user")
    @requires_auth
    def get_blog_user(jwt):
        blogs = Secret.query.order_by(desc(Secret.id)).all()
        userinfo=session[os.environ['PROFILE_KEY']]

        return render_template("blog_user.html", blogs=blogs, userinfo=userinfo)


    # View blog posts MASTER
    @app.route("/blog")
    @requires_auth_rbac('get:blog')
    def get_blog(jwt):
        blogs = Secret.query.order_by(desc(Secret.id)).all()
        userinfo=session[os.environ['PROFILE_KEY']]

        return render_template("blog.html", blogs=blogs, userinfo=userinfo)

    # Create new travel secrets
    # First get template, then post
    @app.route("/blog/create")
    @requires_auth_rbac('post:blog')
    def post_blog(jwt):
        return render_template("blog_create.html")

    @app.route("/blog/create", methods=['POST'])
    @requires_auth_rbac('post:blog')
    def post_blog_submission(jwt):
        # Get user form input and insert in database

        # Minimum fill level check
        secret = Secret(
            title = request.form.get('title'),
            why1 = request.form.get('why1'),
            why2 = request.form.get('why2'),
            why3 = request.form.get('why3'),
            text = request.form.get('text'),
            link = request.form.get('link'),
            user_id = session["user_id"]
        )
        secret.insert()
        flash("Blog was successfully added!")

        return redirect("/blog")


    # Edit travel blog post MASTER
    # First get blog then patch
    @app.route("/blog/<int:id>/edit")
    @requires_auth_rbac('patch:master')
    def patch_own_blog(jwt, id):
        blog = Secret.query.filter(Secret.id == id).one_or_none()
        if blog == None:
            abort(404)
        return render_template("blog_edit.html", blog=blog)

    @app.route("/blog/<int:id>/edit/submission", methods=['PATCH'])
    @requires_auth_rbac('patch:master')
    def patch_own_blog_submission(jwt, id):
        # Get HTML json body response
        body = request.get_json()
        secret = Secret.query.filter(Secret.id == id).one_or_none()

        # Get user edit and update database
        secret.title = body.get('title', None)
        secret.why1 = body.get('why1', None)
        secret.why2 = body.get('why2', None)
        secret.why3 = body.get('why3', None)
        secret.text = body.get('text', None)
        secret.link = body.get('link', None)

        secret.update()

        flash("Blog was successfully updated!")

        return jsonify({ 'success': True })

    # Delete blog MASTER
    @app.route("/blog/<int:id>/delete", methods=['DELETE'])
    @requires_auth_rbac('delete:master')
    def delete_blog_master(jwt, id):
        secret = Secret.query.filter(Secret.id == id).one_or_none()
        secret.delete()
        flash("Blog was DELETED!")

        return jsonify({ 'success': True })


    return app

app = create_app()

if __name__ == '__main__':
    app.run()
