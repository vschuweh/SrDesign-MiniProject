from flask import Flask, redirect, url_for, session, render_template,request
from flask_dance.contrib.google import make_google_blueprint, google
#from flask_login import login_user, logout_user, login_required

import os
import random
import requests


from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, TokenExpiredError, OAuth2Error

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

app = Flask(__name__)

app.secret_key = "supersekrit"
blueprint = make_google_blueprint(
    client_id="346091258469-7qmkik7dk6j10el6urgepvl1h610osh6.apps.googleusercontent.com",
    client_secret="7fHTeRqirbPiYTNSljM4auNr",
    scope=["profile", "email"],
  #  offline=True,
    redirect_url="/app_login"

)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Temperature(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    #location = db.Column(db.String(200), nullable=False)
    #reading=db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    sensor_number = db.Column(db.Integer,nullable=False)

    def __repr__(self):
        return f"Temperature('{self.email}','{self.sensor_number}','{self.date_created}')"

class Sensors(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.Integer, nullable=False)
    temp=db.Column(db.Integer, nullable=False)
    humidity=db.Column(db.Integer, nullable=False)
    sensor_number = db.Column(db.Integer,nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"Sensors('{self.sensor_number}','{self.temp}','{self.humidity}','{self.room}','{self.date_created}')"


app.register_blueprint(blueprint, url_prefix="/login")

@app.route("/app_login")
def index():
    #session.clear() #work around for Oauth token expire error
    if not google.authorized:
        return redirect(url_for("google.login"))


    #session.clear()

    try:
        resp = google.get("/plus/v1/people/me")
        assert resp.ok, resp.text
    except (InvalidGrantError, TokenExpiredError) as e:  # or maybe any OAuth2Error
        return redirect(url_for("google.login"))
    #session.clear()

    email = resp.json()["emails"][0]["value"]

    user = Temperature.query.filter_by(email=email).first()

    #try:
    if user==None:
        sensor=random.randint(0,1000)
        new_user = Temperature(email=email, sensor_number=sensor)
        #new_user = Temperature(location=country+region+city, reading=temp, email=email, sensor_number=sensor)
        db.session.add(new_user)


    else:
        sensor=user.sensor_number

    new_sensor1 = Sensors(room=1, temp=random.randint(65,85),humidity=random.randint(0,100),sensor_number=sensor)
    db.session.add(new_sensor1)

    new_sensor2 = Sensors(room=2, temp=random.randint(65, 85), humidity=random.randint(0, 100), sensor_number=sensor)
    db.session.add(new_sensor2)

    db.session.commit()
    #except:
        #return f'There was an issue adding your data {user.sensor_number}'



    ret_text = "You are {email} on Google".format(email=resp.json()["emails"][0]["value"])
    return redirect(url_for("data", ret_text=ret_text))
    #return "You are {email} on Google".format(email=resp.json()["emails"][0]["value"])

@app.route("/")
def index1():

    return render_template('front.html')

@app.route("/data")
def data():

    if not google.authorized:
        return '<h1 style="text-align: center">You are not logged in</h1>'

    ('this is remote_address')
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
         ipAdd=request.environ['REMOTE_ADDR']
    else:
        ipAdd=request.environ['HTTP_X_FORWARDED_FOR']

    geourl='http://api.ipstack.com/{}?access_key=0a6282da1e588468f7393e09cefe7034'
    geor=requests.get(geourl.format(ipAdd)).json()

    #get geo location of the user -- Get IP of current user device
    #geor=requests.get('http://api.ipstack.com/check?access_key=0a6282da1e588468f7393e09cefe7034').json()
    #print(geor)

    lon = geor['longitude']
    lat = geor['latitude']
    country = geor['country_name']
    region = geor['region_name']
    city = geor['city']
    print(geor)

    #get temperature of the geo location
    url = 'http://api.openweathermap.org/data/2.5/find?lat={}&lon={}&cnt=1&units=imperial&appid=03f5596dd4312075a8353ca25ae0454c'
    rr = requests.get(url.format(lat, lon)).json()

    print(rr)

    temp = rr['list'][0]['main']['temp']

    print(temp)
    req = request.args.get('ret_text')

    info = { #object passed to html
        'userInfo': req,
        'country': country,
        'region': region,
        'city': city,
        'temp': temp
    }

    email = google.get("/plus/v1/people/me").json()["emails"][0]["value"]

    user = Temperature.query.filter_by(email=email).first()


    #try:
    sensors1 = Sensors.query.filter_by(sensor_number=user.sensor_number, room=1).all()
    labels1 = [['Time','Temperature','Humidity']]
    for i in sensors1:
        date1=str(i.date_created)
        labels1.append([date1[:10]+"\n"+date1[11:19],i.temp,i.humidity])

    sensors2 = Sensors.query.filter_by(sensor_number=user.sensor_number, room=2).all()
    labels2 = [['Time', 'Temperature', 'Humidity']]
    for i in sensors2:
        date2 = str(i.date_created)
        labels2.append([date2[:10] + "\n" + date2[11:19], i.temp, i.humidity])

    return render_template('data.html', info=info, labels1=labels1, labels2=labels2)

    #except:
            #return f'There was an issue adding your data'


    #r = random.randint(0, 100)
    #return str(r)

@app.route("/app_logout")
def logout():
    if google.authorized:
        session.clear()

       # token = blueprint.token["access_token"]
       # resp = google.post(
        #    "https://accounts.google.com/o/oauth2/revoke",
        #    params={"token": token},
        #    headers={"Content-Type": "application/x-www-form-urlencoded"}
        #    )
        #assert resp.ok, resp.text

    #logout_user()  # Delete Flask-Login's session cookie
        #del blueprint.token  # Delete OAuth token from storage

    return redirect("/")





if __name__ == "__main__":
    app.run()
