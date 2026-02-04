# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 15:51:54 2026

@author: DMZ
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
    name = StringField(
        "Name", validators=[DataRequired(), Length(min=2, max=100)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone")
    subject = StringField("Subject", validators=[Length(max=200)])
    message = TextAreaField(
        "Message", validators=[DataRequired(), Length(min=10)]
    )
    submit = SubmitField("Send Message")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
