from datetime import datetime
from .. import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    actor_role = db.Column(db.String(20))
    action = db.Column(db.String(100), nullable=False, index=True)
    entity = db.Column(db.String(50), index=True)
    entity_id = db.Column(db.Integer, index=True)
    ip_hash = db.Column(db.String(128), index=True)
    user_agent = db.Column(db.String(255))
    metadata_ = db.Column('metadata', db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
