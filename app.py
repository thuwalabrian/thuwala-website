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
from sqlalchemy import inspect

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
    category = db.Column(db.String(100))  # Added category field


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def init_or_migrate_database():
    """Initialize or migrate database schema"""
    try:
        # Check if 'category' column exists in Service table
        inspector = inspect(db.engine)
        columns = [col["name"] for col in inspector.get_columns("service")]

        if "category" not in columns:
            print("⚠️ 'category' column missing. Adding it now...")
            try:
                # Try to add column (SQLite syntax)
                db.session.execute(
                    "ALTER TABLE service ADD COLUMN category VARCHAR(100)"
                )
                db.session.commit()
                print("✅ Added 'category' column to service table")
            except Exception as e:
                print(f"⚠️ Could not add column automatically: {e}")
                print("Trying PostgreSQL syntax...")
                try:
                    # PostgreSQL syntax
                    db.session.execute(
                        "ALTER TABLE service ADD COLUMN category VARCHAR(100)"
                    )
                    db.session.commit()
                    print(
                        "✅ Added 'category' column to service table (PostgreSQL)"
                    )
                except Exception as e2:
                    print(f"⚠️ PostgreSQL syntax also failed: {e2}")
                    print(
                        "Please update your database manually or delete the database file to recreate."
                    )
                    return False

        return True
    except Exception as e:
        print(f"⚠️ Database inspection error: {e}")
        return False


# Initialize database on app startup
with app.app_context():
    try:
        print("=" * 50)
        print("Initializing database...")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

        # Check and migrate database
        if not init_or_migrate_database():
            print("⚠️ Database migration check failed")

        # Create tables (this won't affect existing tables)
        db.create_all()
        print("Database tables checked/created")

        # Create admin user if not exists
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                email="admin@thuwalaco.com",
                password_hash=generate_password_hash("Admin@2024"),
            )
            db.session.add(admin)
            print("Admin user created")

        # Update existing services with categories if they don't have them
        services_without_category = Service.query.filter(
            (Service.category == None) | (Service.category == "")
        ).all()

        if services_without_category:
            print(
                f"Found {len(services_without_category)} services without categories"
            )
            # Define category mapping based on title
            category_mapping = {
                "administrative": "administrative",
                "executive": "administrative",
                "project": "operations",
                "operations": "operations",
                "data": "data",
                "analytics": "data",
                "communications": "communications",
                "documentation": "communications",
                "branding": "branding",
                "design": "branding",
                "marketing": "branding",
                "business": "business",
                "startup": "business",
                "systems": "systems",
                "process": "systems",
                "capacity": "training",
                "training": "training",
                "creative": "creative",
                "individual": "creative",
                "consulting": "consulting",
                "strategy": "consulting",
            }

            for service in services_without_category:
                title_lower = service.title.lower()
                matched_category = None

                for keyword, category in category_mapping.items():
                    if keyword in title_lower:
                        matched_category = category
                        break

                # Default category if no match
                if not matched_category:
                    matched_category = "administrative"

                service.category = matched_category
                print(
                    f"  - Updated '{service.title}' with category: {matched_category}"
                )

            db.session.commit()
            print("Updated existing services with categories")

        # Define all services (10 total from portfolio)
        all_services_data = [
            {
                "title": "Administrative & Executive Support",
                "description": "We provide seamless virtual and on-site administrative solutions to keep organizations and individuals operating with order and professionalism.",
                "icon": "fas fa-clipboard-check",
                "details": "Virtual assistant and secretarial services, Report writing, document formatting, and minute-taking, Calendar, meeting, and task management, Filing systems and office workflow setup, Policy, SOP, and documentation support",
                "category": "administrative",
            },
            {
                "title": "Project & Operations Support",
                "description": "We help organizations plan, execute, and report on their projects with precision and transparency.",
                "icon": "fas fa-project-diagram",
                "details": "Proposal and report writing, Budget tracking and procurement documentation, M&E data management and templates, Donor reporting and presentation packaging, Stakeholder coordination and communication",
                "category": "operations",
            },
            {
                "title": "Data Management & Analytics",
                "description": "Data drives decision-making. We transform raw data into actionable insights for businesses and NGOs.",
                "icon": "fas fa-chart-bar",
                "details": "Data collection (ODK, Kobo, SurveyCTO), Data entry, cleaning, and analysis, Dashboard design and visualization (Excel, Tableau, Power BI), Executive summaries and reports, Monitoring and evaluation support",
                "category": "data",
            },
            {
                "title": "Communications & Documentation",
                "description": "We help you communicate your story, impact, and value clearly to your audience, partners, and clients.",
                "icon": "fas fa-bullhorn",
                "details": "Corporate profiles and capability statements, Proposal and grant writing, Report editing and formatting, Success stories, press releases, and newsletters, Professional presentations and pitch decks",
                "category": "communications",
            },
            {
                "title": "Branding, Design & Marketing",
                "description": "We build brands that command attention and credibility — from logo design to full-scale marketing campaigns.",
                "icon": "fas fa-palette",
                "details": "Logo and brand identity design, Company profiles and marketing materials, Social media setup, strategy, and content creation, Digital marketing campaigns and advertising management, Personal branding for professionals",
                "category": "branding",
            },
            {
                "title": "Business & Startup Support",
                "description": "For entrepreneurs and SMEs, we provide all the foundational tools needed to launch, formalize, and grow.",
                "icon": "fas fa-briefcase",
                "details": "Business registration guidance, Proposal and business plan writing, Company profile creation, Digital system setup (emails, websites, cloud storage), Business strategy and growth consultation",
                "category": "business",
            },
            {
                "title": "Systems & Process Optimization",
                "description": "We introduce digital systems that save time, reduce errors, and enhance organizational accountability.",
                "icon": "fas fa-cogs",
                "details": "Workflow automation setup, File and record management systems, Collaboration tools (Google Workspace, Notion, Trello), Process mapping and optimization consulting, Staff training on productivity tools",
                "category": "systems",
            },
            {
                "title": "Capacity Building & Training",
                "description": "We empower professionals and teams with practical, modern skills in administration, communication, and data management.",
                "icon": "fas fa-graduation-cap",
                "details": "Office administration and documentation, Proposal and report writing, Data collection and reporting tools, Excel and visualization training, Communication and digital professionalism",
                "category": "training",
            },
            {
                "title": "Creative & Individual Services",
                "description": "Thuwala Co. also supports individuals with personal and professional growth tools.",
                "icon": "fas fa-lightbulb",
                "details": "CV, cover letter, and portfolio design, Personal branding strategy, LinkedIn optimization, Digital profile setup and presentation design, Event and speech support documentation",
                "category": "creative",
            },
            {
                "title": "Consulting & Strategy",
                "description": "Strategic guidance for organizational development and business growth.",
                "icon": "fas fa-chess",
                "details": "Business strategy development, Organizational structure optimization, Process improvement consulting, Market analysis and research, Performance metrics and KPIs",
                "category": "consulting",
            },
        ]

        # Check and add missing services
        existing_titles = [s.title for s in Service.query.all()]
        added_count = 0

        for service_data in all_services_data:
            if service_data["title"] not in existing_titles:
                service = Service(**service_data)
                db.session.add(service)
                added_count += 1
                print(
                    f"  - Added service: {service_data['title']} ({service_data['category']})"
                )

        if added_count > 0:
            db.session.commit()
            print(f"Added {added_count} new services")
        else:
            print("All services already exist in database")

        # Verify we have all 10 services
        total_services = Service.query.count()
        print(f"Total services in database: {total_services}")

        if total_services < 10:
            print("⚠️ Warning: Database has less than 10 services")
            # List what we have
            services_list = Service.query.all()
            for s in services_list:
                print(f"  - {s.title} ({s.category})")

        print("✅ Database initialization complete!")
        print("=" * 50)

    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
        import traceback

        traceback.print_exc()
        print("Will retry on first request...")


# Inject current year into all templates
@app.context_processor
def inject_now():
    return {"now": datetime.now()}


# Routes with error handling for database issues
@app.route("/")
def index():
    try:
        services = Service.query.limit(6).all()  # Show 6 services on homepage
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
        services_list = Service.query.order_by(Service.id).all()
    except Exception as e:
        print(f"Database error in services route: {e}")
        services_list = []
    return render_template("services.html", services=services_list)


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

        # Get services with categories
        services = Service.query.all()
        services_info = [
            {"title": s.title, "category": s.category, "id": s.id}
            for s in services
        ]

        return {
            "database": str(app.config["SQLALCHEMY_DATABASE_URI"]),
            "tables": tables,
            "service_count": service_count,
            "user_count": user_count,
            "message_count": message_count,
            "services": services_info,
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
