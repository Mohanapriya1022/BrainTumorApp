from flask_login import UserMixin
from datetime import datetime
from . import db

# ================= DOCTOR–PATIENT ASSOCIATION TABLE =================
doctor_patient = db.Table(
    'doctor_patient',
    db.Column('doctor_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('patient_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# ================= USER MODEL =================
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    # Basic Info
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'doctor'

    # ===== Patient Profile Fields =====
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    place = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    profile_image = db.Column(
        db.String(200),
        default="default.png"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # ===== Doctor → Assigned Patients =====
    patients = db.relationship(
        'User',
        secondary=doctor_patient,
        primaryjoin=(id == doctor_patient.c.doctor_id),
        secondaryjoin=(id == doctor_patient.c.patient_id),
        backref=db.backref('assigned_doctors', lazy='dynamic'),
        lazy='dynamic'
    )

    # ===== Patient → Reports =====
    reports = db.relationship(
        'Report',
        backref='patient',
        lazy=True,
        cascade="all, delete-orphan"
    )

    # ===== Audit Logs =====
    logs = db.relationship(
        'AuditLog',
        backref='user',
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.name} ({self.role})>"


# ================= REPORT MODEL =================
class Report(db.Model):
    __tablename__ = "report"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    image_path = db.Column(db.String(200), nullable=False)
    result_image_path = db.Column(db.String(200))

    tumor_detected = db.Column(db.Boolean, default=False)
    tumor_type = db.Column(db.String(50))
    severity = db.Column(db.String(50))
    confidence = db.Column(db.Float)

    # Engineering Feature
    tumor_area_px = db.Column(db.Float)

    doctor_comments = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Report {self.id} - Patient {self.patient_id}>"


# ================= AUDIT LOG MODEL =================
class AuditLog(db.Model):
    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    action = db.Column(db.String(255))

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<AuditLog {self.user_id} - {self.action}>"