from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)




#
#Route for homepage
#
@app.route("/")
def home():
    connection = sqlite3.connect('fragrance.db') #connect to database 
    cur = connection.cursor()
    cur.execute("SELECT brand_name FROM Designer;")
    fragrance_brand = cur.fetchall()
    connection.close()
    return render_template("home.html", brands = fragrance_brand)


#
#Route for EDP page
#  
@app.route("/EDP")
def edp():
    connection = sqlite3.connect('fragrance.db') #connect to database 
    cur = connection.cursor()
    cur.execute('''SELECT bottle_id, bottle_name FROM Fragrance 
                INNER JOIN Designer 
                ON Fragrance.bottle_brand = Designer.brand_id 
                WHERE bottle_concentration = 'EDP';''')
    fragrance_result = cur.fetchall()

    cur.execute('''SELECT bottle_concentration 
                FROM Fragrance WHERE bottle_concentration = 'EDP';''')
    fragrance_concentration = cur.fetchone()
    connection.close()
    return render_template("all_fragrances.html", fragrances = fragrance_result, 
                            concentration = fragrance_concentration)



#
#Route for EDT page
#
@app.route("/EDT")
def edt():
    connection = sqlite3.connect('fragrance.db') #connect to database 
    cur = connection.cursor()
    cur.execute('''SELECT bottle_id, bottle_name FROM Fragrance 
                INNER JOIN Designer 
                ON Fragrance.bottle_brand = Designer.brand_id 
                WHERE bottle_concentration = 'EDT';''')
    fragrance_result = cur.fetchall()

    cur.execute('''SELECT bottle_concentration 
                FROM Fragrance WHERE bottle_concentration = 'EDT';''')
    fragrance_concentration = cur.fetchone()
    connection.close()
    return render_template("all_fragrances.html", fragrances = fragrance_result, 
                            concentration = fragrance_concentration)




#
#Route for bottle information 
#
@app.route("/fragrance/<int:id>")
def bottle(id):
    connection = sqlite3.connect('fragrance.db') #connect to database 
    cur = connection.cursor()

    #bottle info
    cur.execute('''SELECT bottle_name, bottle_description, bottle_concentration, 
                bottle_longevity, bottle_size, bottle_price, bottle_photo FROM Fragrance WHERE 
                bottle_id = ?;''', (id,))
    fragrance_info = cur.fetchone()

    #select bottle brand
    cur.execute('''SELECT brand_name from Fragrance INNER JOIN Designer ON 
                Fragrance.bottle_brand = Designer.brand_id 
                WHERE bottle_id = ?;''', (id,))
    fragrance_brand = cur.fetchone() 


    #notes
    cur.execute('''SELECT bottle_name, note_name FROM Notebridge INNER JOIN 
                Note ON NoteBridge.nid = Note.note_id INNER JOIN Fragrance 
                ON NoteBridge.fid = Fragrance.bottle_id WHERE bottle_id = ?''', (id,))

    fragrance_note = cur.fetchall()
    connection.close()
    return render_template("bottle_info.html", notes = fragrance_note, 
                            brand = fragrance_brand, info = fragrance_info)




#
#Route for comparision page
#
@app.route("/comparision")
def comparision():
    connection = sqlite3.connect('fragrance.db') #connect to database 
    cur = connection.cursor()
    cur.execute('''SELECT bottle_name, brand_name, bottle_longevity, 
                bottle_size, bottle_price, bottle_photo FROM Fragrance INNER JOIN 
                Designer ON Fragrance.bottle_brand = Designer.brand_id 
                WHERE bottle_concentration = 'EDT';''')
    edt_result = cur.fetchall()
    
    cur.execute('''SELECT bottle_name, brand_name, bottle_longevity, 
                bottle_size, bottle_price, bottle_photo FROM Fragrance 
                INNER JOIN Designer ON Fragrance.bottle_brand = Designer.brand_id 
                WHERE bottle_concentration = 'EDP';''')
    edp_result = cur.fetchall()
    connection.close()


    return render_template('comparision.html', 
                            edt_comparision = edt_result, 
                            edp_conparision = edp_result)



##
##Form page
##

@app.route("/form")
def form():
    return render_template("review.html")

@app.route("/submit_review", methods = ["POST"])
def submit_review():
    username = request.form['username']
    fid = request.form['fid']
    review = request.form['review']

    connection = sqlite3.connect('fragrance.db') #connect to database 
    cur = connection.cursor()
    cur.execute('''INSERT INTO Form (review_username, review_fid, review_content) 
                VALUES (?,?,?)''', (username, fid, review,)) #insert responese into the database
    connection.commit()
    connection.close()
    return redirect(url_for('form'))#redirects the user back to the form page 



#
#Some fun triangles 
#
@app.route("/triangle/<int:size>")
def triangle(size):
    triangle = ""
    for i in range(1, size + 1):
        triangle += '*' * i + '<br>'
    return f"<html><body><pre>{triangle}</pre></body></html>"


def reverse_triangle(size):
    for i in range(size, 0, -1):
        print('*' * i)











if __name__ == "__main__":
    app.run(debug=True)