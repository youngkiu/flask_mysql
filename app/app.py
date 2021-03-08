from flask import Flask
from config import VERSION, SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import db
from routes import api


app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/#flask_sqlalchemy.SQLAlchemy.init_app
db.init_app(app)
# https://flask-restx.readthedocs.io/en/latest/api.html#flask_restx.Api.init_app
api.init_app(app,
             version=VERSION, title='Company API',
             description='A company name & tag API')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
