from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# App initialization
app = Flask(__name__)

# Initial Path
@app.route("/")
def index():
    return "Hello, World!"

# Main guard
if __name__ == "__main__":
    app.run(debug=True)