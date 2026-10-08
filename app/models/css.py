from datetime import datetime
from .. import db

class UserCssPreference(db.Model):
    __tablename__ = 'user_css_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    css_filename = db.Column(db.String(255), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class CssFile(db.Model):
    __tablename__ = 'css_files'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    original_filename = db.Column(db.String(255))
    mime_type = db.Column(db.String(50))
    size_bytes = db.Column(db.Integer)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sha256 = db.Column(db.String(128))
