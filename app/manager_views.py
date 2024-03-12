from app import app

@app.route("/manager/dashboard")
def admin_dashboard():
    return "Manager Dashboard"

@app.route("/manager/profile")
def admin_profile():
    return "Manager Profile"