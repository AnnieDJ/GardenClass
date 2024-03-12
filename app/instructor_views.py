from app import app

@app.route("/instructor/dashboard")
def instructor_dashboard():
    return "instructor Dashboard"

@app.route("/instructor/profile")
def instructor_profile():
    return "instructor Profile"