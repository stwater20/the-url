from flask import Flask, request, render_template, make_response, send_from_directory
import datetime
import hashlib
import mysql.connector
import urllib.parse
from urllib.parse import unquote

app = Flask(__name__)


mydb = mysql.connector.connect(
    host="theurl-db.mysql.database.azure.com",
    user="stwater20",
    password="Tonton!@#$81903",
    database="theurl_system"
)


def connection():
    """Get a connection and a cursor from the pool"""
    db = mysql.connector.connect(pool_name='batman')
    return db


def check_url(url):
    mycursor = mydb.cursor()
    print(url)
    mycursor.execute(
        "SELECT new_url FROM urls where `old_url`= \"" + url + "\"")
    myresult = mycursor.fetchone()
    mycursor.close()
    return myresult


def check_hash(hash_value):
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT * FROM urls where `new_url`= \""+hash_value + "\"")
    myresult = mycursor.fetchone()
    mycursor.close()
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
        mydb = connection()
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


def count_url(url):
    mycursor = mydb.cursor()
    print(url)
    mycursor.execute(
        "SELECT click_count FROM urls where `new_url`= \"" + url + "\"")
    myresult = mycursor.fetchone()
    mycursor.close()
    count = int(myresult[0]) + 1
    mycursor = mydb.cursor()
    sql = "UPDATE `theurl_system`.`urls` SET `click_count` = " + \
        "\""+str(count)+"\""+"WHERE `new_url` = " + "\"" + url + "\""
    mycursor.execute(sql)


def get_url(url):
    mycursor = mydb.cursor()
    print(url)
    mycursor.execute(
        "SELECT old_url FROM urls where `new_url`= \"" + url + "\"")
    myresult = mycursor.fetchone()
    mycursor.close()
    return myresult


def IsConnectionFailed(url):
    if "http" in url or "https" in url:
        return True
    else:
        return False


def clean_url(url):
    # $-_.+!*'(),
    specialChars = "!^*(),"
    txt = url
    for specialChar in specialChars:
        txt = txt.replace(specialChar, '')
    return txt


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/url-create", methods=["POST"])
def posturl():
    global mydb
    try:
        mydb.cursor()
    except mysql.connector.Error as err:
        mydb = mysql.connector.connect(
            host="theurl-db.mysql.database.azure.com",
            user="stwater20",
            password="Tonton!@#$81903",
            database="theurl_system"
        )

    if request.method == "POST":
        url = request.form["theurl"]
        if not IsConnectionFailed(url):
            response = make_response("原始網址不存在", 200)
            response.mimetype = "text/plain"
            return response
        rh = insert_url(url)
        if "127.0.0.1" in str(request.url_root) or "localhost" in str(request.url_root):
            rh = str(request.url_root)+rh
        else:
            rh = "https://theurl.tw/"+rh
        response = make_response(str(rh), 200)
        response.mimetype = "text/plain"
        return response


@app.route("/<url>")
def newurl(url):
    try:
        if not IsConnectionFailed:
            return render_template("index.html")
        url = clean_url(url)
        u = url.split("/")
        if len(u) >= 4:
            return render_template("index.html")
        response = get_url(u[len(u)-1])
        if response:
            count_url(u[len(u)-1])
            return render_template("route.html", url=unquote(response[0]))
        else:
            return render_template("index.html")
    except Exception as e:
        print(e)
        return render_template("index.html")


@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == "__main__":
    # port = int(os.environ.get('PORT', 80))
    # app.run(host='0.0.0.0', port=port, debug=True)
    app.run()
