from flask import Flask, session, request, redirect, url_for, render_template, flash
from application.Models import*
from sqlalchemy import or_
from main import app
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

@app.route("/")
def main():
    return render_template("index.html")
    
@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('main'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
