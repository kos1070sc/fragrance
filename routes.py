from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return "This is the about page"

@app.route("/EDP")
def edp():
    connection = sqlite3.connect('fragrance.db')
    cur = connection.cursor()
    cur.execute("SELECT bottle_name, bottle_description, bottle_concentration FROM Fragrance WHERE bottle_concentration = 'EDP'")
    fragrance_edp = cur.fetchall()
    return render_template('pizza.html', fragrance_edp = fragrance_edp)


    

if __name__ == "__main__":
    app.run(debug=True)