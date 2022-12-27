from base64 import b64encode
from flask import Flask
from flask import send_from_directory, render_template, request, redirect, session, abort
import os
from replit import db
from requests import get
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_folder="static")

cors = CORS(app, resources={r"/foo": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['UPLOAD_FOLDER'] = "projects"
app.config['MAX_CONTENT_PATH'] = 50000000

app.config["SECRET_KEY"] = os.environ['SECRET_KEY']


def base64(string):
    return b64encode(string.encode("utf-8")).decode()


@app.route('/')
def home():
    try:
        template_data = {"username": session['username']}
    except:
        template_data = {}
    return render_template("home.html", **template_data)


@app.route("/login")
def login():
    return redirect(
        f"https://auth.itinerary.eu.org/auth/?redirect={ base64('https://ShredProjectServer.themadpunter.repl.co/authenticate') }&name=Shred Server"
    )


@app.get("/authenticate")
def handle():
    privateCode = request.args.get("privateCode")

    if privateCode == None:
        return "Bad Request", 400

    resp = get(
        f"https://auth.itinerary.eu.org/api/auth/verifyToken?privateCode={privateCode}"
    ).json()
    if True:
        if resp["valid"]:
            session["username"] = resp["username"]
            return redirect("/")
        else:
            return "Authentication failed - please try again later."
    else:
        return "Invalid Redirect", 400


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route('/projects/download/<path>')
def send_report(path):
    try:
        return send_from_directory('projects', db["projects"][path]["file"])
    except KeyError:
        abort(404)


@app.route('/project/<id>')
def project(id):
    try:
        template_data = {'id': id, 'name': db["projects"][id]['name']}
        return render_template("project.html", **template_data)
    except KeyError:
        abort(404)

    


@app.route('/upload')
def upload_file():
    try:
        template_data = {"username": session["username"]}
    except:
        template_data = {}
    return render_template('upload.html', **template_data)


@app.route('/uploader', methods=['GET', 'POST'])
def uploader_file():
    global db
    dir_path = 'projects'
    count = 0
    # Iterate directory
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            count += 1
    if request.method == 'POST':
        f = request.files['file']
        name = request.form['filename']
        filename = str(os.urandom(16))
        project_no = len(db["projects"]) + 1
        f.save("projects/" + str((filename)) + ".sb3")
        db["projects"][str(project_no - 1)] = {
            "id": project_no,
            "file": filename + ".sb3",
            "name": name
        }
        return 'file uploaded successfully'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def we_did_an_oopsie(e):
    return render_template('500.html'), 500

CORS(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


app.run("0.0.0.0", port=8000)