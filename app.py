from flask import Flask, render_template, request
import os
import requests
from dotenv import load_dotenv
from url_features import extract_features  # If used elsewhere, else remove
import logging
from datetime import datetime
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    filename='api_monitor.log',
    format='%(asctime)s,%(levelname)s,%(message)s'
)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Flask app
app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    REMEMBER_COOKIE_SECURE=True,
    REMEMBER_COOKIE_HTTPONLY=True,
    SECRET_KEY=os.environ.get('SECRET_KEY')
)

# --- Utility Functions ---

def sanitize_url(url):
    """Sanitize URL for logging (hide query params, etc.)"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def dummy_check(url):
    phishing_keywords = ['login', 'update', 'secure', 'verify', 'account', 'banking', 'paypal']
    return any(keyword in url.lower() for keyword in phishing_keywords)

def check_google_safebrowsing(url):
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"
    
    payload = {
        "client": {
            "clientId": "phishing-detector",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        status = response.status_code
        latency = response.elapsed.total_seconds()
        is_threat = bool(response.json().get("matches", []))

        logging.info(f"{datetime.now()},{sanitize_url(url)},{status},{latency},{'Phishing' if is_threat else 'Safe'}")
        return is_threat
    except Exception as e:
        logging.error(f"{datetime.now()},{sanitize_url(url)},ERROR,{e}")
        return f"API error: {e}"









# --- Routes ---
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    method_used = ""
    
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        method = request.form.get("method", "")

        if not url:
            result = "⚠️ Please enter a valid URL."
            method_used = "Input Validation"
        elif method == "dummy":
            result = "🚨 Phishing Detected!" if dummy_check(url) else "✅ Safe URL"
            method_used = "Dummy Keyword Matching"
        elif method == "google":
            verdict = check_google_safebrowsing(url)
            if verdict is True:
                result = "🚨 Google marked this site as unsafe!"
            elif verdict is False:
                result = "✅ Google says this site is safe."
            else:
                result = verdict  # API error message
            method_used = "Google Safe Browsing API"
        else:
            result = "❌ Unknown detection method selected."
            method_used = "Error"

    return render_template("index.html", result=result, method=method_used)




@app.route("/dashboard")
def home():
    return render_template("dashboard.html")




# --- Run App ---
if __name__ == "__main__":
    host = '127.0.0.1'
    port = 5000
    print(f" * Running on http://{host}:{port}/ (Press CTRL+C to quit)")
    app.run(host=host, port=port, debug=True)















