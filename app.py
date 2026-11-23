from flask import Flask, render_template, request, redirect

app = Flask(__name__)

shifts = [
    {"date": "2026-11-28", "start": "09:00", "end": "17:00"},
    {"date": "2026-11-30", "start": "16:00", "end": "22:00"},
]

@app.route("/")
def home():
    return render_template("index.html", shifts=shifts)

@app.route("/add", methods=["POST"])
def add_shift():
    new_shift = {
        "date": request.form["date"],
        "start": request.form["start"],
        "end": request.form["end"],
    }
    shifts.append(new_shift)
    return redirect("/")

@app.route("/calendar")
def calendar():
    return render_template("calendar.html")