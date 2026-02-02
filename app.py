import pickle
import sys
import os
from flask import Flask, render_template, request, jsonify
from database import init_db, insert_complaint, get_all_complaints

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

        # ---- AI predictions ----
      
        priority = priority_model.predict([complaint_text])[0]

        base_hours = float(resolution_model.predict([complaint_text])[0])

        # ---- Priority-based adjustment (FIXED) ----
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

        return jsonify({
            "success": True,
            "complaint": {
                "id": complaint_id,
                "category": category,
                "priority": priority,
                "estimated_resolution_hours": estimated_hours
            }
        })

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
            "category": r[4],                 # ✅ SAME FIELD NAME
            
            "complaint_text": r[5],
            "priority": r[6],
            "estimated_resolution_hours": r[7],
            "status": r[8],
            "submitted_at": r[9]
        })

    return jsonify(data)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)