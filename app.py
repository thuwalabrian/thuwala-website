from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from functools import wraps
from sqlalchemy import inspect  # Add this import

app = Flask(__name__)
app.config.from_object("config.Config")

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "admin_login"


# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    details = db.Column(db.Text)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Initialize database on app startup
with app.app_context():
    try:
        print("=" * 50)
        print("Initializing database...")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

        # Create tables
        db.create_all()
        print("Database tables created")

        # Create admin user if not exists
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                email="admin@thuwalaco.com",
                password_hash=generate_password_hash("Admin@2024"),
            )
            db.session.add(admin)
            print("Admin user created")

        # Add sample services if none exist
        if not Service.query.first():
            services = [
                Service(
                    title="Administrative & Executive Support",
                    description="Virtual assistant services, document formatting, calendar management",
                    icon="fas fa-briefcase",
                    details="Report writing, document formatting, minute-taking, calendar management, task management, filing systems, policy support",
                ),
                Service(
                    title="Project & Operations Support",
                    description="Proposal writing, budget tracking, donor reporting",
                    icon="fas fa-project-diagram",
                    details="Proposal and report writing, budget tracking, M&E data management, donor reporting, stakeholder coordination",
                ),
                Service(
                    title="Data Management & Analytics",
                    description="Data cleaning, analysis, dashboard design, visualization",
                    icon="fas fa-chart-bar",
                    details="Data collection, data entry, cleaning, analysis, dashboard design, visualization, executive summaries",
                ),
                Service(
                    title="Communications & Documentation",
                    description="Corporate profiles, proposal writing, report editing",
                    icon="fas fa-comments",
                    details="Corporate profiles, capability statements, proposal writing, report editing, success stories, press releases",
                ),
            ]

            for service in services:
                db.session.add(service)
            print("Sample services added")

        db.session.commit()
        print("✅ Database initialization complete!")
        print("=" * 50)
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        print("Will retry on first request...")


# Inject current year into all templates
@app.context_processor
def inject_now():
    return {"now": datetime.now()}


# Routes with error handling for database issues
@app.route("/")
def index():
    try:
        services = Service.query.limit(4).all()
    except Exception as e:
        print(f"Database error in index route: {e}")
        # Fallback to empty list if database isn't ready
        services = []
    return render_template("index.html", services=services)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    try:
        services = Service.query.all()
    except Exception as e:
        print(f"Database error in services route: {e}")
        services = []
    return render_template("services.html", services=services)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        try:
            name = request.form.get("name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            subject = request.form.get("subject")
            message = request.form.get("message")

            new_message = ContactMessage(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
            )

            db.session.add(new_message)
            db.session.commit()

            flash(
                "Thank you for your message! We will contact you soon.",
                "success",
            )
            return redirect(url_for("contact"))
        except Exception as e:
            flash("An error occurred. Please try again.", "error")
            print(f"Contact form error: {e}")

    return render_template("contact.html")


# Admin Routes
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("admin_dashboard"))

        flash("Invalid credentials", "error")

    return render_template("admin/login.html")


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    try:
        messages = ContactMessage.query.order_by(
            ContactMessage.created_at.desc()
        ).all()
        unread_count = ContactMessage.query.filter_by(is_read=False).count()
    except Exception as e:
        print(f"Database error in admin dashboard: {e}")
        messages = []
        unread_count = 0

    return render_template(
        "admin/dashboard.html", messages=messages, unread_count=unread_count
    )


@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/admin/message/<int:message_id>/read")
@login_required
def mark_message_read(message_id):
    try:
        message = ContactMessage.query.get_or_404(message_id)
        message.is_read = True
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Add a debug route to check database status
@app.route("/debug/db-status")
def debug_db_status():
    try:
        # SQLAlchemy 2.0 compatible way to get table names
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        service_count = Service.query.count() if "service" in tables else 0
        user_count = User.query.count() if "user" in tables else 0
        message_count = (
            ContactMessage.query.count() if "contact_message" in tables else 0
        )

        return {
            "database": str(app.config["SQLALCHEMY_DATABASE_URI"]),
            "tables": tables,
            "service_count": service_count,
            "user_count": user_count,
            "message_count": message_count,
            "status": "OK",
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


# Simple health check route
@app.route("/health")
def health_check():
    return {"status": "healthy", "service": "thuwala-co"}


if __name__ == "__main__":
    # Create necessary folders
    os.makedirs("static/uploads", exist_ok=True)
    os.makedirs("templates/admin", exist_ok=True)

    # Get port from environment
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
