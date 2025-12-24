from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_login import LoginManager

db = SQLAlchemy()
babel = Babel()
login_manager = LoginManager()
