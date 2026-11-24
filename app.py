import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import date, timedelta
from schedule import occurrences_between, countdown

app = Flask(__name__)
DATABASE = "planner.db"

EVENT_TYPES = ["class", "shift", "deadline", "exam", "personal"]
DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite needs this to enforce links between tables
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT,
            colour TEXT NOT NULL DEFAULT '#3788d8'
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('class', 'shift', 'deadline', 'exam', 'personal')),
            course_id INTEGER REFERENCES courses(id),
            date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            repeat_days TEXT,
            repeat_until TEXT,
            done INTEGER NOT NULL DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    conn = get_db()
    courses = conn.execute("SELECT * FROM courses ORDER BY code").fetchall()
    events = conn.execute("""
        SELECT events.*, courses.code AS course_code
        FROM events
        LEFT JOIN courses ON events.course_id = courses.id
        ORDER BY date, start_time
    """).fetchall()
    conn.close()

    today = date.today()
    week_end = today + timedelta(days=6)

    # Everything happening in the next 7 days (recurring classes expanded)
    agenda = occurrences_between(events, today, week_end)

    # Unfinished deadlines and exams due within 7 days, including overdue ones
    due_soon = []
    for e in events:
        if e["type"] in ("deadline", "exam") and not e["done"]:
            due_date = date.fromisoformat(e["date"])
            if due_date <= week_end:
                item = dict(e)
                item["countdown"] = countdown(due_date, today)
                due_soon.append(item)

    return render_template(
        "index.html", courses=courses, events=events,
        agenda=agenda, due_soon=due_soon,
        event_types=EVENT_TYPES, days=DAYS,
    )


@app.route("/courses/add", methods=["POST"])
def add_course():
    conn = get_db()
    conn.execute(
        "INSERT INTO courses (code, name, colour) VALUES (?, ?, ?)",
        (request.form["code"], request.form.get("name") or None, request.form["colour"]),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/events/add", methods=["POST"])
def add_event():
    repeat_days = ",".join(request.form.getlist("repeat_days")) or None

    conn = get_db()
    conn.execute("""
        INSERT INTO events
            (title, type, course_id, date, start_time, end_time, repeat_days, repeat_until)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form["title"],
        request.form["type"],
        request.form.get("course_id") or None,
        request.form["date"],
        request.form.get("start_time") or None,
        request.form.get("end_time") or None,
        repeat_days,
        request.form.get("repeat_until") or None,
    ))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

@app.route("/events/<int:event_id>/toggle-done", methods=["POST"])
def toggle_done(event_id):
    conn = get_db()
    conn.execute("UPDATE events SET done = 1 - done WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))