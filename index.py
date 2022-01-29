from flask import Flask


app = Flask(__name__)


@app.route('/')
def home():
    html = """
    <html>
    <head>
    <title>just a page</title>
    <script src="https://apis.google.com/js/platform.js" async defer></script>
    <meta name="google-signin-client_id" content="769017929605-rpovnc5j01547ktb1er5fc0qqcd6fcer.apps.googleusercontent.com">
    </head>
    <body>
    <p>Hello, I'm in html</p>
    <div class="g-signin2" data-onsuccess="onSignIn"></div>
    </body>
    </html>
    """
    return html


@app.route('/about')
def about():
    return 'About Page Route'


@app.route('/portfolio')
def portfolio():
    return 'Portfolio Page Route'
