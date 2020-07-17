
# Timezone Keeper Web-App

### Backend sercice
The backend is flask app using a sqlite3 db and JWT web tokens

### Building the backend
Note!: python3 and pip3 need to be installed beforehand
Note!: all command must be run from the timezone-keeper-backend directory

Create a virtual environment and install project dependencies
```
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
```


### Running the backend unit-tests

```
pip3 install -r test-requirements.txt
./run-tests.sh
```

### Running the backend server
Running the service
```
python3 main.py
```
The service runs on http://localhost:7777
You can navigate to http://localhost:7777/api/v1/ to bring up the live swaggerdoc and interract with the API



### Frontend sercice

The frontend is a Vue.js application running on http://localhost:8080

### Building the frontend
Note!: all command must be run from the timezone-keeper-backend directory

```
npm install
```

### Running the frontend app

```
npm start
```

Open http://localhost:7777 in your browser