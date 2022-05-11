# review-planner

## Running locally
```shell
cd c:\path\to\app
set OAUTHLIB_INSECURE_TRANSPORT=1
set FLASK_APP=index
set FLASK_SECRET_KEY=ignored
set FLASK_ENV=development
set /p CLIENT_SECRET_JSON=<C:\path\to\client_secret.json
flask run
```

and then access the app on http://localhost:5000