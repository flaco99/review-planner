from flask import Flask, Response
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    message = cow.Cowacter().milk('Hello from Python from a Serverless Function!  yesssssssssss')
    return Response("<pre>/%s</pre>" % (message), mimetype="text/html")
    #return Response("<h1>Flask</h1><p>You visited: /%s</p>" % (path), mimetype="text/html")
    

@app.route('/hello')
def catch_all(path):
    return Response("<pre>/hello something else</pre>", mimetype="text/html")
