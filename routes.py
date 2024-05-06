from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return("This is the homepage")




if __name__ == "main":
    app.run(debug=True)