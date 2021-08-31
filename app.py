from bson import objectid
from flask import Flask  , render_template , request , redirect, flash, jsonify
from flask.helpers import make_response
from flask_login import LoginManager, logout_user, login_required, login_user, current_user, UserMixin, COOKIE_NAME, COOKIE_SECURE
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from bson.json_util import loads, dumps
from modules import *
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = ami["Username1"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/login.db"
app.config["MONGO_URI"] = f"mongodb+srv://{ami['username3']}:{ami['password']}@mejan-cluster.1ce4z.mongodb.net/ideaex"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
mongo = PyMongo(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(100), unique=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["email"]
        while True:
            user_name = User.query.filter_by(name=name).first()
            if user_name:
                login_user(user=user_name, remember=True)
            else:
                name_save = User(name=name)
                db.session.add(name_save)
                db.session.commit()
                continue
            return redirect("/")
        
    return render_template("dist/login.html")


def last_five(lists):
    if len(lists) > 4:
        listss = [lists[i] for i in range(4)]
    else:
        listss = lists
    return listss


@app.route("/")
@login_required
def daily_dairies():
    favourites = loads(dumps(mongo.db.favourites.find_one({'name':current_user.name}))) 
    if not favourites:
        return redirect("/favourite")
    dairies = mongo.db.ideas.find()
    dairies = loads(dumps(dairies))
    experiences = mongo.db.experiences.find()
    experiences = loads(dumps(experiences))
    dairies.reverse()
    experiences.reverse()
    return render_template("main.html", dairies=last_five(dairies), experiences=last_five(experiences))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/public/<string:public>")
@login_required
def ideas(public):
    if public == "ideas":
        dairies = mongo.db.ideas.find()
        dairies = loads(dumps(dairies))
        dairies.reverse()
        showings = dairies

    if public == "favourites":
        dairies = mongo.db.favourites.find()
        dairies = loads(dumps(dairies))
        dairies.reverse()
        showings = dairies

    if public == "experiences":
        dairies = mongo.db.experiences.find()
        dairies = loads(dumps(dairies))
        dairies.reverse()
        showings = dairies
    print(showings)
    return render_template("public.html", showings=showings)


@app.route("/daily_diary" , methods=["GET" , "POST"])
@login_required
def blog_post_():
    if request.method == "POST":
        address = request.form["address"]
        post = request.form["post"]
        effective = request.form["select"]
        if post and address:
            mongo.db.ideas.insert_one({"name":current_user.name,"subject":address,
             "post":post, "effective":effective, "time_":time.asctime()})
        return redirect("/daily_diary")

    posts = loads(dumps(mongo.db.ideas.find()))
    posts.reverse()
    response = make_response(render_template("dist/daily.html" , posts=posts, user=current_user.name, foo=42))
    response.set_cookie("Daily", "People read this diary")
    return response

@app.route("/daily_edit/<string:_id>", methods=["GET", "POST"])
@login_required
def daily_edit(_id):
    print("okay")
    if request.method == "POST":
        subject = request.form["address"]
        post = request.form["post"]
        mongo.db.ideas.find_one_and_update({"_id":objectid.ObjectId(_id)},{"$set":{"subject":subject, "post":post}})
        return redirect("/daily_diary")

    print("okay")
    post = loads(dumps(mongo.db.ideas.find_one({"_id":objectid.ObjectId(_id)})))
    print(post)
    response = make_response(render_template("dist/daily_edit.html", post=post))
    response.set_cookie("Edit_diary", "Edit your diary")
    return response


@app.route("/experience", methods=["GET","POST"])
@login_required
def experience_():
    if request.method == "POST":
        item =request.form["item"]
        heading =request.form["heading"]
        description=request.form["description"]
        writing =request.form["writing"]
        select = request.form["select"]
        mongo.db.experiences.insert_one({"name":current_user.name, "item":item, "heading":heading,
         "description":description, "writing":writing, "select":select,"time_":time.asctime()})
        return redirect("/experience")

    experiences = loads(dumps(mongo.db.experiences.find({"name":current_user.name})))
    experiences.reverse()
    response = make_response(render_template("dist/experience.html", experiences=experiences))
    response.set_cookie("Experience", "have")
    return response

@app.route("/experience_edit/<string:_id>", methods=["GET", "POST"])
@login_required
def experience_edit(_id):
    if request.method == "POST":
        item = request.form["item"]
        heading = request.form["heading"]
        description= request.form["description"]
        writing = request.form["writing"]
        mongo.db.experiences.find_one_and_update({'_id':objectid.ObjectId(_id)}, {"$set":{"item":item,"heading":heading, "description":description, "writing":writing}})
        return redirect("/experience")

    post = loads(dumps(mongo.db.experiences.find_one({'_id':objectid.ObjectId(_id)})))
    return render_template("dist/experience_edit.html", experience=post, user=current_user.name)

@app.route("/favourite")
@login_required
def favourite():
    favourites =loads(dumps(mongo.db.favourites.find_one({'name':current_user.name})))
    if favourites:
        return render_template("dist/favourite.html", favourites=favourites, user=current_user.name, time=time.asctime())
    else:
        return redirect("/favourite_set")
        
    
@app.route("/favourite_set" , methods=["GET", "POST"])
@login_required
def favourite_set():
    if request.method == "POST":
        person =request.form["person"]
        fish =request.form["fish"]
        place =request.form["place"]
        flower =request.form["flower"]
        animal =request.form["animal"]
        drink =request.form["drink"]
        food =request.form["food"]
        game =request.form["game"]
        movie =request.form["movie"]
        tvshow =request.form["tvshow"]
        fruit =request.form["fruit"]
        select = request.form["select"]
        mongo.db.favourites.find_one_and_delete({"name":current_user.name})
        mongo.db.favourites.insert_one({'name':current_user.name,"person":person,'fish':fish,'place':place,'flower':flower,
        'animal':animal,'drink':drink,'food':food,'game':game,'movie':movie,'tvshow':tvshow,"fruit":fruit, 'select':select})
        return redirect("/favourite")

    favourites =loads(dumps(mongo.db.favourites.find_one({'name':current_user.name})))
    return render_template("dist/favourite_set.html", favourites=favourites, user=current_user.name, time=time.asctime())


@app.route("/admin")
@login_required
def admin():
    name=current_user.name
    if name == "mejan601@gmail.com":
        login_person = User.query.all()
        login_person.reverse()
        return render_template("admin.html", 
            subscribers=login_person, no_subscribers=len(login_person))
    else:
        return redirect("/")



if __name__=="__main__":
    app.run(debug=True, port=3900, host="0.0.0.0")
