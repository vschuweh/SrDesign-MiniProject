# 2019-mini-s24

Starting with the log-in, our web application uses Google OAuth to authorize the login with a token. The application will 
provide the weather if the user's current location as well as graphed data for two seperate sensors (2 rooms). Our application
utilizes two API calls. The program makes a python evironemnt request module to obtain the caller's (user's) IP. The IP is then
used in the ipstack api call to get the user's geolocation. The latitude and longitude values from the geolocation are used as
inputs for the openweathermap api (to get the weather of current location).

A new set of sensor data is generated for each room at each successful login. The sensor is simulated by providing two random 
numbers in the range of 1 to 100 for humidity and 65 to 85 for temperature. Our application uses one SQLite database which 
contains two tables: temperature and sensor. The temperature table includes 4 columns - id, email, sensor number, and date 
created. The sensor table includes 6 columns - id, room, temperature, humidity, sensor number, and date created. The sensor
is a randomly generated number from 1 to 1000 and each user is assigned one sensor number. This number is also used to link 
the two tables together. 

After a successful login through OAuth, the application will check if the email has been previously used to login by searching
for a mathcing email through the email column in the temperature table. If the user exists, the program will record the randomly
generated sensor data to the sensor table. If the user doesn't exist, the program will add the user to the temperature table as
well as it's randomly generated sensor data to the sensor table.

We query the data based upon email id then collect all previous sensor data for that user and plot it. If the user is logging in
for the firt time, there will only be one set of data points for each room. The plot utilizes Google Charts with javascript in html.
Furthermore, we used python flask for the web development, flask-dance for authentication, and flask SQLAlchemy for the database.

Html us used for the front end which can be found under the templates directory. Our application is deployed on the cloud using
pythonanywhere. You may access our web application [here](http://vschuweh.pythonanywhere.com/).

Lastly in GitHub, our localHost branch holds the code we used to run and test our program on our local machine.
