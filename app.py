import pickle
import sys
import os
from flask import Flask, render_template, request, jsonify
from database import (
    init_db,
    insert_complaint,
    get_all_complaints,
    update_complaint_status
)

# ---------------- PATH FIX ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ---------------- APP ----------------
app = Flask(__name__)
app.secret_key = "dev-secret-key"

# ---------------- LOAD MODELS ----------------
priority_model = pickle.load(open(resource_path("priority_model.pkl"), "rb"))
resolution_model = pickle.load(open(resource_path("resolution_model.pkl"), "rb"))

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

# ---------------- SUBMIT COMPLAINT ----------------
@app.route("/api/submit_complaint", methods=["POST"])
def submit_complaint():
    try:
        data = request.get_json()

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        phone = data.get("phone", "").strip()
        category = data.get("category", "").strip()
        complaint_text = data.get("complaint", "").strip()

        if not name or not complaint_text:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        priority = priority_model.predict([complaint_text])[0]
        base_hours = float(resolution_model.predict([complaint_text])[0])

        if priority == "High":
            estimated_hours = base_hours + 6
        elif priority == "Medium":
            estimated_hours = base_hours + 2
        else:
            estimated_hours = max(2, base_hours - 3)

        estimated_hours = round(estimated_hours, 1)

        complaint_id = insert_complaint(
            name,
            email,
            phone,
            category,
            complaint_text,
            priority,
            estimated_hours,
            "Submitted"
        )

        return jsonify({"success": True, "id": complaint_id})

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"success": False, "error": "Server error"}), 500

# ---------------- GET COMPLAINTS ----------------
@app.route("/api/complaints")
def api_complaints():
    rows = get_all_complaints()
    data = []

    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1],
            "email": r[2],
            "phone": r[3],
            "category": r[4],
            "complaint_text": r[5],
            "priority": r[6],
            "estimated_resolution_hours": r[7],
            "status": r[8],
            "submitted_at": r[9]
        })

    return jsonify(data)

# ---------------- UPDATE STATUS (NEW) ----------------
@app.route("/api/update_status/<int:complaint_id>", methods=["POST"])
def update_status(complaint_id):
    try:
        data = request.get_json()
        new_status = data.get("status")

        if new_status not in ["Open", "In Progress", "Resolved"]:
            return jsonify({"error": "Invalid status"}), 400

        update_complaint_status(complaint_id, new_status)

        return jsonify({"success": True})

    except Exception as e:
        print("❌ STATUS UPDATE ERROR:", e)
        return jsonify({"error": "Server error"}), 500
# ---------------- STATS ----------------
@app.route("/api/stats")
def api_stats():
    rows = get_all_complaints()

    total = len(rows)
    open_count = 0
    in_progress = 0
    resolved = 0

    for r in rows:
        status = r[8]

        if status in ("Submitted", "Open"):
            open_count += 1
        elif status == "In Progress":
            in_progress += 1
        elif status == "Resolved":
            resolved += 1

    return jsonify({
        "total": total,
        "open": open_count,
        "in_progress": in_progress,
        "resolved": resolved
    })

# ---------------- MAIN ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
