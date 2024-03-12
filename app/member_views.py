from app import app

@app.route("/member/dashboard")
def member_dashboard():
    return "Member Dashboard"

@app.route("/member/profile")
def member_profile():
    return "Member Profile"