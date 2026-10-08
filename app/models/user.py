from datetime import datetime
from flask_login import UserMixin
from .. import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    nome_completo = db.Column(db.String(150), nullable=False)
    cpf_hash = db.Column(db.String(128), unique=True, nullable=False, index=True)
    cpf_mask = db.Column(db.String(14), nullable=False)
    rg_numero = db.Column(db.String(20), nullable=False)
    rg_orgao = db.Column(db.String(15), nullable=False)
    rg_uf = db.Column(db.String(2), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    titulo_eleitoral = db.Column(db.String(12), unique=True, nullable=False, index=True)
    zona_eleitoral = db.Column(db.String(4), nullable=False)
    secao_eleitoral = db.Column(db.String(4), nullable=False)
    cep = db.Column(db.String(8), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    municipio_id = db.Column(db.Integer, db.ForeignKey('ibge_municipios.id'), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    logradouro = db.Column(db.String(150), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    complemento = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime)
