from flask import Flask, render_template, request, render_template_string
import sqlite3

# Constants
MAX_NAME_CHARACTER = 30
MAX_REVIEW_CHARACTER = 500
MAX_FRAGRANCE_ID = 12

app = Flask(__name__)


# Fetch funtion
# Function parametre determines if it is a fetchone or fetchall
def fetch(query, function=0, parameter=()):
    connection = sqlite3.connect('fragrance.db')
    cur = connection.cursor()
    # excutes that query that is passed on
    cur.execute(query, parameter)
    if function == 1:
        result = cur.fetchone()
    else:
        result = cur.fetchall()
    connection.close()
    return result


# Routes
# Route for homepage
@app.route("/")
def home():
    # This query selects the brand names
    # To display all featured brands in homepage
    query = "SELECT brand_name FROM Designer;"
    # Fetches all the brand names
    fragrance_brand = fetch(query)
    return render_template("home.html", brands=fragrance_brand)


# Route for EDP page
@app.route("/EDP")
def edp():
    # This query selects all the relevant general info for edp fragrance
    # It uses joins to connect the fragrance and designer tables together
    # This is to show the fragrance and their corrosponding brands
    fragrance_query = '''SELECT bottle_id, bottle_name FROM Fragrance
        INNER JOIN Designer ON Fragrance.bottle_brand = Designer.brand_id
        WHERE bottle_concentration = 'EDP';'''
    # This query gets the edp concentration
    concentration_query = '''SELECT bottle_concentration
        FROM Fragrance WHERE bottle_concentration = 'EDP';'''
    fragrance_result = fetch(fragrance_query)
    fragrance_concentration = fetch(concentration_query, function=1)
    return render_template("all_fragrances.html", fragrances=fragrance_result,
                           concentration=fragrance_concentration)


# Route for individual bottle information
@app.route("/fragrance/<int:id>")
def bottle(id):
    # checks if less than 0 or greater than 12
    # displays the 404 page if it doesn't meet conditions
    if id <= 0:
        return page_not_found(404)
    elif id > MAX_FRAGRANCE_ID:
        return page_not_found(404)
    else:
        # This query selects in depth details about the particular fragrance
        info_query = '''SELECT bottle_name, bottle_description,
            bottle_concentration, bottle_longevity, bottle_size,
            bottle_price, bottle_photo FROM Fragrance WHERE
            bottle_id = ?;'''
        # This query joins the designer and fragrance table together
        # And selects brand name for the particular fragrance
        brand_query = '''SELECT brand_name FROM Fragrance
            INNER JOIN Designer ON Fragrance.bottle_brand =
            Designer.brand_id WHERE bottle_id = ?;'''
        # This query shows what notes a particular fragrance has
        # Because 1 fragrance can have many notes
        # and 1 note could be in many fragrances
        # A bridging table, Notebridge is used to join everything together
        notes_query = '''SELECT bottle_name, note_name FROM Notebridge
            INNER JOIN Note ON Notebridge.nid = Note.note_id
            INNER JOIN Fragrance ON Notebridge.fid = Fragrance.bottle_id
            WHERE bottle_id = ?;'''
        # feches all relevant info and displays on website
        fragrance_info = fetch(info_query, function=1, parameter=(id,))
        fragrance_brand = fetch(brand_query, function=1, parameter=(id,))
        fragrance_note = fetch(notes_query, parameter=(id,))
        return render_template("bottle_info.html", notes=fragrance_note,
                               brand=fragrance_brand, info=fragrance_info)


# Route for comparision page
@app.route("/comparision")
def comparision():
    # These 2 queries selects relevant info to compare the frgrances
    edt_query = '''SELECT bottle_name, brand_name, bottle_longevity,
        bottle_size, bottle_price, bottle_photo FROM Fragrance
        INNER JOIN Designer ON Fragrance.bottle_brand = Designer.brand_id
        WHERE bottle_concentration = 'EDT';'''
    edp_query = '''SELECT bottle_name, brand_name, bottle_longevity,
        bottle_size, bottle_price, bottle_photo FROM Fragrance
        INNER JOIN Designer ON Fragrance.bottle_brand = Designer.brand_id
        WHERE bottle_concentration = 'EDP';'''
    edt_result = fetch(edt_query)
    edp_result = fetch(edp_query)
    return render_template('comparision.html',
                           edt_comparision=edt_result,
                           edp_conparision=edp_result)


# Form page
@app.route("/form")
def form():
    # This query displays approved reviews only
    # 1 in review_approval is approved
    review_query = '''SELECT review_username, bottle_name, review_content
        FROM Fragrance INNER JOIN Form ON Fragrance.bottle_id = Form.review_fid
        WHERE review_approval = 1;'''
    fragrance_reviews = fetch(review_query)
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
    elif len(username) > MAX_NAME_CHARACTER:
        return render_template_string('''Error: Name too long. Please enter a
                                      name under 30 characters.
                                      <a href="http://127.0.0.1:5000/form">
                                      Go back to the form</a>''')
    # Checks if review is longer than 40 characters
    elif len(review) > MAX_REVIEW_CHARACTER:
        return render_template_string('''Error: Your review is too long.
                                      Please shorten it to 500 characters.
                                      <a href="{{ url_for('form') }}">
                                      Go back to the form</a>''')
    else:
        connection = sqlite3.connect("fragrance.db")
        cur = connection.cursor()
        # This query inserts review into the database
        # The table is expected to have columns: review_username,
        # review_fid, and review_content
        cur.execute('''INSERT INTO Form (review_username, review_fid,
                    review_content) VALUES (?,?,?)''',
                    # The values that is inserted are provided as a tuple
                    # username is name of the user
                    # fid is the fragrance id
                    # review is the concent of the review
                    (username, fid, review,))
        connection.commit()
        connection.close()
        # Displays an success message on review_submit.html
        return render_template("review_submit.html")


# Route for EDT page
@app.route("/EDT")
def edt():
    # This query selects all the relevant general info for edt fragrance
    # It uses joins to connect the fragrance and designer tables together
    # This is to show the fragrance and their corrosponding brands
    fragrance_query = '''SELECT bottle_id, bottle_name FROM Fragrance
        INNER JOIN Designer ON Fragrance.bottle_brand = Designer.brand_id
        WHERE bottle_concentration = 'EDT';'''
    # This query gets the edt concentration
    concentration_query = '''SELECT bottle_concentration
        FROM Fragrance WHERE bottle_concentration = 'EDT';'''
    fragrance_result = fetch(fragrance_query)
    fragrance_concentration = fetch(concentration_query, function=1)
    return render_template("all_fragrances.html", fragrances=fragrance_result,
                           concentration=fragrance_concentration)


# Search route
@app.route("/search", methods=["POST"])
def search():
    # Retrive the search term from the user and converts it to lowercase
    # This makes the search case insensitive
    search = request.form["search_bar"].lower()
    connection = sqlite3.connect("fragrance.db")
    cur = connection.cursor()
    # The SQL query allows user to search for fragrances by name,
    # brand or concentration
    # The LIKE operator is used for partial matches
    # The query joins the Fragrance and Designer tables togther
    cur.execute('''SELECT bottle_name, brand_name, bottle_concentration,
                bottle_id FROM Fragrance INNER JOIN Designer ON
                Fragrance.bottle_brand = Designer.brand_id WHERE
                LOWER(bottle_name) LIKE ?
                OR LOWER(bottle_concentration) LIKE ?
                OR LOWER(brand_name) LIKE ?;''',
                # The % signs are wildcards that allow for matches that contain
                # the search term anywhere in the string
                # For example, a search of 'male' will match with 'Le Male'
                ('%' + search + '%', '%' + search + '%', '%' + search + '%',))
    search_results = cur.fetchall()
    connection.close()
    # checks if the result are fasly values
    if not search_results:
        # displays error message if no results
        return render_template("no_results.html")
    else:
        # displays search results
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
