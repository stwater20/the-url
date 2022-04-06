import os
from urllib.request import Request
from flask import Flask, request, render_template, make_response
import datetime
import hashlib
import mysql.connector
import urllib.parse
from urllib.parse import unquote

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="theurl_system"
)


def check_url(url):
    mycursor = mydb.cursor()
    print(url)
    mycursor.execute(
        "SELECT new_url FROM urls where `old_url`= \"" + url + "\"")
    myresult = mycursor.fetchone()
    return myresult


def check_hash(hash_value):
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM urls where `new_url`= \""+hash_value + "\"")
    myresult = mycursor.fetchone()
    return myresult


def create_hash(url):
    s = hashlib.sha1()
    url_datetime = url + str(datetime.datetime.now())
    s.update(str(url_datetime).encode("UTF8"))
    h = s.hexdigest()
    rh = str(h[0:6])
    if check_hash(rh):
        create_hash(url)
    else:
        return rh


def insert_url(url):
    url = urllib.parse.quote_plus(url)
    response = check_url(url)
    if response:
        return response[0]
    else:
        hash_url = create_hash(url)
        mycursor = mydb.cursor()
        print(hash_url)
        sql = "INSERT INTO `theurl_system`.`urls`(`old_url`,`new_url`,`timestamp`,`click_count`) VALUES (" \
            + "\"" + str(url) + "\"," \
            + "\"" + str(hash_url) + "\"," \
            + "\"" + str(datetime.datetime.now()) + "\"," \
            + "\"" + str("0") + "\"" \
            + ");"
        print(sql)
        mycursor.execute(sql)
        mydb.commit()
        return str(hash_url)


def get_url(url):
    mycursor = mydb.cursor()
    print(url)
    mycursor.execute(
        "SELECT old_url FROM urls where `new_url`= \"" + url + "\"")
    myresult = mycursor.fetchone()
    return myresult[0]


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/url-create", methods=["POST"])
def posturl():
    if request.method == "POST":
        url = request.form["theurl"]
        rh = insert_url(url)
        rh = str(request.url_root)+rh
        response = make_response(str(rh), 200)
        response.mimetype = "text/plain"
        return response


@app.route("/<url>")
def newurl(url):
    u = url.split("/")
    response = get_url(u[len(u)-1])
    if response:
        return render_template("route.html", url=unquote(response))
    else:
        return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
