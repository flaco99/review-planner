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
    <script>
function onSignIn(googleUser) {
  var profile = googleUser.getBasicProfile();
  var id_token = googleUser.getAuthResponse().id_token;
  window.location.replace("https://review-planner.vercel.app/dumdum/" + id_token);
  console.log('ID token: ' + id_token);
  console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
  console.log('Name: ' + profile.getName());
  console.log('Image URL: ' + profile.getImageUrl());
  console.log('Email: ' + profile.getEmail()); // This is null if the 'email' scope is not present.
}    
    </script>
    </head>
    <body>
    <p>Hello, I'm in html</p>
    <div class="g-signin2" data-onsuccess="onSignIn"></div>
    </body>
    </html>
    """
    return html


@app.route('/dumdum/<tokenid>')
def about(tokenid):
    return f"dumdum {tokenid}"


@app.route('/portfolio')
def portfolio():
    return 'Portfolio Page Route'
