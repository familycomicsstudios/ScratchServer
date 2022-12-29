"""
DO NOT OPEN PROJECT FILES!!!
IT BREAKS THEM!
DO NOT VIEW ANY FILES IN PROJECTS FOLDER
"""
# Disable GIFs please
from base64 import b64encode
from flask import Flask
from flask import send_from_directory, render_template, request, redirect, session, abort
from requests import get
from flask_cors import CORS
import os, json, string, random

app = Flask(__name__, static_folder="static")

devs = ["know0your0true0color", "The_Mad_Punter", "jwklongYT"]

cors = CORS(app, resources={r"/foo": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['UPLOAD_FOLDER'] = "projects"
app.config['MAX_CONTENT_PATH'] = 50000000

app.config["SECRET_KEY"] = os.environ['SECRET_KEY']


def b64(string):
    return b64encode(string.encode("utf-8")).decode()
#read repl chatt
@app.route("/del/<id>")
def delete_file(id):
    id = int(id)
    try:
        if not session["username"] in devs:
            return """<script>window.location.replace("https://PMProjectServer.101freshpenguin.repl.co");</script>"""
    except:
        return "nono"
    with open("names.json", "r") as nm:
        nm = json.load(nm)
        nm[id] = {
        "name": "Deleted",
        "desc": "Deleted",
        "notes": "Deleted",
        "file": "no", # file isnt a thing
        "thumb": "no"
    }
    with open("names.json", "w") as names:
        json.dump(nm, names, indent=4)
        names.close()
    return "done"
        

@app.route('/')
def home():
    with open("names.json", "r") as nm:
        try:
            template_data = {
                "username": session['username'],
                "saves": nm.read()
            }
        except:
            template_data = {"saves": nm.read()}
    return render_template("home.html", **template_data)


@app.route("/login")
def login():
    return redirect(
        f"https://auth.itinerary.eu.org/auth/?redirect={ b64('https://PMProjectServer.101Freshpenguin.repl.co/authenticate') }&name=PM Project Sharing"
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
    with open("names.json", "r") as nm:
        nm = json.load(nm)
    try:
        return send_from_directory('projects', nm[int(path)]["file"])
    except IndexError:
        abort(404)


@app.route('/project/<id>')
def project(id):
    with open("names.json", "r") as nm:
        nm = json.load(nm)
    try:
        template_data = {
            'id': id,
            'name': nm[int(id)]['name'],
            'notes': nm[int(id)]['notes'],
            'desc': nm[int(id)]['desc'],
            'thumb': nm[int(id)]['thumb']
        }
        return render_template("project.html", **template_data)
    except IndexError:
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
    if not (request.form['filename']
            == None) and not (request.files['thumb'].read() == None) and not (
                request.files['file'].read()
                == None) and request.files["file"].filename.endswith(".sb3"):
        name = request.form['filename']
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        filename = ''.join(random.choice(letters) for i in range(32))
        open("projects/" + str(filename) + ".sb3", 'ab').close()
        with open("projects/" + str(filename) + ".sb3", 'wb') as fp:
            fp.write(request.files['file'].read())
        with open("names.json", "r") as nms:
            nms = json.load(nms)
        project_no = len(nms)
        datas = {
            "id": project_no,
            "file": filename + ".sb3",
            "name": name,
            "desc": request.form["desc"],
            "notes": request.form["notes"],
            "thumb": str(b64encode(request.files["thumb"].read()))[2:-1]
        }
        with open("names.json", "r") as nm:
            nm = json.load(nm)
            nm.append(datas)
        with open("names.json", "w") as names:
            json.dump(nm, names, indent=4)
            return 'file uploaded successfully. Your ID is ' + str(
                project_no) + "."
            names.close()
    else:
        return render_template("badupload.html")


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
