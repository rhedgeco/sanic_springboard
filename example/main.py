from sanic import Sanic
from springboard import Springboard
from utilities.oauth.google_oauth import GoogleOauthHandler

app = Springboard(Sanic('example_app'))

oauth = GoogleOauthHandler(
    '452338962726-tne0iin890sjlg5ctni1ooer5b6ebl5g.apps.googleusercontent.com'
)
oauth.connect_springboard(app)

if __name__ == '__main__':
    app.localhost()
