import os
import sqlite3
from flask import Flask, g, render_template, request, jsonify, make_response

app = Flask(__name__)
app.config["DATABASE"] = os.environ.get("DATABASE", "credit.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            term INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'в ожидании',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    db.commit()


@app.before_request
def _ensure_db():
    init_db()


def _set_cookie(response, app_id):
    response.set_cookie("current_app_id", str(app_id))
    return response


def _get_cookie_app_id():
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.is_json or request.method == "POST":
        data = request.get_json() or request.form
        db = get_db()
        cur = db.execute(
            "INSERT INTO applications (name, amount, term) VALUES (?, ?, ?)",
            (data["name"], float(data["amount"]), int(data["term"])),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM applications WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        response = make_response(jsonify(dict(row)), 201)
        response.set_cookie("current_app_id", str(cur.lastrowid))
        return response
    return render_template("apply.html")


@app.route("/applications")
def applications():
    return render_template("applications.html")


@app.route("/api/applications", methods=["GET"])
def api_applications():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM applications ORDER BY id DESC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/applications/<int:app_id>/status", methods=["PATCH"])
def api_update_status(app_id):
    new_status = request.get_json()["status"]
    db = get_db()
    db.execute(
        "UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id)
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM applications WHERE id = ?", (app_id,)
    ).fetchone()
    resp = make_response(jsonify(dict(row)))
    if new_status in ("одобрено", "отклонено"):
        resp.set_cookie("current_app_id", "", expires=0)
    return resp


if __name__ == "__main__":
    app.run(debug=True)
