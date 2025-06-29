from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# App initialization
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:pass@localhost:3307/test_data"
db = SQLAlchemy(app)

# Table creation
class TaskManager(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    created = db.Column(db.Date, default=lambda:datetime.utcnow().date())
    completed = db.Column(db.String(10), default="Pending")

    def __repr__(self):
        return f"{self.sno}. {self.task}"

# Initial Path
@app.route("/")
def index():
    logged_in = session.get("logged",False)
    return render_template("home.html", logged=logged_in)

# Main guard
if __name__ == "__main__":
    app.run(debug=True)