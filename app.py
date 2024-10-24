from flask import Flask, redirect, url_for, render_template, request, session
import os
import http.client
import requests
import json

app = Flask(__name__)

app.secret_key = '6FD9BCTH3ONLY0N388A2C7B419A9ABB630'

@app.route("/")
def landing_redirect():
    return redirect("/start")      

@app.route("/landing/")
def landing():
    return render_template("landing.html")

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action_type = request.form.get('action_type')
        
        if action_type == 'signup':
            return handle_signup()
        elif action_type == 'login':
            return handle_login()
    
    return render_template("login.html")

@app.route("/logout/")
def logout():
    if 'email' in session:
        session.clear()
        return redirect("/login/")
    return redirect("/landing/")

@app.route("/start/")
def start():
    session.clear()
    return redirect("/landing/")

@app.route("/sources/")
def sources():
    return render_template("sources.html")

@app.route("/dashboard/")
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    return render_template("dashboard.html")

@app.route("/dashboard/hackathons", methods=['GET'])
def pullUrlSearch():
    searchCity = request.args.get('city')
    searchState = request.args.get('states')
    searchDistance = request.args.get('distance')

    lat, lng = lat_and_lng(searchCity, searchState)

    user_email = session.get('email')

    if lat and lng:
        located_cities = get_close_cities(lat, lng, searchDistance)

        citiesList = []
        if 'data' in located_cities:
            for close_city in located_cities['data']:
                citiesList.append(close_city['city'])

        hackathons = []
        with open('hackathonsPosts.txt', 'r') as file:
            for line in file:
                fullName, existCity, existState, collaboratePost, serverLink, software, email = line.strip().split(',')
                print(f"Processing line: {line}")
                if existState == searchState and existCity in citiesList:
                    print(f"Email matched for hackathon: {user_email}")
                    if email == user_email:
                        hackathon = {
                            'name': fullName,
                            'matchCity': existCity,
                            'matchState': existState,
                            'collaborate': collaboratePost,
                            'discordLink': serverLink,
                            'usedSoftware': software,
                            'email' : email,
                            'can_delete': (email == user_email)
                        }
                    
                    else:
                        hackathon = {
                            'name': fullName,
                            'matchCity': existCity,
                            'matchState': existState,
                            'collaborate': collaboratePost,
                            'discordLink': serverLink,
                            'usedSoftware': software,
                            'can_delete' : False
                        }

                    hackathons.append(hackathon)
        
        return render_template('joinhackathon.html', hackathons=hackathons)

    return redirect("/dashboard")


def lat_and_lng(city, state):
    api_key = 'AIzaSyA_Vg3vmRKWO_hLlkAzcKvU1lf1FMYf_k0'
    webUrl = f"https://maps.googleapis.com/maps/api/geocode/json?address={city},{state}&key={api_key}"
    results = requests.get(webUrl)
    resultsData = results.json()

    if resultsData['status'] == 'OK':
        cords = resultsData['results'][0]['geometry']['location']
        return cords['lat'], cords['lng']
    return None, None

def get_close_cities( lat, lng, radius ):

    conn = http.client.HTTPSConnection("wft-geo-db.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "87a6bd5685msh013d8e0f76623bdp141736jsnef565079f582",
        'x-rapidapi-host': "wft-geo-db.p.rapidapi.com"
    }

    url = f"/v1/geo/locations/{lat}{lng}/nearbyCities?radius={radius}&distanceUnit=MI&limit=10"

    conn.request("GET", url, headers=headers)

    res = conn.getresponse()
    data = res.read()

    nearby_cities = json.loads(data.decode("utf-8"))

    return nearby_cities

@app.route("/home")
def home():
    return redirect("/landing")

@app.route("/dashboard/createHackathon/")
def createHackathon():
    return render_template("createHackathon.html")

@app.route("/submitHackathon", methods=["POST"])
def submitHackathon():

    full_name = request.form.get("fullName")
    city = request.form.get("city")
    state = request.form.get("state")
    collaboratePost = request.form.get("collaboratePost")
    serverLink = request.form.get("serverLink")
    software = request.form.get("software")
    email = request.form.get("email")

    with open('hackathonsPosts.txt', 'a') as file:
        file.write(f"{full_name},{city},{state},{collaboratePost},{serverLink},{software},{email}\n")

    return redirect("/dashboard")

@app.route('/delete_hackathon', methods=['POST'])
def delete_hackathon():
    email_to_delete = request.form.get('email')

    with open('hackathonsPosts.txt', 'r') as f:
        lines = f.readlines()

    with open('hackathonsPosts.txt', 'w') as f:
        for line in lines:
            if email_to_delete not in line:
                f.write(line)

    return redirect('/dashboard/hackathons')

def handle_signup():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')

    if not first_name or not last_name or not email or not password:
        return("All fields are required")

    with open('accounts.txt', 'a') as file:
        file.write(f"{email},{password}\n")

    return redirect("/landing/")

def handle_login():
    email = request.form.get('email')
    password = request.form.get('password')

    if os.path.exists('accounts.txt'):
        with open('accounts.txt', 'r') as file:
            for line in file:
                if line.isspace():
                    continue
                else:
                    stored_email, stored_password = line.strip().split(',')
                    if stored_email == email and stored_password == password:
                        session['email'] = email
                        return redirect("/landing/")

    return("Invalid email or password.")

if __name__ == "__main__":
    app.run()