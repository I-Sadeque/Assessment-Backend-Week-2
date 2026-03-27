"""An API for handling marine experiments."""

from datetime import datetime

from flask import Flask, jsonify, request
from psycopg2 import sql

from database_functions import get_db_connection


app = Flask(__name__)

"""
For testing reasons; please ALWAYS use this connection. 

- Do not make another connection in your code
- Do not close this connection

If you do not understand this instructions; as a coach to explain
"""
conn = get_db_connection("marine_experiments")


@app.get("/")
def home():
    """Returns an informational message."""
    return jsonify({
        "designation": "Project Armada",
        "resource": "JSON-based API",
        "status": "Classified"
    })


def apply_type_filter(exp_type, where_clauses, params):
    """Validates type and updates query parameters. Returns an error tuple if invalid."""
    if exp_type is not None:
        exp_type = exp_type.lower()
        if exp_type not in ["intelligence", "obedience", "aggression"]:
            return jsonify({"error": "Invalid value for 'type' parameter"}), 400
        where_clauses.append("et.type_name = %s")
        params.append(exp_type)
    return None


def apply_score_filter(score_over, where_clauses, params):
    """Validates score and updates query parameters. Returns an error tuple if invalid."""
    if score_over is not None:
        try:
            score_over_val = int(score_over)
            if not (0 <= score_over_val <= 100):
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid value for 'score_over' parameter"}), 400

        where_clauses.append("((e.score / et.max_score) * 100) > %s")
        params.append(score_over_val)
    return None


@app.get("/experiment")
def get_experiments():
    """Returns a list of experiments, optionally filtered by type and score."""
    exp_type = request.args.get("type")
    score_over = request.args.get("score_over")

    where_clauses = []
    params = []

    type_error = apply_type_filter(exp_type, where_clauses, params)
    if type_error:
        return type_error

    score_error = apply_score_filter(score_over, where_clauses, params)
    if score_error:
        return score_error

    query = """
        SELECT 
            e.experiment_id,
            e.subject_id,
            sp.species_name AS species,
            TO_CHAR(e.experiment_date, 'YYYY-MM-DD') AS experiment_date,
            et.type_name AS experiment_type,
            TO_CHAR((e.score / et.max_score) * 100, 'FM990.00') AS score
        FROM experiment e
        JOIN subject sub ON e.subject_id = sub.subject_id
        JOIN species sp ON sub.species_id = sp.species_id
        JOIN experiment_type et ON e.experiment_type_id = et.experiment_type_id
    """

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += " ORDER BY e.experiment_date DESC;"

    with conn.cursor() as cur:
        cur.execute(query, params)
        experiments = cur.fetchall()

    return jsonify(experiments), 200


if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    app.run(port=8000, debug=True)

    conn.close()
