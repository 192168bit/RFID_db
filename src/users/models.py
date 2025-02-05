# from src import db
from sqlalchemy import Column, Integer, String, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    contact_num = db.Column(db.Integer(50), unique=True, nullable=False)
    address = db.Column(db.String(200))
    email = db.Column(db.String(100), nullable=False)
    type_id = db.Column(db.Integer, ForeignKey("types.id"), nullable=False)
    level_id = db.Column(db.Integer, ForeignKey("levels.id"), nullable=False)
    section_id = db.Column(db.Integer, ForeignKey("section.id"), nullable=False)
    strand_id = db.Column(db.Integer, ForeignKey("strand.id"), nullable=False)
    attendance = db.relationship("Attendance", backref="users", lazy=True)


class Types(db.Model):
    __tablename__ = "types"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    type_name = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.relationship("Users", backref="types", lazy=True)


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utc, nullable=False)


class Levels(db.Model):
    __tablename__ = "levels"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    grade_level = db.Column(db.Integer(50), unique=True, nullable=False)


class Sections(db.Model):
    __tablename__ = "sections"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    section_name = db.Column(db.String, unique=True, nullable=False)


class Strands(db.Model):
    __tablename__ = "strand"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    strand_name = db.Column(db.String(100), unique=True, nullable=False)
