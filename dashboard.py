from flask import Flask, render_template
import os

app = Flask(__name__)



@app.route("/dashboard")
def dashboard():
    logs = []

    log_file = "api_monitor.log"

    if not os.path.exists(log_file):
        logs.append({
            "time": "-", "level": "ERROR", "url": "-", "status": "-", "result": "Log file not found."
        })
        return render_template("dashboard.html", logs=logs)

    with open(log_file, "r") as f:
        for line in f:
            parts = line.strip().split(",", 4)  # Limit to 5 parts max
            if len(parts) >= 5:
                time, level, url, status, result = parts
            elif len(parts) == 4:
                time, level, url, status = parts
                result = "-"
            else:
                continue  # Skip malformed lines

            logs.append({
                "time": time,
                "level": level,
                "url": url,
                "status": status,
                "result": result
            })

    logs.reverse()  # Show latest first
    return render_template("dashboard.html", logs=logs[:100])  # Max 100 entries

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 5000  # or whatever port you're using
    url = f"http://{host}:{port}/dashboard"
    print(f" * Running on {url} (Press CTRL+C to quit)")
    app.run(host=host, port=port, debug=True)
