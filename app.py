# Libraries Required
from flask import Flask, render_template, redirect, request, session, flash
# Database
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Mailing
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import random
# Hashing
from werkzeug.security import generate_password_hash, check_password_hash

# App initialization
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mytaskmanager.db"
db = SQLAlchemy(app)

# User Table creation
class Users(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True, unique=True)
    pwd = db.Column(db.String(200), nullable=False)
    
    tasks = db.relationship("TaskManager", backref="user", lazy=True)

    def __repr__(self):
        return f"{self.uid}. {self.email}"

# Task Table creation
class TaskManager(db.Model):
    __tablename__ = 'task_manager'
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created = db.Column(db.Date, default=lambda:datetime.utcnow().date())
    completed = db.Column(db.String(10), default="Pending")
    
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)

    def __repr__(self):
        return f"{self.sno}. {self.task}"

# Loading .env
load_dotenv()

# Mail Config
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT"))
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_RECEIVER'] = os.getenv("MAIL_RECEIVER")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS") == "True"
app.config['MAIL_USE_SSL'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Mail Setup
mail = Mail(app)

# Initial Path
@app.route("/")
def index():
    return render_template("home.html", logged=False, active="home")


# Before Login Pages:

# Account Login 
@app.route("/login", methods=["GET", "POST"])
def login():
    # logged_in = session.get("logged", False)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pass")
        
        # Check if User Exists
        user = Users.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.pwd, password):
                # Login successful
                logged = True
                session['logged'] = logged
                session['user_id'] = user.uid
                
                # flash("Logged in successfully!", "success")
                return redirect("/viewTask")
            else:
                flash("Invalid password. Please try again.", "error")
        else:
            flash("No account found with that email.", "error")
    
    return render_template("login.html", logged=False, active="login")

# Forgot Password
@app.route("/forgotPassword", methods=["GET","POST"])
def forgot():
    forgot_stage = 1

    # Stage 1: Send OTP
    if request.method == "POST":
        email = request.form.get("email")
        otp = str(random.randint(100000, 999999))

        # Back & Exit
        stage_action = request.form.get("stage_action")
        if stage_action == "back":
            forgot_stage = 1
        elif stage_action == "exit":
            flash("Password reset cancelled.", "error")
            return redirect("/login")

        if email:
            user = Users.query.filter_by(email=email).first()
            if not user:
                flash("Account with this email doesn't exists.", "error")
                return redirect("/signup")
            
            # Email Content
            msg = Message(
                subject="OTP for My Task Manager Password Reset",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f"""
Dear {user.fullname},

Your One-Time Password (OTP) to reset your password is:

{otp}

This code is valid for the next 5 minutes. Please do not share it with anyone.

If you did not request this code, please ignore this email.

Thanks,
My Task Manager Team
"""
            )

            # Email Sent
            try:
                mail.send(msg)
                flash("An OTP has been sent to your email address!", "success")
            except Exception as e:
                flash("Email sending failed. Please try again later.", "error")
                print(f"Email error: {e}")
            
            # Session Storing Values
            session['forgot_otp'] = otp
            session['forgot_email'] = email
            forgot_stage = 2          
        
        # stage 2: OTP Validation
        elif request.form.get("pass"):
            entered_otp = request.form.get("pass")

            if entered_otp == session.get("forgot_otp"):
                flash("OTP verified successfully.", "success")
                forgot_stage = 3
            else:
                flash("Invalid OTP. Please try again.", "error")
                forgot_stage = 2

        # stage 3: Resetting User Password
        elif request.form.get("create_pass") and request.form.get("confirm_pass"):
            pass1 = request.form.get("create_pass")
            pass2 = request.form.get("confirm_pass")

            if pass1 != pass2:
                flash("Passwords do not match.", "error")
                forgot_stage = 3
            else:
                # Password Hashing
                passw = generate_password_hash(pass1)
                user = Users.query.filter_by(email=session["forgot_email"]).first()
                user.pwd = passw
                db.session.commit()
                session.clear()

                flash("Password changed successfully!", "success")
                return redirect("/login")

    return render_template("forgot_password.html", logged=False, active="login", forgot_stage=forgot_stage)

# Account Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # logged_in = session.get("logged", False)

    signup_stage = 1

    if request.method == "POST":
        # Stage 1: Send OTP
        name = request.form.get("fullname")
        email = request.form.get("email")
        otp = str(random.randint(100000, 999999))

        # Back & Exit
        stage_action = request.form.get("stage_action")
        if stage_action == "back":
            signup_stage = 1
        elif stage_action == "exit":
            flash("Password reset cancelled.", "error")
            return redirect("/signup")           

        if name and email:
            existing_user = Users.query.filter_by(email=email).first()
            if existing_user:
                flash("Account with this email already exists.", "error")
                return redirect("/signup")
            
            # Email Content
            msg = Message(
                subject="Verification Code for My Task Manager",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f"""
Dear {name},

Your One-Time Password (OTP) for completing your registration is:

{otp}

This code is valid for the next 5 minutes. Please do not share it with anyone.

If you did not request this code, please ignore this email.

Thanks,
My Task Manager Team
"""
            )

            # Email Sent
            try:
                mail.send(msg)
                flash("An OTP has been sent to your email address!", "success")
            except Exception as e:
                flash("Email sending failed. Please try again later.", "error")
                print(f"Email error: {e}")
            
            # Session Storing Values
            session['signup_name'] = name
            session['signup_otp'] = otp
            session['signup_email'] = email
            signup_stage = 2

        elif request.form.get("pass"):
            # stage 2: OTP Validation
            entered_otp = request.form.get("pass")

            if entered_otp == session.get("signup_otp"):
                flash("OTP verified successfully.", "success")
                signup_stage = 3
            else:
                flash("Invalid OTP. Please try again.", "error")
                signup_stage = 2

        elif request.form.get("create_pass") and request.form.get("confirm_pass"):
            # stage 3: Creating User Account
            pass1 = request.form.get("create_pass")
            pass2 = request.form.get("confirm_pass")

            if pass1 != pass2:
                flash("Passwords do not match.", "error")
                signup_stage = 3
            else:
                # Password Hashing
                passw = generate_password_hash(pass1)
                new_user = Users(
                    fullname=session.get('signup_name'),
                    email=session.get('signup_email'),
                    pwd=passw
                )
                db.session.add(new_user)
                db.session.commit()

                session.clear()

                flash("Account created successfully!", "success")
                return redirect("/login")

    return render_template("signup.html", logged=False, active="signup", signup_stage=signup_stage)

# About Page
@app.route("/about", methods=["GET","POST"])
def about():
    # logged_in = session.get("logged", False)

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        msg = Message(
            subject="My Task Manager Contact Message",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_RECEIVER']],
            body=f"Name: {name}\n\nEmail: {email}\n\nMessage: {message}"
        )

        mail.send(msg)

        flash("Your Message Sent Successfully!", "success")

    return render_template("about.html", logged=False, active="about")



# After Login Pages:

# View All Tasks
@app.route("/viewTask", methods=["GET","POST"])
def view():
    if not session.get("logged"):
        return redirect("/")
    
    userid = session['user_id']
    tasks = TaskManager.query.filter_by(uid=session["user_id"]).all()

    return render_template("view_task.html", logged=True, user=userid, tasks=tasks, active="view")

# Complete/Incomplete Task
@app.route("/toggleTask/<int:sno>")
def toggle_task(sno):
    if not session.get("logged"):
        return redirect("/")
    
    task = TaskManager.query.filter_by(sno=sno, uid=session["user_id"]).first()
    if task:
        task.completed = "Pending" if task.completed == "Completed" else "Completed"
        db.session.commit()
        # flash(f"Task marked as {task.completed}!", "success")
    return redirect("/viewTask")


# Delete a Task
@app.route("/deleteTask/<int:sno>", methods=["GET","POST"])
def delete_task(sno):
    if not session.get("logged"):
        return redirect("/")

    task = TaskManager.query.filter_by(sno=sno, uid=session["user_id"]).first()
    if task:
        # flash("Task deleted successfully!", "success")
        db.session.delete(task)
        db.session.commit()
    return redirect("/viewTask")


# Update a Task
@app.route("/updateTask/<int:sno>", methods=["GET", "POST"])
def update_task(sno):
    if not session.get("logged"):
        return redirect("/")

    task = TaskManager.query.filter_by(sno=sno, uid=session["user_id"]).first()

    if request.method == "POST":
        new_task = request.form.get("task")
        new_desc = request.form.get("desc")
        task.task = new_task
        task.description = new_desc
        db.session.commit()
        # flash("Task updated successfully!", "success")
        return redirect("/viewTask")

    return render_template("update_task.html", logged=True, active="update", task=task)

# Add New Tasks
@app.route("/addTask", methods=["GET","POST"])
def add():
    if not session.get("logged"):
        return redirect("/")
    
    user_id = session['user_id']

    if request.method == "POST":
        task = request.form["task"]
        description = request.form["desc"]

        new_task = TaskManager(task=task, description=description, uid=user_id)

        db.session.add(new_task)
        db.session.commit()

        flash("Task added successfully!","success")
        # return redirect("/viewTask")

    return render_template("add_task.html", logged=True, active="add")

# View User Profile
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("logged"):
        return redirect("/")
    
    user = Users.query.get(session['user_id'])

    # Default Page
    page = "view_profile"
    
    if request.method == "POST":
        # Clicked button value:
        action = request.form.get("action")

        if action == "edit":
            page = "edit_profile"

        elif action == "save_profile":
            new_name = request.form.get("name")
            new_phone = request.form.get("phone")

            # Update profile
            user.fullname = new_name
            user.phone = new_phone
            db.session.commit()

            flash("Profile updated successfully!", "success")
            page = "view_profile"

        elif action == "change_password":
            page = "change_password"

        elif action == "save_password":
            old_pass = request.form.get("old_pass")
            new_pass = request.form.get("new_pass")
            confirm_pass = request.form.get("confirm_pass")

            # Checking password
            if not check_password_hash(user.pwd, old_pass):
                flash("Old password is incorrect!", "error")
                page = "change_password"
            # Confirming password
            elif new_pass != confirm_pass:
                flash("New passwords do not match!", "error")
                page = "change_password"
            # Updating password
            else:
                user.pwd = generate_password_hash(new_pass)
                db.session.commit()
                flash("Password changed successfully!", "success")
                page = "view_profile"

    return render_template("profile.html", logged=True, profile=user, active="profile", page=page)

# Account Logout 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Main guard
if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    app.run(debug=True)