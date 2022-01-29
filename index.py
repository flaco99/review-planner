from flask import Flask


app = Flask(__name__)


@app.route('/')
def home():
    return "<html><head><title>just a page</title></head><body>Hello, I'm in html</body></html>"


@app.route('/about')
def about():
    return 'About Page Route'


@app.route('/portfolio')
def portfolio():
    return 'Portfolio Page Route'
