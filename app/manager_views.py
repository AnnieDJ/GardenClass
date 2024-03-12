from app import app

@app.route("/manager/dashboard")
def manager_dashboard():
    return "Manager Dashboard"

@app.route("/manager/profile")
def manager_profile():
    return "Manager Profile"