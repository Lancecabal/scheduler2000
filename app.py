from flask import Flask, render_template

app = Flask(__name__)

shifts = [
    {"date": "2026-11-28", "start": "09:00", "end": "17:00"},
    {"date": "2026-11-30", "start": "16:00", "end": "22:00"},
]

@app.route("/")
def home():
    return render_template("index.html", shifts=shifts)