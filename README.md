# mushroom-predictor
Python script for mushroom prediction with notification e-mail

Преди да започнете, ще трябва да се регистрирате за API ключ в OpenWeatherMap: https://openweathermap.org/api

# use Firebase Realtime Database, follow these steps:

Create a Firebase project: Go to the Firebase Console and sign in with your Google account. Create a new project by clicking on "Add project" and following the on-screen instructions.

Enable Realtime Database: Once your project is created, click on "Realtime Database" in the left-hand menu, and then click on the "Create database" button. Choose a location for your database and click "Done".

Set up Firebase Admin SDK: In the Firebase Console, click on the gear icon next to "Project Overview" and select "Project settings". Then, go to the "Service accounts" tab and click on "Python" under "Admin SDK configuration snippet". Follow the instructions to set up the Firebase Admin SDK in your Python environment.

Install the Firebase Admin SDK: Run the following command in your terminal or command prompt to install the SDK:

**Warning**
Remember to replace 'path/to/serviceAccountKey.json' with the path to your service account key file and 'https://your-database-url.firebaseio.com/' with the URL of your Firebase Realtime Database.

# Logger
Този модифициран скрипт записва всички съобщения, които излизат към конзолата, в стандартен лог файл /var/log/mushroom.log. Обърнете внимание, че може да се наложи да стартирате скрипта с административни права, за да може да създаде и пише в лог файла в директорията /var/log.

# Crontab
За да настроите cron job да изпълнява скрипта на всеки час, отворете терминал и въведете crontab -e, за да редактирате crontab файла. Добавете следния ред в края на файла, като замените /path/to/predictor.py с пълния път до скрипта:

```console
0 * * * * /path/to/venv/bin/python3 /path/to/predictor.py
```

# Venv

```console
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

