from flask import Flask  , render_template , request , redirect, flash, jsonify
from flask.helpers import make_response
from flask_login import LoginManager, logout_user, login_required, login_user, current_user, UserMixin, COOKIE_NAME, COOKIE_SECURE
from flask_sqlalchemy import SQLAlchemy
from modules import *
import time


app = Flask(__name__)
app.config["SECRET_KEY"] = ami["Username1"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/login.db"
app.config["SQLALCHEMY_BINDS"] = {"daily":"sqlite:///database/daily.db",
                                    "experience" : "sqlite:///database/experience.db",
                                    "favourite" : "sqlite:///database/favorite.db"}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(100), unique=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class blog_post(db.Model):
    __bind_key__ = "daily"
    sno = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String(200))
    subject = db.Column(db.String(200))
    post = db.Column(db.String(1000))
    effective = db.Column(db.String(5))
    time_ = db.Column(db.String(30))


class Experience(db.Model):
    __bind_key__ = "experience"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    item = db.Column(db.String(50))
    heading = db.Column(db.String(100))
    description = db.Column(db.String(200))
    writing = db.Column(db.String(1000))
    select = db.Column(db.String(5))
    time_ = db.Column(db.String(30))

class Favourite(db.Model):
    __bind_key__ = "favourite"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    person = db.Column(db.String(200))
    drink = db.Column(db.String(200))
    animal = db.Column(db.String(200))
    flower = db.Column(db.String(200))
    place = db.Column(db.String(200))
    fruit = db.Column(db.String(200))
    fish = db.Column(db.String(200))
    food = db.Column(db.String(200))
    game = db.Column(db.String(200))
    movie = db.Column(db.String(200))
    tvshow = db.Column(db.String(200))
    select = db.Column(db.String(5))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["email"]
        remember = request.form.get("remember")
        while True:
            user_name = User.query.filter_by(name=name).first()
            if user_name:
                if remember:
                    login_user(user=user_name, remember=True)
                else:
                    login_user(user=user_name, remember=False)
            else:
                name_save = User(name=name)
                db.session.add(name_save)
                db.session.commit()
                continue
            return redirect("/")
        
    return render_template("dist/login.html")


@app.route("/")
@login_required
def daily_dairies():
    dairies = blog_post.query.all()
    experiences = Experience.query.all()
    dairies.reverse()
    experiences.reverse()
    return render_template("main.html", dairies=dairies, experiences=experiences)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/daily_diary" , methods=["GET" , "POST"])
@login_required
def blog_post_():
    if request.method == "POST":
        address = request.form["address"]
        post = request.form["post"]
        effective = request.form["select"]
        if post and address:
            post_blog = blog_post(name=current_user.name,subject=address,
             post=post, effective=effective, time_=time.asctime())
            db.session.add(post_blog)
            db.session.commit()
        return redirect("/daily_diary")

    posts = blog_post.query.filter_by(name=current_user.name).all()
    posts.reverse()
    response = make_response(render_template("dist/daily.html" , posts=posts, user=current_user.name, foo=42))
    response.set_cookie("Daily", "People read this diary")
    return response

@app.route("/daily_edit/<int:sno>", methods=["GET", "POST"])
@login_required
def daily_edit(sno):
    if request.method == "POST":
        subject = request.form["address"]
        post = request.form["post"]
        before_edit = blog_post.query.filter_by(sno=sno).first()
        before_edit.subject = subject
        before_edit.post = post
        db.session.add(before_edit)
        db.session.commit()
        return redirect("/")

    post = blog_post.query.filter_by(sno=sno).first()
    response = make_response(render_template("dist/daily_edit.html", post=post))
    response.set_cookie("Edit_diary", "Edit your diary")
    return response


@app.route("/experience", methods=["GET","POST"])
@login_required
def experience_():
    username = request.cookies.get("Daily")
    print(username)
    if request.method == "POST":
        item =request.form["item"]
        heading =request.form["heading"]
        description=request.form["description"]
        writing =request.form["writing"]
        select = request.form["select"]
        experience_save = Experience(name=current_user.name, item=item, heading=heading,
         description=description, writing=writing, select=select, time_=time.asctime())
        db.session.add(experience_save)
        db.session.commit()
        return redirect("/experience")

    experiences = Experience.query.filter_by(name=current_user.name).all()
    experiences.reverse()
    response = make_response(render_template("dist/experience.html", experiences=experiences))
    response.set_cookie("Experience", "have")
    return response

@app.route("/experience_edit/<int:id>", methods=["GET", "POST"])
@login_required
def experience_edit(id):
    if request.method == "POST":
        item = request.form["item"]
        heading = request.form["heading"]
        description= request.form["description"]
        writing = request.form["writing"]
        before_edit = Experience.query.filter_by(id=id).first()
        before_edit.item = item
        before_edit.heading = heading
        before_edit.description = description
        before_edit.writing = writing
        db.session.add(before_edit)
        db.session.commit()
        return redirect("/experience")

    post = Experience.query.filter_by(id=id).first()
    print(post)
    return render_template("dist/experience_edit.html", experience=post, user=current_user.name)

@app.route("/favourite", methods=["GET", "POST"])
@login_required
def favourite():
    favourites = Favourite.query.filter_by(name=current_user.name).all()
    if favourites:
        return render_template("dist/favourite.html", favourites=favourites, user=current_user.name, time=time.asctime())
    elif request.method == "POST":
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
        select = request.form["select"]
        save_sql = Favourite(name=current_user.name,person=person,fish=fish,place=place,flower=flower,
        animal=animal,drink=drink,food=food,game=game,movie=movie,tvshow=tvshow, select=select)
        db.session.add(save_sql)
        db.session.commit()
        return redirect("/favourite")
        
    return render_template("dist/favourite_set.html")



if __name__=="__main__":
    app.run(debug=True, port=3900, host="0.0.0.0")
