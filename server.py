from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
import re
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "GogurtIsSuperiorYogurt"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASS_REGEX = re.compile(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,20}$')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    session.clear()
    if len(request.form['fname']) < 2:
        flash("Please enter a first name that is two characters or longer")

    if len(request.form['lname']) < 2:
        flash("Please enter a last name that is two characters or longer")

    mysql = connectToMySQL("the_wall")
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Email is not valid!")

    query = "SELECT email FROM users WHERE EXISTS (SELECT email FROM users WHERE email=%(em)s);"
    data = {
        "em": request.form['email']
    }

    if mysql.query_db(query, data):
        flash("That email already exists")

    if not PASS_REGEX.match(request.form['pass']):
        flash("Password must be between 8 and 20 characters long contain at least one uppercase letter, one lowercase letter, and one number")

    if request.form['pass'] != request.form['cpass']:
        flash("Passwords must match!")

    if not '_flashes' in session.keys(): 
        pw_hash = bcrypt.generate_password_hash(request.form['pass'])
        mysql = connectToMySQL("the_wall")
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pw)s, NOW(), NOW());"
        data = {
            "fn": request.form['fname'],
            "ln": request.form['lname'],
            "em": request.form['email'],
            "pw": pw_hash
        }
        user_id = mysql.query_db(query, data)
        flash("CONGRATULATIONS YOU SUCCESSFULLY CREATED AN ACCOUNT!!!!!")
        flash("YEWWW TIME TO GET SENDY WITH IT BAYBAY")

        mysql = connectToMySQL("the_wall")
        query = "SELECT * FROM users WHERE id = %(id)s;"
        data = {
            "id": user_id
        }
        cur_user = mysql.query_db(query, data)

        if 'user' not in session:
            session['user'] = cur_user
        else:
            session['user'] = cur_user

        return redirect("/logged_in")

    print("*"*100)
    return redirect("/")

@app.route('/login', methods=['POST'])
def login():
    mysql = connectToMySQL("the_wall")
    query = "SELECT * FROM users WHERE email=%(em)s;"
    data = {
        "em": request.form['email'],
    }
    session['user'] = mysql.query_db(query, data)

    if session['user']:
        if bcrypt.check_password_hash(session['user'][0]['password'], request.form['pass']):
            return redirect("/logged_in")
    
    flash("We couldn't log you in please try again", "error")
    return redirect('/')

    # if mysql.query_db(query, data) and bcrypt.check_password_hash(pw_hash, )

@app.route('/logout')
def logout():
    session.clear()
    print(session)
    return redirect('/')

@app.route('/logged_in')
def logged_in():
    print(session)
    if 'user' in session:
        mysql = connectToMySQL("the_wall")
        users = mysql.query_db("SELECT * FROM users;")
        mysql = connectToMySQL("the_wall")
        messages = mysql.query_db("SELECT * FROM messages JOIN users ON users.id = messages.users_id;")
        return render_template('wall.html', users=users, messages=messages)

    flash("You need to be logged in!")
    return redirect('/')

@app.route('/send', methods=["POST"])
def send_message():
    if len(request.form['message']) > 240 or len(request.form['message']) <= 5 :
        flash("Your message was too many or too few characters! Please try again")
        return redirect('logged_in')

    if session['user'][0]['id']:
        mysql= connectToMySQL("the_wall")
        query = "INSERT INTO messages (text, created_at, updated_at, users_id, reciever_id) VALUES (%(tx)s, NOW(), NOW(), %(ud)s, %(rd)s );"

        data = {
            "ud": session['user'][0]['id'],
            "tx": request.form['message'],
            "rd": request.form['hidden']

        }

        print("Going to insert yer data")
        mysql.query_db(query, data)
        print("Boy Oh boy that data was sent")
        flash("Your message has been sent!")
    return redirect('logged_in')

@app.route('/delete/<id>')
def delete(id):
    if 'user' in session:
        mysql = connectToMySQL("the_wall")
        mysql = connectToMySQL("the_wall")
        query = "DELETE FROM messages WHERE messages.id = %(id)s AND messages.reciever_id = %(uid)s;"
        data = {
            "id": id,
            "uid": session['user'][0]['id']
        }
        mysql.query_db(query, data)
    return redirect('logged_in')

if __name__ == "__main__":
    app.run(debug=True)