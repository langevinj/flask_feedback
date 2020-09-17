from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User class"""

    __tablename__ = "users"

    username = db.Column(db.String(20), nullable=False,
                         unique=True, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    feedback = db.relationship("Feedback", backref="user", cascade="all,delete")


    @classmethod 
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user w/hashed password & return user"""

        hashed = bcrypt.generate_password_hash(pwd)
        #turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        #return instance of user w/username and hased pwd
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """validate that user exists and password is correct, returning user if valid or else false"""

        u = User.query.filter_by(username=username).first()
    
        if u and bcrypt.check_password_hash(u.password, pwd):
            #return a user instance
            return u  
        else: 
            return False

class Feedback(db.Model):
    """Feedback class"""

    __tablename__ = "feedback"

    id = db.Column(db.Integer, nullable=False,
                   autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False,)


