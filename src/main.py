import sqlite3
from flask import Flask, request, jsonify, g

DATABASE = "db/friend.db"

app = Flask(__name__)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db
    
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
        
def init_db():
    with app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS friend (
                id_friend INTEGER PRIMARY KEY AUTOINCREMENT,
                name_friend TEXT NOT NULL,
                family_name_friend TEXT NOT NULL,
                info_friend TEXT NOT NULL
            )
            """
        )
        db.commit()


def row_to_dict(row):
    return {"id_friend": row["id_friend"], "name_friend": row["name_friend"], "family_name_friend": row["family_name_friend"], "info_friend": row["info_friend"]}
    

@app.route("/friend", methods=["GET"])
def list_items():
    db = get_db()
    rows = db.execute("SELECT * FROM friend").fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@app.route("/friend/<int:id_friend>", methods=["GET"])
def get_item(id_friend):
    db = get_db()
    row = db.execute("SELECT * FROM friend WHERE id_friend = ?", (id_friend,)).fetchone()
    if row is None:
        return jsonify({"error": "Friend not found"}), 404
    return jsonify(row_to_dict(row))


@app.route("/friend", methods=["POST"])
def create_item():
    data = request.get_json(silent=True) or {}
    name = data.get("name_friend")
    family_name = data.get("family_name_friend")
    info = data.get("info_friend", "")

    if not name:
        return jsonify({"error": "'name_friend' is required"}), 400
        
    if not family_name:
        return jsonify({"error": "'family_name_friend' is required"}), 400
    
    if not info:
        return jsonify({"error": "'info_friend' is required"}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO friend (name_friend, family_name_friend, info_friend) VALUES (?, ?, ?)", (name, family_name, info)
    )
    db.commit()

    new_item = db.execute(
        "SELECT * FROM friend WHERE id_friend = ?", (cursor.lastrowid,)
    ).fetchone()
    return jsonify(row_to_dict(new_item)), 201


@app.route("/friend/<int:id_friend>", methods=["PUT"])
def update_item(id_friend):
    data = request.get_json(silent=True) or {}
    db = get_db()

    existing = db.execute("SELECT * FROM friend WHERE id_friend = ?", (id_friend,)).fetchone()
    if existing is None:
        return jsonify({"error": "Friend not found"}), 404

    name = data.get("name_friend", existing["name_friend"])
    family_name = data.get("family_name_friend", existing["family_name_friend"])
    info = data.get("info_friend", existing["info_friend"])

    db.execute(
        "UPDATE friend SET name_friend = ?, family_name_friend = ?, info_friend = ? WHERE id_friend = ?",
        (name, family_name, info, id_friend),
    )
    db.commit()

    updated = db.execute("SELECT * FROM friend WHERE id_friend = ?", (id_friend,)).fetchone()
    return jsonify(row_to_dict(updated))


@app.route("/friend/<int:id_friend>", methods=["DELETE"])
def delete_item(id_friend):
    db = get_db()
    existing = db.execute("SELECT * FROM friend WHERE id_friend = ?", (id_friend,)).fetchone()
    if existing is None:
        return jsonify({"error": "Friend not found"}), 404

    db.execute("DELETE FROM friend WHERE id_friend = ?", (id_friend,))
    db.commit()
    return jsonify({"result": "deleted", "id_friend": id_friend})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)