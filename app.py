from flask import Flask, render_template, redirect, session, flash
# from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

# toolbar = DebugToolbarExtension(app)

@app.route("/")
def go_to_register():
    """Redirect user to registration page"""

    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    """Registration of user"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()

        session["username"] = new_user.username

        # on successful login, redirect to secret page
        return redirect(f"/users/{username}")

    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_form():
    """login a user"""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data  
        pwd = form.password.data    

        #authenticate will return a user or False
        user = User.authenticate(username, pwd)
        if user: 
            session["username"] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Bad username/password"]
            render_template("login.html", form=form)
            
    return render_template("login.html", form=form)


@app.route("/logout")
def log_out():
    """logout user"""
    session.pop("username")
    return redirect("/login")


@app.route("/users/<username>")
def secret(username):
    """route for only logged in users"""

    if "username" not in session:
        flash("You must be logged in to view")
        return redirect("/")
    else: 
        curr_user = User.query.filter(User.username==username).first()
        user_feedback = Feedback.query.filter(Feedback.username==curr_user.username).all()
        if user_feedback != "":
            return render_template("user-info.html", curr_user=curr_user, user_feedback=user_feedback)
        else:
            return render_template("user-info.html", curr_user=curr_user)


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """route for deleting a user"""

    if "username" not in session or username != session['username']:
        flash("You must be logged in to delete your account")

    else:
        curr_user = User.query.filter(User.username==username).first()
        db.session.delete(curr_user)
        db.session.commit()
        session.clear()

    return redirect("/login")
    

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    """Add feedback for a user, or if submitted create a new feedback instance for the user"""

    curr_user = User.query.filter(User.username == username).first()

    if "username" not in session or username != session['username']:
        flash("You must be logged in to add feedback")
        return redirect("/")
    

    form = FeedbackForm()

    if form.validate_on_submit():

        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(
            title=title, content=content, username=curr_user.username)
        db.session.add(new_feedback)
        db.session.commit()
        # on successful adding of feedback bring back to users pages
        return redirect(f"/users/{username}")

    else:
        return render_template("add_feedback.html", form=form)

@app.route("/feedback/<int:feedbackid>/update", methods=["GET", "POST"])
def update_feedback(feedbackid):
    """Update a piece of feedback"""

    feedback = Feedback.query.get(feedbackid)

    if "username" not in session or feedback.username != session['username']:
        flash("You do not have access to this feedback")
        return redirect("/")

    form = FeedbackForm(obj = feedback)#attempting to pass in values
    
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        
        # on successful editting of feedback bring back to users pages
        return redirect(f"/users/{feedback.username}")
    
    return render_template("update_feedback.html", form=form)
        

@app.route("/feedback/<int:feedbackid>/delete")
def delete_feedback(feedbackid):
    """delete feedback"""

    feedback = Feedback.query.get(feedbackid)
    if "username" not in session or feedback.username != session['username']:
        flash("You cannot delete feedback that isn't yours")
        return redirect("/")

    else:
        username = feedback.username
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted")

    return redirect(f"/users/{username}")
    
        
