from datetime import datetime
from .. import db

class LgpdConsent(db.Model):
    __tablename__ = 'lgpd_consents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    actor_type = db.Column(db.String(10), nullable=False, default='user')
    ip_hash = db.Column(db.String(128), nullable=False)
    user_agent = db.Column(db.String(255))
    consent_version = db.Column(db.String(20), nullable=False)
    legal_link_used = db.Column(db.String(255), nullable=False)
    consented_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
