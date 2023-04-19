# mushroom-predictor
Python script for mushroom prediction with e-mail notification

Before you begin, you will need to register for an API key here [OpenWeatherMap](https://link-url-here.org)https://openweathermap.org/api)

# Use Firebase Realtime Database

* Create a Firebase project: Go to the Firebase Console and sign in with your Google account. Create a new project by clicking on "Add project" and following the on-screen instructions.

* Enable Realtime Database: Once your project is created, click on "Realtime Database" in the left-hand menu, and then click on the "Create database" button. Choose a location for your database and click "Done".

* Set up Firebase Admin SDK: In the Firebase Console, click on the gear icon next to "Project Overview" and select "Project settings". Then, go to the "Service accounts" tab and click on "Python" under "Admin SDK configuration snippet". Follow the instructions to set up the Firebase Admin SDK in your Python environment.

**Warning**
Remember to replace 'path/to/serviceAccountKey.json' with the path to your service account key file and 'https://your-database-url.firebaseio.com/' with the URL of your Firebase Realtime Database.

# Logger
**Note**
Please note that you may need to start the script with administrative privileges in order for it to create and write to the log file in the /var/log directory.

# Crontab
To set up a cron job to run the script every hour, open a terminal and enter crontab -e to edit the crontab file. Add the following line at the end of the file, replacing /path/to/predictor.py with the full path to the script:

```console
0 * * * * /path/to/venv/bin/python3 /path/to/predictor.py
```

# Venv

```console
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

