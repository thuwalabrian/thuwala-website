"""Alembic-friendly models shim.

Import model classes here so Alembic can access SQLAlchemy metadata
without triggering application startup code that should only run when
the app is executed.
"""
from app import db

# Import models to ensure metadata is populated
from app import (
    User,
    ContactMessage,
    Service,
    Portfolio,
    PasswordResetToken,
    Advertisement,
)

# Expose metadata for Alembic
target_metadata = db.metadata
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 15:50:44 2026

@author: DMZ
"""

from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)


class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    details = db.Column(db.Text)
