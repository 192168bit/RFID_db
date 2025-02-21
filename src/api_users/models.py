import uuid

from sqlalchemy import func
from src import db
from datetime import datetime, timezone
from werkzeug.security import check_password_hash


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rfid_tag = db.Column(db.String(255), nullable=True)
    photo_url = db.Column(db.String(225), nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    contact_num = db.Column(db.String(100), unique=True, nullable=False)
    parent_phone = db.Column(db.String(100), unique=True, nullable=True)
    address = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    type_id = db.Column(db.Integer, db.ForeignKey("usertypes.id"), nullable=False)
    type = db.relationship("UserTypes", backref="user", lazy=True)

    level_id = db.Column(db.Integer, db.ForeignKey("levels.id"), nullable=True)
    level = db.relationship("Levels", backref="user", lazy=True)

    section_id = db.Column(db.Integer, db.ForeignKey("sections.id"), nullable=True)
    section = db.relationship("Sections", backref="user", lazy=True)

    strand_id = db.Column(db.Integer, db.ForeignKey("strands.id"), nullable=True)
    strand = db.relationship("Strands", backref="user", lazy=True)

    def toDict(self):
        return {
            "id": self.id,
            "rfid_tag": self.rfid_tag,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "contact_num": self.contact_num,
            "parent_phone": self.parent_phone,
            "photo_url": self.photo_url,
            "email": self.email,
            "type_id": self.type_id,
            "type_name": self.type.type_name if self.type else None,
            "level_id": self.level_id,
            "level_name": self.level.level_name if self.level else None,
            "section_id": self.section_id,
            "section_name": self.section.section_name if self.section else None,
            "strand_id": self.strand_id,
            "strand_name": self.strand.strand_name if self.strand else None,
        }

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User(first_name={self.first_name}, last_name={self.last_name})>"


class UserTypes(db.Model):
    __tablename__ = "usertypes"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    type_name = db.Column(db.String, unique=True, nullable=False)

    def toDict(self):
        return {"id": self.id, "type_name": self.type_name}


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rfid_tag = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now(), server_default=func.now())
    status = db.Column(db.String(100), nullable=True)
    time_in = db.Column(db.DateTime, nullable=True)  # Time when the user checks in
    time_out = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("Users", backref="attendances")

    def toDict(self):
        return {"id": self.id, "status": self.status, "timestamp": self.timestamp}


class Levels(db.Model):
    __tablename__ = "levels"
    id = db.Column(db.Integer, primary_key=True)
    level_name = db.Column(db.String, unique=True, nullable=False)

    def toDict(self):
        return {"id": self.id, "level_name": self.level_name}


class Sections(db.Model):
    __tablename__ = "sections"
    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String, unique=True, nullable=False)

    def toDict(self):
        return {"id": self.id, "section_name": self.section_name}


class Strands(db.Model):
    __tablename__ = "strands"
    id = db.Column(db.Integer, primary_key=True)
    strand_name = db.Column(db.String, unique=True, nullable=False)

    def toDict(self):
        return {"id": self.id, "strand_name": self.strand_name}


class Events(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(255))
    event_date = db.Column(db.String(255))
    event_month = db.Column(db.String(50), nullable=False)

    def toDict(self):
        return {
            "id": self.id,
            "event_name": self.event_name,
            "event_date": self.event_date,
            "event_month": self.event_month
        }


class RFIDs(db.Model):
    __tablename__ = "rfids"
    id = db.Column(db.Integer, primary_key=True)
    rfid_tag = db.Column(db.String(255), unique=True)
    timestamp = db.Column(db.DateTime, default=func.now(), server_default=func.now())

    def toDict(self):
        return {
            "id": self.id,
            "rfid_tag": self.rfid_tag,
            "timestamp": self.timestamp
        }