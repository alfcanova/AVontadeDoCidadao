from datetime import datetime
from .. import db

class ChaveAssinatura(db.Model):
    __tablename__ = 'chaves_assinatura'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo_chave = db.Column(db.String(15), nullable=False, default='sistema')
    pubkey_pem = db.Column(db.Text, nullable=False)
    privkey_encrypted = db.Column(db.Text)
    ativa = db.Column(db.Boolean, nullable=False, default=True)
    revogada_em = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Assinatura(db.Model):
    __tablename__ = 'assinaturas'
    id = db.Column(db.Integer, primary_key=True)
    pl_id = db.Column(db.Integer, db.ForeignKey('pl_de_ip.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    documento_hash = db.Column(db.String(128), nullable=False)
    signed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_hash = db.Column(db.String(128))
    user_agent = db.Column(db.String(255))
    assinatura_hash = db.Column(db.String(128))
    pubkey_pem_ref = db.Column(db.Text)
    chave_assinatura_id = db.Column(db.Integer, db.ForeignKey('chaves_assinatura.id'))
    protocolo_govbr = db.Column(db.String(100))
    data_assinatura_govbr = db.Column(db.DateTime)
    hash_documento_govbr = db.Column(db.String(128))
    govbr_metadata = db.Column(db.JSON)
    pdf_uuid = db.Column(db.String(36))
    signer_name = db.Column(db.String(150))
    signer_doc_tipo = db.Column(db.String(10))
    signer_doc_hash = db.Column(db.String(128))
    dados_verificacao = db.Column(db.Text)
    verificavel = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
