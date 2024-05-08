from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return "This is the about page"


#Route for EDP Page 
@app.route("/EDP")
def edp():
    connection = sqlite3.connect('fragrance.db') #connect to database 
    cur = connection.cursor()
    cur.execute("SELECT bottle_name FROM Fragrance WHERE bottle_concentration = 'EDP'") #select bottle name
    fragrance_name = cur.fetchall()

    cur.execute("SELECT brand_name from Fragrance INNER JOIN Designer ON Fragrance.bottle_brand = Designer.brand_id WHERE bottle_concentration = 'EDP'")
    fragrance_brand = cur.fetchall() #select bottle brand

    cur.execute("SELECT bottle_description FROM Fragrance WHERE bottle_concentration = 'EDP'")
    fragrance_desc = cur.fetchall() #select bottle description

    return render_template('fragrance_info.html', name = fragrance_name, brand = fragrance_brand, description = fragrance_desc) #display info with templates


 

if __name__ == "__main__":
    app.run(debug=True)