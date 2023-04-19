import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Set up logging
logging.basicConfig(
    filename='/var/log/mushroom.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Firebase configuration
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-database-url.firebaseio.com/'
})

# Weather API configuration
API_KEY = 'your_openweathermap_api_key'
API_URL = 'http://api.openweathermap.org/data/2.5/weather'

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'your_email@example.com'
SENDER_PASSWORD = 'your_email_password'
RECIPIENT_EMAIL = 'recipient_email@example.com'

def get_weather_data(lat, lon):
    payload = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(API_URL, params=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching weather data: {response.text}")

def mushroom_probability(weather_data_list):
    suitable_conditions_count = 0
    for data in weather_data_list:
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        if 18 <= temp <= 24 and humidity >= 80:
            suitable_conditions_count += 1

    probability = suitable_conditions_count / len(weather_data_list) * 100
    return probability

def send_email(weather_data_list, probability):
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = RECIPIENT_EMAIL
    message['Subject'] = 'Mushroom Probability Report'

    text = f"Вероятността за поникване на гъби е {probability:.2f}%.\n\n"
    text += "Weather data:\n"
    for data in weather_data_list:
        text += json.dumps(data) + "\n"

    message.attach(MIMEText(text, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
        server.quit()
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def save_weather_data_to_firebase(weather_data):
    ref = db.reference('weather_data')
    ref.push(weather_data)

def read_weather_data_from_firebase():
    ref = db.reference('weather_data')
    weather_data_list = list(ref.get().values())
    return weather_data_list

def email_sent_today(log_filename):
    try:
        with open(log_filename, 'r') as f:
            last_sent_date = f.read().strip()
            return last_sent_date == str(current_date)
    except FileNotFoundError:
        return False

def main():
    lat = 42.698334
    lon = 23.319941
    current_date = datetime.now().date()

    weather_data = get_weather_data(lat, lon)
    save_weather_data_to_firebase(weather_data)

    weather_data_list = read_weather_data_from_firebase()[-72:]

    probability = mushroom_probability(weather_data_list)
    logging.info(f"Probability of mushrooms: {probability:.2f}%")

    if probability > 70 and not email_sent_today('/var/log/mushroom_email_sent.log'):
        send_email(weather_data_list, probability)
        with open('/var/log/mushroom_email_sent.log', 'w') as f:
            f.write(str(current_date))

if __name__ == "__main__":
    main()
