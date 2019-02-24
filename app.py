from flask import Flask, g
from flask.ext.login import LoginManager

import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'asdfioeriugn12,wdfiommiojf!euihreg'

#login manager setting
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login"

#load user
@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return respponse


if __name__ == '__main__':
    #initialize database
    models.initialize()
    #create admin user
    models.User.create_user(
        name='archie J',
        email='archieJ@hotmail.com',
        password='password',
        admin=True
    )
    app.run(debug=DEBUG, host=HOST, port=PORT)
    
