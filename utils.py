# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 15:52:28 2026

@author: DMZ
"""

import os
from werkzeug.security import generate_password_hash
from app import db
from models import User, Service


def create_folders():
    """Create necessary folders"""
    folders = [
        "static/uploads",
        "templates/admin",
        "static/css",
        "static/js",
        "static/images",
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    return True


def init_database():
    """Initialize database with sample data"""
    # Create tables
    db.create_all()

    # Create admin user
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@thuwalaco.com",
            password_hash=generate_password_hash("Admin@2024"),
        )
        db.session.add(admin)

    # Add sample services
    if not Service.query.first():
        services = [
            {
                "title": "Administrative & Executive Support",
                "description": "Virtual assistant services, document formatting, calendar management",
                "icon": "fas fa-briefcase",
                "details": "Report writing, document formatting, minute-taking, calendar management, task management, filing systems, policy support",
            },
            {
                "title": "Project & Operations Support",
                "description": "Proposal writing, budget tracking, donor reporting",
                "icon": "fas fa-project-diagram",
                "details": "Proposal and report writing, budget tracking, M&E data management, donor reporting, stakeholder coordination",
            },
            {
                "title": "Data Management & Analytics",
                "description": "Data cleaning, analysis, dashboard design, visualization",
                "icon": "fas fa-chart-bar",
                "details": "Data collection, data entry, cleaning, analysis, dashboard design, visualization, executive summaries",
            },
            {
                "title": "Communications & Documentation",
                "description": "Corporate profiles, proposal writing, report editing",
                "icon": "fas fa-comments",
                "details": "Corporate profiles, capability statements, proposal writing, report editing, success stories, press releases",
            },
            {
                "title": "Branding, Design & Marketing",
                "description": "Logo design, marketing materials, social media strategy",
                "icon": "fas fa-palette",
                "details": "Logo and brand identity design, company profiles, social media setup, digital marketing campaigns",
            },
            {
                "title": "Business & Startup Support",
                "description": "Business registration, business plans, company profiles",
                "icon": "fas fa-rocket",
                "details": "Business registration guidance, proposal and business plan writing, company profile creation, digital system setup",
            },
        ]

        for service_data in services:
            service = Service(**service_data)
            db.session.add(service)

    db.session.commit()
    return True
