from app import app

@app.route("/instructor/dashboard")
def staff_dashboard():
    return "instructor Dashboard"

@app.route("/instructor/profile")
def staff_profile():
    return "instructor Profile"