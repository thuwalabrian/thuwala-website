from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
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
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from sqlalchemy import inspect, text
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_wtf.csrf import CSRFProtect
import traceback
import logging
from urllib.parse import quote

app = Flask(__name__)
app.config.from_object("config.Config")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 60 * 60 * 24 * 30  # 30 days


@app.after_request
def add_static_cache_headers(response):
    if request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=2592000"
    return response


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "admin_login"
csrf = CSRFProtect(app)

# Shared list of service categories used across routes and templates.
SERVICE_CATEGORIES = [
    "administrative",
    "operations",
    "data",
    "communications",
    "branding",
    "business",
    "systems",
    "training",
    "creative",
    "consulting",
]

# Default content for environments without a database (e.g., Vercel serverless).
DEFAULT_SERVICES = [
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

DEFAULT_PORTFOLIO = [
    {
        "title": "Malawi NGO Data Dashboard",
        "client": "Malawi Development NGO",
        "description": "Designed and implemented a comprehensive data dashboard for monitoring and evaluation. The system collects field data via ODK and presents real-time insights through interactive Power BI dashboards.",
        "category": "data",
        "image_url": "/static/images/portfolio/data-dashboard.jpg",
        "technologies": "Power BI, ODK, Python, SQL",
        "testimonial": "Thuwala Co. transformed our data management. What used to take weeks now takes hours. Their dashboard helps us make data-driven decisions.",
        "client_name": "John Banda",
        "client_role": "M&E Director",
        "featured": True,
    },
    {
        "title": "Startup Business Branding Package",
        "client": "AgriTech Startup",
        "description": "Complete branding package including logo design, business cards, company profile, and social media setup. Created a cohesive brand identity that helped secure initial funding.",
        "category": "branding",
        "image_url": "/static/images/portfolio/branding-package.jpg",
        "technologies": "Adobe Creative Suite, Canva, WordPress",
        "testimonial": "Professional, timely, and exceeded expectations. Our investors commented on how polished our materials looked.",
        "client_name": "Sarah Chibwana",
        "client_role": "CEO & Founder",
        "featured": True,
    },
    {
        "title": "Government Project Reporting System",
        "client": "Ministry Department",
        "description": "Streamlined project reporting system that reduced report preparation time by 60%. Created templates, automated data collection, and trained staff on new processes.",
        "category": "administrative",
        "image_url": "/static/images/portfolio/reporting-system.jpg",
        "technologies": "Microsoft Office, Google Workspace, Process Automation",
        "testimonial": "The efficiency gains have been remarkable. Our team now focuses on analysis rather than data compilation.",
        "client_name": "Dr. Michael Phiri",
        "client_role": "Project Director",
        "featured": True,
    },
    {
        "title": "Educational Institution Website Redesign",
        "client": "Private College",
        "description": "Complete website redesign with CMS integration, improving user engagement by 200%. Added online application system and student portal.",
        "category": "systems",
        "image_url": "/static/images/portfolio/website-redesign.jpg",
        "project_url": "https://example-college.mw",
        "technologies": "WordPress, PHP, JavaScript, CSS3",
        "testimonial": "Our online applications increased by 150% after the redesign. Professional and student-friendly.",
        "client_name": "Prof. Elizabeth Kachali",
        "client_role": "Principal",
        "featured": True,
    },
    {
        "title": "Corporate Training Program",
        "client": "Financial Institution",
        "description": "Designed and delivered Excel & Data Visualization training for 50+ staff members. Created custom training materials and follow-up support system.",
        "category": "training",
        "image_url": "/static/images/portfolio/training-program.jpg",
        "technologies": "Excel, Power BI, Training Materials",
        "testimonial": "The training was practical and immediately applicable. Staff confidence with data tools improved dramatically.",
        "client_name": "Robert Mwale",
        "client_role": "HR Director",
        "featured": False,
    },
    {
        "title": "Business Process Optimization",
        "client": "Manufacturing Company",
        "description": "Analyzed and optimized supply chain documentation processes, reducing processing time by 40% and errors by 75%.",
        "category": "operations",
        "image_url": "/static/images/portfolio/process-optimization.jpg",
        "technologies": "Process Mapping, SOP Development, Workflow Automation",
        "testimonial": "The new processes saved us significant time and reduced frustration across departments.",
        "client_name": "David Simbeye",
        "client_role": "Operations Manager",
        "featured": True,
    },
]

DEFAULT_ADS = [
    {
        "id": 1,
        "title": "Special Offer: 20% Off All Services",
        "description": "Launch your projects with our professional services at a discounted rate. Limited time offer!",
        "cta_text": "Claim Offer",
        "cta_link": "/contact",
        "image_url": None,
        "background_color": "#dc2626",
        "text_color": "#ffffff",
    },
    {
        "id": 2,
        "title": "New: Data Analytics Dashboard Solutions",
        "description": "Transform your raw data into actionable insights with our new dashboard solutions.",
        "cta_text": "Learn More",
        "cta_link": "/services",
        "image_url": None,
        "background_color": "#2563eb",
        "text_color": "#ffffff",
    },
]


def get_services_fallback():
    return [{**service, "id": idx + 1} for idx, service in enumerate(DEFAULT_SERVICES)]


def get_portfolio_fallback():
    return list(DEFAULT_PORTFOLIO)


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


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    client = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # e.g., 'branding', 'data', 'administrative'
    image_url = db.Column(db.String(500))
    project_url = db.Column(db.String(500))  # Link to live project if available
    completion_date = db.Column(db.Date)
    technologies = db.Column(db.String(500))  # Comma-separated tech/tools used
    testimonial = db.Column(db.Text)
    client_name = db.Column(db.String(200))
    client_role = db.Column(db.String(200))
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="reset_tokens")


class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cta_text = db.Column(db.String(100), default="Learn More")
    cta_link = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    background_color = db.Column(db.String(50), default="#2563eb")
    text_color = db.Column(db.String(50), default="#ffffff")
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# --- Lazy DB initialization (essential for Vercel / serverless) ----------
# On Vercel the `if __name__ == '__main__'` block never executes, so
# `init_db()` would never be called.  We use a `before_request` hook
# to create tables and seed data on the very first request of each
# cold-start.
_db_initialized = False


@app.before_request
def ensure_db_initialized():
    global _db_initialized
    if not _db_initialized:
        try:
            db.create_all()
            init_db()
        except Exception as e:
            app.logger.warning("Lazy DB init failed: %s", e)
        _db_initialized = True


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


def generate_reset_token():
    """Generate a secure reset token"""
    return secrets.token_urlsafe(32)


def get_file_extension(filename):
    """Extract lowercase file extension from a filename."""
    if not filename or "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


def is_allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    return get_file_extension(filename) in app.config["ALLOWED_EXTENSIONS"]


def has_uploaded_file(field_name):
    """Check if a real file was submitted in the given form field."""
    if field_name not in request.files:
        return False
    f = request.files[field_name]
    return f and f.filename and f.filename.strip() != ""


def save_uploaded_image(file, subdir, add_timestamp=True):
    """Save an uploaded image file and return its web-accessible URL.

    Returns a tuple (url, error_message).  On success error_message is None.
    On failure url is None and error_message explains the problem.
    """
    # Guard: no file or empty filename
    if not file or not file.filename or file.filename.strip() == "":
        return None, None  # nothing submitted — not an error

    original = file.filename.strip()
    ext = get_file_extension(original)

    if not ext:
        return None, "File has no extension. Please upload an image file."

    if ext not in app.config["ALLOWED_EXTENSIONS"]:
        allowed = ", ".join(sorted(app.config["ALLOWED_EXTENSIONS"]))
        return None, f"File type '.{ext}' is not supported. Allowed: {allowed}"

    # Build a safe filename, preserving the extension even if secure_filename strips it
    safe_name = secure_filename(original)
    if not safe_name or not get_file_extension(safe_name):
        # secure_filename stripped too much — rebuild from timestamp + extension
        safe_name = f"upload.{ext}"

    if add_timestamp:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{safe_name}"

    upload_dir = os.path.join(app.config["UPLOAD_FOLDER"], subdir)
    try:
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, safe_name)
        file.save(filepath)
        url = f"/static/uploads/{subdir}/{safe_name}"
        app.logger.info("Image saved: %s", url)
        return url, None
    except OSError as e:
        app.logger.error("File upload failed: %s", e, exc_info=True)
        return None, f"Server error saving file: {e}"


def send_password_reset_email(user_email, reset_url):
    """Send password reset email to user"""
    # If mail credentials are not configured, behave differently in dev vs production.
    missing_creds = not app.config.get("MAIL_USERNAME") or not app.config.get(
        "MAIL_PASSWORD"
    )

    if missing_creds:
        msg = f"Email credentials not configured. Would send reset link to {user_email}: {reset_url}"
        print(f"DEBUG: {msg}")
        # In debug/development keep the previous shortcut behavior to avoid blocking local dev.
        # In production fail loudly so an operator notices and fixes mail settings.
        is_dev = app.debug or os.environ.get("FLASK_ENV", "").lower() == "development"
        if is_dev:
            return True
        raise RuntimeError(
            "MAIL_USERNAME and MAIL_PASSWORD must be set in production to send emails"
        )

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Password Reset Request - Thuwala Co."
        msg["From"] = app.config["MAIL_DEFAULT_SENDER"]
        msg["To"] = user_email

        # HTML email content
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Password Reset - Thuwala Co.</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Thuwala Co.</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <h2>Hello,</h2>
                    <p>We received a request to reset your password for the Thuwala Co. admin account.</p>
                    <p>Click the button below to reset your password:</p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background: #f3f4f6; padding: 15px; border-radius: 5px; word-break: break-all;">
                        {reset_url}
                    </p>
                    <p>This link will expire in 24 hours.</p>
                    <p>If you didn't request a password reset, you can safely ignore this email.</p>
                    <div class="footer">
                        <p>Best regards,<br>The Thuwala Co. Team</p>
                        <p style="font-size: 12px; color: #9ca3af;">
                            This is an automated message. Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text version
        text = f"""
        Password Reset Request - Thuwala Co.
        
        Hello,
        
        We received a request to reset your password for the Thuwala Co. admin account.
        
        Click this link to reset your password: {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request a password reset, you can safely ignore this email.
        
        Best regards,
        The Thuwala Co. Team
        """

        # Attach both versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        msg.attach(part1)
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]) as server:
            if app.config.get("MAIL_USE_TLS", True):
                server.starttls()
            server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            server.send_message(msg)

        print(f"Password reset email sent to {user_email}")
        return True

    except Exception as e:
        app.logger.error("Error sending email: %s", e, exc_info=True)
        return False


# Add a custom template filter for darkening colors
@app.template_filter("darken_color")
def darken_color_filter(color, percent=20):
    """Darken a hex color by given percentage"""
    try:
        # Remove # if present
        color = color.lstrip("#")

        # Parse to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)

        # Darken
        r = max(0, min(255, int(r * (100 - percent) / 100)))
        g = max(0, min(255, int(g * (100 - percent) / 100)))
        b = max(0, min(255, int(b * (100 - percent) / 100)))

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return color


def build_whatsapp_url(
    name, email, phone, subject, message, service="", inquiry_type=""
):
    """Build a WhatsApp `wa.me` redirect URL with a pre-filled message.

    The user's browser will open WhatsApp (web or app) with the message
    ready to send, so the business owner receives it instantly.
    """
    wa_number = app.config.get("WHATSAPP_NUMBER", "265887873006")

    lines = [
        "📩 *New Inquiry from Thuwala Co. Website*",
        "",
        f"*Name:* {name}",
        f"*Email:* {email}",
    ]
    if phone:
        lines.append(f"*Phone:* {phone}")
    if service:
        lines.append(f"*Service Interest:* {service}")
    if inquiry_type:
        lines.append(f"*Inquiry Type:* {inquiry_type}")
    lines += [
        f"*Subject:* {subject}",
        "",
        f"*Message:*",
        message,
    ]

    text = "\n".join(lines)
    return f"https://wa.me/{wa_number}?text={quote(text)}"


def init_or_migrate_database():
    """Initialize or migrate database schema"""
    try:
        # Check if 'category' column exists in Service table
        inspector = inspect(db.engine)
        columns = [col["name"] for col in inspector.get_columns("service")]

        if "category" not in columns:
            app.logger.info(
                "'category' column missing from service table — adding it now…"
            )
            try:
                db.session.execute(
                    text("ALTER TABLE service ADD COLUMN category VARCHAR(100)")
                )
                db.session.commit()
                app.logger.info("Added 'category' column to service table")
            except Exception as e:
                db.session.rollback()
                app.logger.warning("Could not add 'category' column: %s", e)
                app.logger.warning(
                    "Please update your database manually or delete the database file to recreate."
                )
                return False

        return True
    except Exception as e:
        print(f"⚠️ Database inspection error: {e}")
        return False


def init_db():
    """Initialize or seed the database. Call inside an application context."""
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
            (Service.category.is_(None)) | (Service.category == "")
        ).all()

        if services_without_category:
            print(f"Found {len(services_without_category)} services without categories")
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
        all_services_data = DEFAULT_SERVICES

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

        # Add sample portfolio items if none exist
        if Portfolio.query.count() == 0:
            sample_portfolio = DEFAULT_PORTFOLIO

            for item in sample_portfolio:
                portfolio = Portfolio(**item)
                db.session.add(portfolio)

            db.session.commit()
            print(f"Added {len(sample_portfolio)} portfolio items")
        else:
            print(f"Portfolio already has {Portfolio.query.count()} items")

        # Add sample advertisements if none exist
        try:
            ad_count = Advertisement.query.count()
            print(f"ℹ️  Advertisement count: {ad_count}")

            if ad_count == 0:
                sample_ads = [
                    {
                        **ad,
                        "is_active": True,
                        "display_order": idx + 1,
                    }
                    for idx, ad in enumerate(DEFAULT_ADS)
                ]

                for ad_data in sample_ads:
                    ad = Advertisement(**ad_data)
                    db.session.add(ad)
                    print(f"  - Adding ad: {ad_data['title']}")

                db.session.commit()
                print(f"✅ Added {len(sample_ads)} sample advertisements")
            else:
                # List existing ads
                existing_ads = Advertisement.query.all()
                print(f"ℹ️  Database already has {ad_count} advertisements:")
                for ad in existing_ads:
                    print(
                        f"  - {ad.title} (Active: {ad.is_active}, Order: {ad.display_order})"
                    )
        except Exception as e:
            app.logger.warning("Error with advertisements: %s", e, exc_info=True)

        # Clean up expired tokens on startup
        expired_tokens = PasswordResetToken.query.filter(
            PasswordResetToken.expires_at < datetime.utcnow()
        ).all()

        for token in expired_tokens:
            db.session.delete(token)

        db.session.commit()

        print("✅ Database initialization complete!")
        print("=" * 50)

    except Exception as e:
        app.logger.error("Database initialization error: %s", e, exc_info=True)
        app.logger.info("Will retry on first request...")


# Inject current year into all templates
@app.context_processor
def inject_now():
    return {"now": datetime.now()}


# Routes with error handling for database issues
@app.route("/")
def index():
    try:
        services = Service.query.limit(6).all()  # Show 6 services on homepage
        if not services:
            services = get_services_fallback()[:6]

        # Get active advertisements
        ads = []
        try:
            ads_query = (
                Advertisement.query.filter_by(is_active=True)
                .order_by(
                    Advertisement.display_order,
                    Advertisement.created_at.desc(),
                )
                .limit(5)
                .all()
            )  # Limit to 5 ads max
            # Convert to dictionaries for JSON serialization
            ads = [
                {
                    "id": ad.id,
                    "title": ad.title,
                    "description": ad.description,
                    "cta_text": ad.cta_text,
                    "cta_link": ad.cta_link,
                    "image_url": ad.image_url,
                    "background_color": ad.background_color,
                    "text_color": ad.text_color,
                }
                for ad in ads_query
            ]
            if not ads:
                ads = DEFAULT_ADS
            print(f"DEBUG: Found {len(ads)} active advertisements for homepage")
        except Exception as e:
            print(f"DEBUG: Error fetching ads: {e}")
            ads = DEFAULT_ADS

        # Query a few portfolio items for homepage preview
        try:
            portfolio_items = (
                Portfolio.query.order_by(
                    Portfolio.featured.desc(), Portfolio.created_at.desc()
                )
                .limit(6)
                .all()
            )
            if not portfolio_items:
                portfolio_items = get_portfolio_fallback()[:6]
            # Extract testimonials from portfolio items
            if portfolio_items and isinstance(portfolio_items[0], dict):
                testimonials = [
                    {
                        "testimonial": p.get("testimonial"),
                        "client_name": p.get("client_name"),
                        "client_role": p.get("client_role"),
                    }
                    for p in portfolio_items
                    if p.get("testimonial")
                ]
            else:
                testimonials = [
                    {
                        "testimonial": p.testimonial,
                        "client_name": p.client_name,
                        "client_role": p.client_role,
                    }
                    for p in portfolio_items
                    if p.testimonial
                ]
        except Exception as e:
            print(f"DEBUG: Error fetching portfolio items: {e}")
            portfolio_items = get_portfolio_fallback()[:6]
            testimonials = [
                {
                    "testimonial": p.get("testimonial"),
                    "client_name": p.get("client_name"),
                    "client_role": p.get("client_role"),
                }
                for p in portfolio_items
                if p.get("testimonial")
            ]

    except Exception as e:
        print(f"Database error in index route: {e}")
        services = get_services_fallback()[:6]
        ads = DEFAULT_ADS
        portfolio_items = get_portfolio_fallback()[:6]
        testimonials = [
            {
                "testimonial": p.get("testimonial"),
                "client_name": p.get("client_name"),
                "client_role": p.get("client_role"),
            }
            for p in portfolio_items
            if p.get("testimonial")
        ]

    return render_template(
        "index.html",
        services=services,
        advertisements=ads,
        portfolio_items=portfolio_items,
        testimonials=testimonials,
        now=datetime.utcnow(),
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    try:
        services_list = Service.query.order_by(Service.id).all()
        if not services_list:
            services_list = get_services_fallback()
    except Exception as e:
        print(f"Database error in services route: {e}")
        services_list = get_services_fallback()
    return render_template("services.html", services=services_list)


@app.route("/portfolio")
def portfolio():
    # Get filter category from query parameter
    category_filter = request.args.get("category", "all")
    try:

        # Query portfolio items
        if category_filter == "all":
            portfolio_items = Portfolio.query.order_by(
                Portfolio.featured.desc(), Portfolio.created_at.desc()
            ).all()
        else:
            portfolio_items = (
                Portfolio.query.filter_by(category=category_filter)
                .order_by(Portfolio.featured.desc(), Portfolio.created_at.desc())
                .all()
            )
        if not portfolio_items:
            fallback_items = get_portfolio_fallback()
            if category_filter == "all":
                portfolio_items = fallback_items
            else:
                portfolio_items = [
                    item
                    for item in fallback_items
                    if item.get("category") == category_filter
                ]

        # Get unique categories for filter
        categories = db.session.query(Portfolio.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        if not categories:
            categories = sorted(
                {item.get("category") for item in get_portfolio_fallback()}
            )

    except Exception as e:
        print(f"Database error in portfolio route: {e}")
        fallback_items = get_portfolio_fallback()
        if category_filter == "all":
            portfolio_items = fallback_items
        else:
            portfolio_items = [
                item
                for item in fallback_items
                if item.get("category") == category_filter
            ]
        categories = sorted({item.get("category") for item in fallback_items})

    return render_template(
        "portfolio.html",
        portfolio_items=portfolio_items,
        categories=categories,
        current_category=category_filter,
    )


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        service = request.form.get("service_interest", "").strip()
        inquiry_type = request.form.get("inquiry_type", "").strip()

        # --- 1. Try saving to the database (works on paid hosting) ---
        db_saved = False
        try:
            new_message = ContactMessage(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
            )
            db.session.add(new_message)
            db.session.commit()
            db_saved = True
        except Exception as e:
            db.session.rollback()
            app.logger.warning("Could not save contact message to DB: %s", e)

        # --- 2. WhatsApp redirect (ideal for Vercel / no-DB hosting) ---
        if app.config.get("WHATSAPP_ENABLED"):
            wa_url = build_whatsapp_url(
                name,
                email,
                phone,
                subject,
                message,
                service=service,
                inquiry_type=inquiry_type,
            )
            # If DB also worked we flash a note; otherwise the redirect is
            # the *only* delivery channel so no flash is needed.
            if db_saved:
                flash(
                    "Message saved! You'll now be redirected to WhatsApp to send it directly.",
                    "success",
                )
            return redirect(wa_url)

        # --- 3. DB-only path (traditional hosting) ---
        if db_saved:
            flash(
                "Thank you for your message! We will contact you soon.",
                "success",
            )
        else:
            flash("An error occurred. Please try again.", "error")

        return redirect(url_for("contact"))

    return render_template("contact.html")


# Password Reset Routes
@app.route("/admin/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Handle forgot password requests"""
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Please enter your email address", "error")
            return redirect(url_for("forgot_password"))

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate reset token
            token = generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(
                hours=app.config["PASSWORD_RESET_TOKEN_EXPIRE_HOURS"]
            )

            # Save token to database
            reset_token = PasswordResetToken(
                user_id=user.id, token=token, expires_at=expires_at
            )

            try:
                # Delete any existing unused tokens for this user
                PasswordResetToken.query.filter_by(
                    user_id=user.id, is_used=False
                ).delete()

                db.session.add(reset_token)
                db.session.commit()

                # Generate reset URL
                reset_url = url_for("reset_password", token=token, _external=True)

                # Send email
                if send_password_reset_email(user.email, reset_url):
                    flash(
                        "Password reset instructions have been sent to your email.",
                        "success",
                    )
                else:
                    flash("Error sending email. Please contact support.", "error")

            except Exception as e:
                db.session.rollback()
                print(f"Error creating reset token: {e}")
                flash("An error occurred. Please try again.", "error")
        else:
            # For security, show success even if email doesn't exist
            flash(
                "If an account exists with that email, reset instructions have been sent.",
                "success",
            )

        return redirect(url_for("admin_login"))

    return render_template("admin/forgot_password.html")


@app.route("/admin/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Handle password reset with token"""
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    # Validate token
    reset_token = PasswordResetToken.query.filter_by(token=token, is_used=False).first()

    if not reset_token:
        flash("Invalid or expired reset token.", "error")
        return redirect(url_for("admin_login"))

    if datetime.utcnow() > reset_token.expires_at:
        flash("Reset token has expired. Please request a new one.", "error")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validate passwords
        if not password or not confirm_password:
            flash("Please fill in all fields", "error")
            return render_template("admin/reset_password.html", token=token)

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("admin/reset_password.html", token=token)

        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return render_template("admin/reset_password.html", token=token)

        # Update user password
        user = User.query.get(reset_token.user_id)
        if user:
            user.password_hash = generate_password_hash(password)
            reset_token.is_used = True

            try:
                db.session.commit()
                flash(
                    "Password has been reset successfully. You can now login with your new password.",
                    "success",
                )
                return redirect(url_for("admin_login"))
            except Exception as e:
                db.session.rollback()
                print(f"Error resetting password: {e}")
                flash("An error occurred. Please try again.", "error")
        else:
            flash("User not found", "error")

    return render_template("admin/reset_password.html", token=token)


@app.route("/admin/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allow logged-in users to change their password"""
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            flash("Please fill in all fields", "error")
            return redirect(url_for("change_password"))

        # Verify current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash("Current password is incorrect", "error")
            return redirect(url_for("change_password"))

        # Check if new password is different
        if check_password_hash(current_user.password_hash, new_password):
            flash("New password must be different from current password", "error")
            return redirect(url_for("change_password"))

        # Validate new password
        if new_password != confirm_password:
            flash("New passwords do not match", "error")
            return redirect(url_for("change_password"))

        if len(new_password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return redirect(url_for("change_password"))

        # Update password
        current_user.password_hash = generate_password_hash(new_password)

        try:
            db.session.commit()
            flash("Password changed successfully", "success")

            # Log user out and redirect to login page
            logout_user()
            return redirect(url_for("admin_login"))

        except Exception as e:
            db.session.rollback()
            print(f"Error changing password: {e}")
            flash("An error occurred. Please try again.", "error")

    return render_template("admin/change_password.html")


# Admin Routes
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Invalid credentials", "error")
            return render_template("admin/login.html")

        try:
            pw_ok = check_password_hash(user.password_hash, password)
        except Exception:
            pw_ok = False

        if not pw_ok:
            flash("Invalid credentials", "error")
            return render_template("admin/login.html")

        login_user(user)
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/login.html")


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    try:
        messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
        unread_count = ContactMessage.query.filter_by(is_read=False).count()
        service_count = Service.query.count()
        portfolio_count = Portfolio.query.count()
        user_count = User.query.count()
    except Exception as e:
        print(f"Database error in admin dashboard: {e}")
        messages = []
        unread_count = 0
        service_count = 0
        portfolio_count = 0
        user_count = 0

    return render_template(
        "admin/dashboard.html",
        messages=messages,
        unread_count=unread_count,
        service_count=service_count,
        portfolio_count=portfolio_count,
        user_count=user_count,
    )


@app.route("/admin/message/<int:message_id>/view")
@login_required
def view_message(message_id):
    try:
        message = ContactMessage.query.get_or_404(message_id)
        return jsonify(
            {
                "success": True,
                "message": {
                    "name": message.name,
                    "email": message.email,
                    "phone": message.phone,
                    "subject": message.subject,
                    "message": message.message,
                    "created_at": message.created_at.strftime("%Y-%m-%d %H:%M"),
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/admin/message/<int:message_id>/read", methods=["POST"])
@login_required
def mark_message_read(message_id):
    try:
        message = ContactMessage.query.get_or_404(message_id)
        message.is_read = True
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Admin Services Management
@app.route("/admin/services")
@login_required
def admin_services():
    try:
        services = Service.query.order_by(Service.category, Service.id).all()
        categories = db.session.query(Service.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
    except Exception as e:
        print(f"Database error in admin services: {e}")
        services = []
        categories = []

    return render_template(
        "admin/services.html", services=services, categories=categories
    )


@app.route("/admin/service/add", methods=["GET", "POST"])
@login_required
def add_service():
    if request.method == "POST":
        try:
            service = Service(
                title=request.form.get("title"),
                description=request.form.get("description"),
                icon=request.form.get("icon"),
                details=request.form.get("details"),
                category=request.form.get("category"),
            )
            db.session.add(service)
            db.session.commit()
            flash("Service added successfully!", "success")
            return redirect(url_for("admin_services"))
        except Exception as e:
            flash(f"Error adding service: {str(e)}", "error")

    return render_template("admin/edit_service.html", categories=SERVICE_CATEGORIES)


@app.route("/admin/service/<int:service_id>/edit", methods=["GET", "POST"])
@login_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)

    if request.method == "POST":
        try:
            service.title = request.form.get("title")
            service.description = request.form.get("description")
            service.icon = request.form.get("icon")
            service.details = request.form.get("details")
            service.category = request.form.get("category")

            db.session.commit()
            flash("Service updated successfully!", "success")
            return redirect(url_for("admin_services"))
        except Exception as e:
            flash(f"Error updating service: {str(e)}", "error")

    return render_template(
        "admin/edit_service.html", service=service, categories=SERVICE_CATEGORIES
    )


@app.route("/admin/service/<int:service_id>/delete", methods=["POST"])
@login_required
def delete_service(service_id):
    try:
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        flash("Service deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting service: {str(e)}", "error")

    return redirect(url_for("admin_services"))


# Admin Portfolio Management
@app.route("/admin/portfolio")
@login_required
def admin_portfolio():
    try:
        portfolio_items = Portfolio.query.order_by(
            Portfolio.featured.desc(), Portfolio.created_at.desc()
        ).all()
    except Exception as e:
        print(f"Database error in admin portfolio: {e}")
        portfolio_items = []

    return render_template("admin/portfolio.html", portfolio_items=portfolio_items)


@app.route("/admin/portfolio/add", methods=["GET", "POST"])
@login_required
def add_portfolio():
    if request.method == "POST":
        try:
            # Handle file upload for image
            image_url = request.form.get("image_url", "").strip() or None
            if has_uploaded_file("image_file"):
                uploaded_url, upload_err = save_uploaded_image(
                    request.files["image_file"], "portfolio"
                )
                if upload_err:
                    flash(upload_err, "error")
                    return render_template(
                        "admin/edit_portfolio.html", categories=SERVICE_CATEGORIES
                    )
                if uploaded_url:
                    image_url = uploaded_url

            portfolio = Portfolio(
                title=request.form.get("title"),
                client=request.form.get("client"),
                description=request.form.get("description"),
                category=request.form.get("category"),
                image_url=image_url,
                project_url=request.form.get("project_url"),
                technologies=request.form.get("technologies"),
                testimonial=request.form.get("testimonial"),
                client_name=request.form.get("client_name"),
                client_role=request.form.get("client_role"),
                featured=bool(request.form.get("featured")),
            )
            db.session.add(portfolio)
            db.session.commit()
            flash("Portfolio item added successfully!", "success")
            return redirect(url_for("admin_portfolio"))
        except Exception as e:
            flash(f"Error adding portfolio item: {str(e)}", "error")

    return render_template("admin/edit_portfolio.html", categories=SERVICE_CATEGORIES)


@app.route("/admin/portfolio/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_portfolio(item_id):
    portfolio = Portfolio.query.get_or_404(item_id)

    if request.method == "POST":
        try:
            # Handle file upload for image
            image_url = request.form.get("image_url", "").strip() or None
            if has_uploaded_file("image_file"):
                uploaded_url, upload_err = save_uploaded_image(
                    request.files["image_file"], "portfolio"
                )
                if upload_err:
                    flash(upload_err, "error")
                    return render_template(
                        "admin/edit_portfolio.html",
                        item=portfolio,
                        categories=SERVICE_CATEGORIES,
                    )
                if uploaded_url:
                    image_url = uploaded_url

            portfolio.title = request.form.get("title")
            portfolio.client = request.form.get("client")
            portfolio.description = request.form.get("description")
            portfolio.category = request.form.get("category")
            if image_url:
                portfolio.image_url = image_url
            portfolio.project_url = request.form.get("project_url")
            portfolio.technologies = request.form.get("technologies")
            portfolio.testimonial = request.form.get("testimonial")
            portfolio.client_name = request.form.get("client_name")
            portfolio.client_role = request.form.get("client_role")
            portfolio.featured = bool(request.form.get("featured"))

            db.session.commit()
            flash("Portfolio item updated successfully!", "success")
            return redirect(url_for("admin_portfolio"))
        except Exception as e:
            flash(f"Error updating portfolio item: {str(e)}", "error")

    return render_template(
        "admin/edit_portfolio.html", portfolio=portfolio, categories=SERVICE_CATEGORIES
    )


@app.route("/admin/portfolio/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_portfolio(item_id):
    try:
        portfolio = Portfolio.query.get_or_404(item_id)
        db.session.delete(portfolio)
        db.session.commit()
        flash("Portfolio item deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting portfolio item: {str(e)}", "error")

    return redirect(url_for("admin_portfolio"))


# Admin Advertisement Management Routes
@app.route("/admin/advertisements")
@login_required
def admin_advertisements():
    """Manage advertisements from admin panel"""
    try:
        # Get filter from query parameter
        filter_type = request.args.get("filter", "all")

        # Base query
        query = Advertisement.query

        # Apply filters
        if filter_type == "active":
            query = query.filter_by(is_active=True)
        elif filter_type == "inactive":
            query = query.filter_by(is_active=False)
        elif filter_type == "expired":
            query = query.filter(Advertisement.end_date < datetime.utcnow())
        elif filter_type == "upcoming":
            query = query.filter(Advertisement.start_date > datetime.utcnow())

        # Get advertisements
        advertisements = query.order_by(
            Advertisement.display_order, Advertisement.created_at.desc()
        ).all()

        # Calculate stats
        total_ads = Advertisement.query.count()
        active_ads = Advertisement.query.filter_by(is_active=True).count()
        inactive_ads = Advertisement.query.filter_by(is_active=False).count()

        expired_ads = Advertisement.query.filter(
            Advertisement.end_date < datetime.utcnow()
        ).count()

        upcoming_ads = Advertisement.query.filter(
            Advertisement.start_date > datetime.utcnow()
        ).count()

    except Exception as e:
        print(f"Error in admin_advertisements: {e}")
        advertisements = []
        total_ads = active_ads = inactive_ads = expired_ads = upcoming_ads = 0
        filter_type = "all"

    return render_template(
        "admin/advertisements.html",
        advertisements=advertisements,
        total_ads=total_ads,
        active_ads=active_ads,
        inactive_ads=inactive_ads,
        expired_ads=expired_ads,
        upcoming_ads=upcoming_ads,
        filter=filter_type,
        now=datetime.utcnow(),
    )


@app.route("/admin/advertisement/add", methods=["GET", "POST"])
@login_required
def add_advertisement():
    """Add new advertisement"""
    if request.method == "POST":
        try:
            # --- Resolve image: uploaded file takes priority over URL ---
            image_url = None
            if has_uploaded_file("image_file"):
                uploaded_url, upload_err = save_uploaded_image(
                    request.files["image_file"], "ads"
                )
                if upload_err:
                    flash(upload_err, "error")
                    return render_template("admin/edit_advertisement.html", ad=None)
                image_url = uploaded_url
            else:
                raw_url = request.form.get("image_url", "").strip()
                if raw_url:
                    image_url = raw_url

            # --- Parse optional dates ---
            start_date = None
            end_date = None
            start_date_str = request.form.get("start_date", "").strip()
            end_date_str = request.form.get("end_date", "").strip()
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M")
                except ValueError:
                    pass
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M")
                except ValueError:
                    pass

            # --- Create advertisement ---
            ad = Advertisement(
                title=request.form.get("title", "").strip(),
                description=request.form.get("description", "").strip(),
                cta_text=request.form.get("cta_text", "Learn More").strip(),
                cta_link=request.form.get("cta_link", "").strip(),
                image_url=image_url,
                background_color=request.form.get("background_color") or "#2563eb",
                text_color=request.form.get("text_color") or "#ffffff",
                is_active=bool(request.form.get("is_active")),
                start_date=start_date,
                end_date=end_date,
                display_order=int(request.form.get("display_order", 0) or 0),
            )

            db.session.add(ad)
            db.session.commit()

            flash("Advertisement created successfully!", "success")
            return redirect(url_for("admin_advertisements"))

        except Exception as e:
            db.session.rollback()
            app.logger.error("Error adding advertisement: %s", e, exc_info=True)
            flash(f"Error creating advertisement: {str(e)}", "error")

    return render_template("admin/edit_advertisement.html", ad=None)


@app.route("/admin/advertisement/<int:ad_id>/edit", methods=["GET", "POST"])
@login_required
def edit_advertisement(ad_id):
    """Edit existing advertisement"""
    ad = Advertisement.query.get_or_404(ad_id)

    if request.method == "POST":
        try:
            # --- Resolve image ---
            if request.form.get("remove_image"):
                ad.image_url = None
            elif has_uploaded_file("image_file"):
                uploaded_url, upload_err = save_uploaded_image(
                    request.files["image_file"], "ads"
                )
                if upload_err:
                    flash(upload_err, "error")
                    return render_template("admin/edit_advertisement.html", ad=ad)
                if uploaded_url:
                    ad.image_url = uploaded_url
            else:
                raw_url = request.form.get("image_url", "").strip()
                # Only update URL if user actually typed something
                # (empty means keep current when no file uploaded)
                if raw_url:
                    ad.image_url = raw_url
                elif not request.form.get("image_url"):
                    pass  # field absent — keep current
                else:
                    ad.image_url = None  # user deliberately cleared it

            # --- Parse optional dates ---
            start_date_str = request.form.get("start_date", "").strip()
            end_date_str = request.form.get("end_date", "").strip()
            ad.start_date = (
                datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M")
                if start_date_str
                else None
            )
            ad.end_date = (
                datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M")
                if end_date_str
                else None
            )

            # --- Update remaining fields ---
            ad.title = request.form.get("title", "").strip()
            ad.description = request.form.get("description", "").strip()
            ad.cta_text = request.form.get("cta_text", "Learn More").strip()
            ad.cta_link = request.form.get("cta_link", "").strip()
            ad.background_color = request.form.get("background_color") or "#2563eb"
            ad.text_color = request.form.get("text_color") or "#ffffff"
            ad.is_active = bool(request.form.get("is_active"))
            ad.display_order = int(request.form.get("display_order", 0) or 0)

            db.session.commit()
            flash("Advertisement updated successfully!", "success")
            return redirect(url_for("admin_advertisements"))

        except Exception as e:
            db.session.rollback()
            app.logger.error("Error updating advertisement: %s", e, exc_info=True)
            flash(f"Error updating advertisement: {str(e)}", "error")

    return render_template("admin/edit_advertisement.html", ad=ad)


@app.route("/admin/advertisement/<int:ad_id>/toggle", methods=["POST"])
@login_required
def toggle_advertisement(ad_id):
    """Toggle advertisement active status"""
    try:
        ad = Advertisement.query.get_or_404(ad_id)
        ad.is_active = not ad.is_active
        db.session.commit()

        status = "activated" if ad.is_active else "deactivated"
        flash(f"Advertisement {status} successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error toggling advertisement: {e}")
        flash(f"Error toggling advertisement: {str(e)}", "error")

    return redirect(url_for("admin_advertisements"))


@app.route("/admin/advertisement/<int:ad_id>/delete", methods=["POST"])
@login_required
def delete_advertisement(ad_id):
    """Delete advertisement"""
    try:
        ad = Advertisement.query.get_or_404(ad_id)
        db.session.delete(ad)
        db.session.commit()
        flash("Advertisement deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting advertisement: {e}")
        flash(f"Error deleting advertisement: {str(e)}", "error")

    return redirect(url_for("admin_advertisements"))


@app.route("/admin/advertisement/<int:ad_id>/move_up", methods=["POST"])
@login_required
def move_advertisement_up(ad_id):
    """Move advertisement up in display order"""
    try:
        ad = Advertisement.query.get_or_404(ad_id)

        # Find previous ad
        prev_ad = (
            Advertisement.query.filter(Advertisement.display_order < ad.display_order)
            .order_by(Advertisement.display_order.desc())
            .first()
        )

        if prev_ad:
            # Swap display orders
            temp_order = ad.display_order
            ad.display_order = prev_ad.display_order
            prev_ad.display_order = temp_order

            db.session.commit()
            flash("Advertisement moved up successfully!", "success")
        else:
            flash("Advertisement is already at the top", "info")

    except Exception as e:
        db.session.rollback()
        print(f"Error moving advertisement up: {e}")
        flash(f"Error moving advertisement: {str(e)}", "error")

    return redirect(url_for("admin_advertisements"))


@app.route("/admin/advertisement/<int:ad_id>/move_down", methods=["POST"])
@login_required
def move_advertisement_down(ad_id):
    """Move advertisement down in display order"""
    try:
        ad = Advertisement.query.get_or_404(ad_id)

        # Find next ad
        next_ad = (
            Advertisement.query.filter(Advertisement.display_order > ad.display_order)
            .order_by(Advertisement.display_order.asc())
            .first()
        )

        if next_ad:
            # Swap display orders
            temp_order = ad.display_order
            ad.display_order = next_ad.display_order
            next_ad.display_order = temp_order

            db.session.commit()
            flash("Advertisement moved down successfully!", "success")
        else:
            flash("Advertisement is already at the bottom", "info")

    except Exception as e:
        db.session.rollback()
        print(f"Error moving advertisement down: {e}")
        flash(f"Error moving advertisement: {str(e)}", "error")

    return redirect(url_for("admin_advertisements"))


# User Management Routes
@app.route("/admin/users")
@login_required
def admin_users():
    """Manage users (only accessible to admins)"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
    except Exception as e:
        app.logger.warning("Error loading users: %s", e)
        users = []
    return render_template("admin/users.html", users=users)


@app.route("/admin/users/add", methods=["GET", "POST"])
@login_required
def add_user():
    """Add new admin user"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate inputs
        if not username or not email or not password:
            flash("Please fill in all fields", "error")
            return redirect(url_for("add_user"))

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return redirect(url_for("add_user"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "error")
            return redirect(url_for("add_user"))

        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return redirect(url_for("add_user"))

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("User added successfully", "success")
            return redirect(url_for("admin_users"))
        except Exception as e:
            db.session.rollback()
            print(f"Error adding user: {e}")
            flash("An error occurred. Please try again.", "error")

    return render_template("admin/add_user.html")


# Test route for email configuration (development only)
@app.route("/admin/test-email")
@login_required
def test_email():
    """Test email configuration (for development only)"""
    if app.config.get("FLASK_ENV") == "production":
        return "Not available in production", 403

    reset_url = url_for("reset_password", token="test-token-123", _external=True)
    success = send_password_reset_email("test@example.com", reset_url)

    return f"Test email sent: {success}<br>Reset URL: {reset_url}"


# Debug route to check advertisements (admin-only)
@app.route("/debug/check-ads")
@login_required
def debug_check_ads():
    """Debug route to check advertisements"""
    try:
        ads = Advertisement.query.all()
        return jsonify(
            {
                "advertisement_table_exists": True,
                "total_ads": len(ads),
                "ads": [
                    {
                        "id": ad.id,
                        "title": ad.title,
                        "description": (
                            ad.description[:50] + "..." if ad.description else ""
                        ),
                        "cta_text": ad.cta_text,
                        "cta_link": ad.cta_link,
                        "background_color": ad.background_color,
                        "text_color": ad.text_color,
                        "is_active": ad.is_active,
                        "display_order": ad.display_order,
                        "created_at": (
                            ad.created_at.strftime("%Y-%m-%d %H:%M")
                            if ad.created_at
                            else ""
                        ),
                    }
                    for ad in ads
                ],
            }
        )
    except Exception as e:
        return jsonify({"error": str(e), "advertisement_table_exists": False})


# Debug route to manually add sample ads (admin-only)
@app.route("/debug/add-sample-ads")
@login_required
def debug_add_sample_ads():
    """Manually add sample ads"""
    try:
        # Delete existing ads first
        Advertisement.query.delete()

        sample_ads = [
            {
                "title": "Special Offer: 20% Off All Services",
                "description": "Launch your projects with our professional services at a discounted rate. Limited time offer!",
                "cta_text": "Claim Offer",
                "cta_link": "/contact",
                "background_color": "#dc2626",
                "text_color": "#ffffff",
                "is_active": True,
                "display_order": 1,
            },
            {
                "title": "New: Data Analytics Dashboard Solutions",
                "description": "Transform your raw data into actionable insights with our new dashboard solutions.",
                "cta_text": "Learn More",
                "cta_link": "/services",
                "background_color": "#2563eb",
                "text_color": "#ffffff",
                "is_active": True,
                "display_order": 2,
            },
        ]

        for ad_data in sample_ads:
            ad = Advertisement(**ad_data)
            db.session.add(ad)

        db.session.commit()

        return f"✅ Added {len(sample_ads)} sample ads. <a href='/'>Go to homepage</a>"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Debug route to check database status (admin-only)
@app.route("/debug/db-status")
@login_required
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
        portfolio_count = Portfolio.query.count() if "portfolio" in tables else 0
        reset_token_count = (
            PasswordResetToken.query.count() if "password_reset_token" in tables else 0
        )
        advertisement_count = (
            Advertisement.query.count() if "advertisement" in tables else 0
        )

        # Get services with categories
        services = Service.query.all()
        services_info = [
            {"title": s.title, "category": s.category, "id": s.id} for s in services
        ]

        return {
            "database": str(app.config["SQLALCHEMY_DATABASE_URI"]),
            "tables": tables,
            "service_count": service_count,
            "user_count": user_count,
            "message_count": message_count,
            "portfolio_count": portfolio_count,
            "reset_token_count": reset_token_count,
            "advertisement_count": advertisement_count,
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
    os.makedirs("static/uploads/portfolio", exist_ok=True)
    os.makedirs("templates/admin", exist_ok=True)
    os.makedirs("static/images/portfolio", exist_ok=True)

    # Initialize database (only when running directly)
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            print(f"⚠️  init_db() failed during startup: {e}")

    # Get port from environment
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
