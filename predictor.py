import os
import sys
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

def load_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

config = load_config('config.json')

# Weather API configuration
API_KEY = config['openweathermap_api_key']
API_URL = config['api_url']

# Email configuration
SENDER_EMAIL = config['email']['sender_email']
SENDER_PASSWORD = config['email']['sender_password']

# Firebase configuration
cred = credentials.Certificate(config['firebase']['service_account_key'])
firebase_admin.initialize_app(cred, {
    'databaseURL': config['firebase']['database_url']
})

def check_and_create_log_file(log_file_path):
    try:
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w') as log_file:
                log_file.write("")

        if not os.access(log_file_path, os.W_OK):
            print(f"Error: Log file '{log_file_path}' is not writable.")
            sys.exit(1)

    except Exception as e:
        print(f"Error checking or creating log file '{log_file_path}': {e}")
        sys.exit(1)

# Set up logging
LOG_FILE_PATH = "/var/log/mushroom.log"
check_and_create_log_file(LOG_FILE_PATH)
logging.basicConfig(
    filename='LOG_FILE_PATH',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Email configuration
SENDER_EMAIL = config['email']['sender_email']
SENDER_PASSWORD = config['email']['sender_password']
RECIPIENT_EMAIL = config['email']['recipient_email']
SMTP_SERVER = config['email']['smtp_server']
SMTP_PORT = config['email']['smtp_port']

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

def format_weather_data_as_table(weather_data_list):
    table_header = "<tr><th>Date & Time</th><th>Temperature (°C)</th><th>Humidity (%)</th></tr>"
    table_rows = [
        f"<tr><td>{data['dt']}</td><td>{data['temp']:.2f}</td><td>{data['humidity']}</td></tr>"
        for data in weather_data_list
    ]
    table = f"<table border='1'>{table_header}{''.join(table_rows)}</table>"
    return table

def calculate_daily_averages(weather_data_list):
    daily_data = {}
    for data in weather_data_list:
        date = data['dt'].split(' ')[0]
        if date not in daily_data:
            daily_data[date] = {'temp': [], 'humidity': []}
        daily_data[date]['temp'].append(data['temp'])
        daily_data[date]['humidity'].append(data['humidity'])

    daily_averages = {}
    for date, values in daily_data.items():
        avg_temp = sum(values['temp']) / len(values['temp'])
        avg_humidity = sum(values['humidity']) / len(values['humidity'])
        daily_averages[date] = {'avg_temp': avg_temp, 'avg_humidity': avg_humidity}

    return daily_averages

def send_email(weather_data_list, probability):
    table = format_weather_data_as_table(weather_data_list)
    daily_averages = calculate_daily_averages(weather_data_list)

    daily_averages_table = "<h3>Daily Averages:</h3>"
    daily_averages_table += "<table border='1'><tr><th>Date</th><th>Avg Temp (°C)</th><th>Avg Humidity (%)</th></tr>"
    for date, averages in daily_averages.items():
        daily_averages_table += f"<tr><td>{date}</td><td>{averages['avg_temp']:.2f}</td><td>{averages['avg_humidity']:.2f}</td></tr>"
    daily_averages_table += "</table>"

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Mushroom Alert: {probability:.2f}% probability"
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL

    html = f"""
    <html>
    <body>
        <h1>Mushroom Alert</h1>
        <p>There is a {probability:.2f}% probability of mushrooms in your area.</p>
        <h3>Weather Data:</h3>
        {table}
        {daily_averages_table}
    </body>
    </html>
    """
    html_part = MIMEText(html, "html")
    message.attach(html_part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        if SENDER_PASSWORD:
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
    
def send_test_email():
    message = MIMEMultipart("alternative")
    message["Subject"] = "Mushroom Alert: Test Email"
    message["From"] = SENDER_EMAIL
    message["To"] = RECIPIENT_EMAIL

    html = """
    <html>
    <body>
        <h1>Mushroom Alert</h1>
        <p>This is a test email. Please ignore it.</p>
    </body>
    </html>
    """
    html_part = MIMEText(html, "html")
    message.attach(html_part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        if SENDER_PASSWORD:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
        server.quit()
        logging.info("Test email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending test email: {e}")

def read_last_run_date(file_path):
    try:
        with open(file_path, 'r') as f:
            last_run_date = f.read().strip()
        return datetime.strptime(last_run_date, "%Y-%m-%d").date()
    except FileNotFoundError:
        return None

def write_last_run_date(file_path, date):
    with open(file_path, 'w') as f:
        f.write(date.strftime("%Y-%m-%d"))

def main():
    LAST_RUN_DATE_FILE = 'last_run_date.txt'
    current_date = datetime.now().date()
    last_run_date = read_last_run_date(LAST_RUN_DATE_FILE)

    if last_run_date is None or last_run_date < current_date:
        send_test_email()
        write_last_run_date(LAST_RUN_DATE_FILE, current_date)

    # Coordinates
    lat = config['coordinates']['lat']
    lon = config['coordinates']['lon']

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
