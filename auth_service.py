
import os
import time
import urllib.parse
import webbrowser
import requests

from pathlib import Path
from dotenv import load_dotenv

# Allow HTTP only for local OAuth development.
# Never enable this setting in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from google_auth_oauthlib.flow import InstalledAppFlow
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


# ==================================================
# FIREBASE CONFIGURATION
# ==================================================

load_dotenv(
    dotenv_path=Path(__file__).resolve().parent / ".env",
    override=True
)

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

FIREBASE_BASE = "https://identitytoolkit.googleapis.com/v1"

print("Firebase API Key Loaded:", bool(FIREBASE_API_KEY))

# ==================================================
# GOOGLE OAUTH CONFIGURATION
# ==================================================

GOOGLE_CLIENT_FILE = "google_oauth_client.json"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


class AuthError(Exception):
    """Custom authentication exception."""
    pass


# ==================================================
# FIREBASE AUTHENTICATION
# ==================================================

def _firebase_post(endpoint, payload):

    if not FIREBASE_API_KEY:
        raise AuthError("Firebase API Key is missing.")

    url = f"{FIREBASE_BASE}/{endpoint}?key={FIREBASE_API_KEY}"

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=25
        )

    except requests.RequestException as exc:
        raise AuthError(
            f"Network connection failed: {exc}"
        ) from exc

    try:
        data = response.json() if response.content else {}

    except ValueError:
        raise AuthError(
            "Invalid response received from Firebase."
        )

    if not response.ok:

        message = data.get(
            "error", {}
        ).get(
            "message", "Authentication failed."
        )

        friendly_errors = {
            "EMAIL_EXISTS":
                "This email is already registered. Please log in.",

            "INVALID_EMAIL":
                "Please enter a valid email address.",

            "WEAK_PASSWORD":
                "Password must contain at least 6 characters.",

            "EMAIL_NOT_FOUND":
                "Account not found. Please sign up first.",

            "INVALID_PASSWORD":
                "Incorrect password.",

            "INVALID_LOGIN_CREDENTIALS":
                "Incorrect email or password.",

            "OPERATION_NOT_ALLOWED":
                "Enable Email/Password authentication in Firebase Console.",

            "USER_DISABLED":
                "This account has been disabled.",

            "TOO_MANY_ATTEMPTS_TRY_LATER":
                "Too many attempts. Please try again later.",

            "API_KEY_INVALID":
                "Invalid Firebase API Key.",
        }

        raise AuthError(
            friendly_errors.get(message, message)
        )

    return data


# ==================================================
# EMAIL SIGNUP
# ==================================================

def signup_email(email, password):

    email = email.strip()

    if not email or not password:
        raise AuthError(
            "Email and password are required."
        )

    if len(password) < 6:
        raise AuthError(
            "Password must contain at least 6 characters."
        )

    return _firebase_post(
        "accounts:signUp",
        {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }
    )


# ==================================================
# EMAIL LOGIN
# ==================================================

def login_email(email, password):

    email = email.strip()

    if not email or not password:
        raise AuthError(
            "Email and password are required."
        )

    return _firebase_post(
        "accounts:signInWithPassword",
        {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }
    )


# ==================================================
# GOOGLE AUTHENTICATION
# ==================================================

def login_google():

    if not os.path.exists(GOOGLE_CLIENT_FILE):
        raise AuthError(
            "Google OAuth client configuration file was not found."
        )

    server = None

    try:

        # Create Google OAuth flow.
        flow = InstalledAppFlow.from_client_secrets_file(
            GOOGLE_CLIENT_FILE,
            scopes=SCOPES
        )

        # Custom OAuth callback handler.
        class OAuthCallbackHandler(BaseHTTPRequestHandler):

            def do_GET(self):

                query = parse_qs(
                    urlparse(self.path).query
                )

                # Ignore browser favicon and unrelated requests.
                if "code" not in query and "error" not in query:
                    self.send_response(204)
                    self.end_headers()
                    return

                # Save the actual Google callback URL.
                self.server.authorization_response = (
                    f"http://127.0.0.1:"
                    f"{self.server.server_port}{self.path}"
                )

                if "error" in query:

                    heading = "Google Sign-In Failed"

                    message = (
                        "Authentication was cancelled or denied."
                    )

                else:

                    heading = "Google Sign-In Successful"

                    message = (
                        "Opening GestureFlow. You can close this tab "
                        "if it remains open."
                    )

                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>GestureFlow</title>
                    <meta charset="UTF-8">
                    <meta name="viewport"
                          content="width=device-width, initial-scale=1.0">
                </head>

                <body style="
                    background:#111827;
                    color:#F4F7FA;
                    font-family:Arial,sans-serif;
                    text-align:center;
                    padding-top:80px;
                ">

                    <h1 style="color:#35BFA0;">
                        GestureFlow
                    </h1>

                    <h2>{heading}</h2>

                    <p>{message}</p>

                    <script>
                        window.onload = function() {{
                            window.open('', '_self');
                            window.close();
                        }};
                    </script>

                </body>
                </html>
                """

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    "text/html; charset=utf-8"
                )

                self.send_header(
                    "Cache-Control",
                    "no-store"
                )

                self.end_headers()

                self.wfile.write(
                    html.encode("utf-8")
                )

            def log_message(self, format, *args):
                pass

        # Start a temporary local callback server.
        server = HTTPServer(
            ("127.0.0.1", 0),
            OAuthCallbackHandler
        )

        server.timeout = 1

        redirect_uri = (
            f"http://127.0.0.1:{server.server_port}/"
        )

        flow.redirect_uri = redirect_uri

        # Generate the Google authorization URL.
        authorization_url, expected_state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="select_account"
        )

        # Open Google sign-in in the default browser.
        webbrowser.open(authorization_url)

        # Wait for the actual OAuth callback.
        # Ignore favicon and unrelated browser requests.
        deadline = time.monotonic() + 180

        while (
            not getattr(server, "authorization_response", None)
            and time.monotonic() < deadline
        ):
            server.handle_request()

        callback_url = getattr(
            server,
            "authorization_response",
            None
        )

        server.server_close()
        server = None

        if not callback_url:
            raise AuthError(
                "Google authentication timed out. Please try again."
            )

        callback_query = parse_qs(
            urlparse(callback_url).query
        )

        if "error" in callback_query:
            raise AuthError(
                "Google authentication was cancelled or denied."
            )

        # Verify OAuth state.
        returned_state = callback_query.get("state", [None])[0]

        if returned_state != expected_state:
            raise AuthError(
                "Google authentication state validation failed."
            )

        # Exchange authorization code for Google credentials.
        flow.fetch_token(
            authorization_response=callback_url
        )

        google_id_token = getattr(
            flow.credentials,
            "id_token",
            None
        )

        if not google_id_token:
            raise AuthError(
                "Google ID token was not received. "
                "Please check your OAuth configuration."
            )

        # Exchange Google's ID token for Firebase credentials.
        post_body = urllib.parse.urlencode(
            {
                "id_token": google_id_token,
                "providerId": "google.com",
            }
        )

        firebase_user = _firebase_post(
            "accounts:signInWithIdp",
            {
                "postBody": post_body,
                "requestUri": "http://localhost",
                "returnSecureToken": True,
                "returnIdpCredential": True,
            }
        )

        return firebase_user

    except AuthError:
        raise

    except Exception as exc:
        raise AuthError(
            f"Google sign-in failed: {exc}"
        ) from exc

    finally:

        if server is not None:
            server.server_close()
