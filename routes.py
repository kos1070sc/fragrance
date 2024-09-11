from flask import Flask, render_template, request, render_template_string
import sqlite3

app = Flask(__name__)

# Functions
# These functions uses parametres to prevent sql attacks


# Fetch one function
def fetch_one(query, parameter=()):
    connection = sqlite3.connect('fragrance.db')
    cur = connection.cursor()
    cur.execute(query, parameter)  # excutes that query that is passed on
    result = cur.fetchone()
    connection.close()
    return result


# Fetch all function
def fetch_all(query, parameter=()):
    connection = sqlite3.connect('fragrance.db')
    cur = connection.cursor()
    cur.execute(query, parameter)
    results = cur.fetchall()
    connection.close()
    return results


# Routes
# Route for homepage
@app.route("/")
def home():
    query = "SELECT brand_name FROM Designer;"
    fragrance_brand = fetch_all(query)  # Fetches all the brand names
    return render_template("home.html", brands=fragrance_brand)


# Route for EDP page
@app.route("/EDP")
def edp():
    fragrance_query = '''SELECT bottle_id, bottle_name FROM Fragrance
        INNER JOIN Designer ON Fragrance.bottle_brand = Designer.brand_id
        WHERE bottle_concentration = 'EDP';'''

    concentration_query = '''SELECT bottle_concentration
        FROM Fragrance WHERE bottle_concentration = 'EDP';'''

    fragrance_result = fetch_all(fragrance_query)
    fragrance_concentration = fetch_one(concentration_query)
    return render_template("all_fragrances.html", fragrances=fragrance_result,
                           concentration=fragrance_concentration)


# Route for EDT page
@app.route("/EDT")
def edt():
    fragrance_query = '''SELECT bottle_id, bottle_name FROM Fragrance
        INNER JOIN Designer ON Fragrance.bottle_brand = Designer.brand_id
        WHERE bottle_concentration = 'EDT';'''

    concentration_query = '''SELECT bottle_concentration
        FROM Fragrance WHERE bottle_concentration = 'EDT';'''

    fragrance_result = fetch_all(fragrance_query)
    fragrance_concentration = fetch_one(concentration_query)
    return render_template("all_fragrances.html", fragrances=fragrance_result,
                           concentration=fragrance_concentration)


# Route for individaul bottle information
@app.route("/fragrance/<int:id>")
def bottle(id):
    info_query = '''SELECT bottle_name, bottle_description,
        bottle_concentration, bottle_longevity, bottle_size,
        bottle_price, bottle_photo FROM Fragrance WHERE
        bottle_id = ?;'''

    brand_query = '''SELECT brand_name FROM Fragrance
        INNER JOIN Designer ON Fragrance.bottle_brand =
        Designer.brand_id WHERE bottle_id = ?;'''

    notes_query = '''SELECT bottle_name, note_name FROM Notebridge
        INNER JOIN Note ON Notebridge.nid = Note.note_id
        INNER JOIN Fragrance ON Notebridge.fid = Fragrance.bottle_id
        WHERE bottle_id = ?;'''

    fragrance_info = fetch_one(info_query, (id,))
    fragrance_brand = fetch_one(brand_query, (id,))
    fragrance_note = fetch_all(notes_query, (id,))
    return render_template("bottle_info.html", notes=fragrance_note,
                           brand=fragrance_brand, info=fragrance_info)


# Route for comparision page
@app.route("/comparision")
def comparision():
    edt_query = '''SELECT bottle_name, brand_name, bottle_longevity,
        bottle_size, bottle_price, bottle_photo FROM Fragrance
        INNER JOIN Designer ON Fragrance.bottle_brand = Designer.brand_id
        WHERE bottle_concentration = 'EDT';'''

    edp_query = '''SELECT bottle_name, brand_name, bottle_longevity,
        bottle_size, bottle_price, bottle_photo FROM Fragrance
        INNER JOIN Designer ON Fragrance.bottle_brand = Designer.brand_id
        WHERE bottle_concentration = 'EDP';'''

    edt_result = fetch_all(edt_query)
    edp_result = fetch_all(edp_query)
    return render_template('comparision.html',
                           edt_comparision=edt_result,
                           edp_conparision=edp_result)


# Form page
@app.route("/form")
def form():
    review_query = '''SELECT review_username, bottle_name, review_content
        FROM Fragrance INNER JOIN Form ON Fragrance.bottle_id = Form.review_fid
        WHERE review_approval = 1;'''   # Displays approved reviews only
    fragrance_reviews = fetch_all(review_query)
    return render_template("review.html", reviews=fragrance_reviews)


# Submit review page
@app.route("/submit_review", methods=["POST"])
def submit_review():
    username = request.form["username"]
    fid = request.form["fid"]
    review = request.form["review"]
    # Checks if username or review is null
    if not username or not review:
        return render_template_string('''Error: Cannot have a null input for
                                      name or review. Please fill out the
                                      form fully.<a href=
                                      "http://127.0.0.1:5000/form">
                                      Go back to the form</a>''')
    # Checks if username is longer than 30 characters
    elif len(username) > 30:
        return render_template_string('''Error: Name too long. Please enter a
                                      name under 30 characters.
                                      <a href="http://127.0.0.1:5000/form">
                                      Go back to the form</a>''')
    # Checks if review is longer than 40 characters
    elif len(review) > 500:
        return render_template_string('''Error: Your review is too long.
                                      Please shorten it to 500 characters.
                                      <a href="{{ url_for('form') }}">
                                      Go back to the form</a>''')
    else:
        connection = sqlite3.connect("fragrance.db")
        cur = connection.cursor()
        cur.execute('''INSERT INTO Form (review_username, review_fid,
                    review_content) VALUES (?,?,?)''',
                    (username, fid, review,))
        # insert review into the database
        connection.commit()
        connection.close()
        return render_template("review_submit.html")
        # Displays an success message on review_submit.html


# Search page
@app.route("/search", methods=["POST"])
def search():
    search = request.form["search_bar"].lower()
    # this makes the search case insensitive
    connection = sqlite3.connect("fragrance.db")
    cur = connection.cursor()
    cur.execute('''SELECT bottle_name, brand_name, bottle_concentration,
                bottle_id FROM Fragrance INNER JOIN Designer ON
                Fragrance.bottle_brand = Designer.brand_id WHERE
                LOWER(bottle_name) LIKE ?
                OR LOWER(bottle_concentration) LIKE ?
                OR LOWER(brand_name) LIKE ?;''',
                # the user can search for the name,
                # brand or concentration of the fragrance
                ('%' + search + '%', '%' + search + '%', '%' + search + '%',))
    # return result even if there is only a partial input with LIKE operator
    search_results = cur.fetchall()
    connection.close()
    if not search_results:  # checks if the result are fasly values
        return render_template("no_results.html")
    # displays error message if no results
    else:
        return render_template("search.html", search_results=search_results)


# 404 page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# Some fun triangles!!!
@app.route("/triangle/<int:size>")
def triangle(size):
    triangle = ""
    for i in range(1, size + 1):
        triangle += '*' * i + '<br>'
    return f"<html><body><pre>{triangle}</pre></body></html>"


def reverse_triangle(size):
    for i in range(size, 0, -1):
        print('*' * i)


# Debugger
if __name__ == "__main__":
    app.run(debug=True)
