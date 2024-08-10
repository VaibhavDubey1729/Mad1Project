from flask import Flask, render_template, redirect, request, session, url_for
from application.Models import *

app = Flask(__name__)
app.secret_key = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

db.init_app(app)

with app.app_context():
    db.create_all()

from application.Controls import*
from application.UserController import*


if __name__ == "__main__":
    app.run(debug=True)