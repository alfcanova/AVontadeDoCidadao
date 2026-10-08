from datetime import datetime
from .. import db

class RestricaoLegal(db.Model):
    __tablename__ = 'restricoes_legais'
    id = db.Column(db.Integer, primary_key=True)
    norma = db.Column(db.String(50), nullable=False)
    numero = db.Column(db.String(50), nullable=False)
    artigo = db.Column(db.String(50))
    descricao = db.Column(db.Text, nullable=False)
    escopos_alvo = db.Column(db.JSON, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class QuorumAssinatura(db.Model):
    __tablename__ = 'quoruns_assinaturas'
    id = db.Column(db.Integer, primary_key=True)
    escopo = db.Column(db.String(20), nullable=False)
    uf_id = db.Column(db.Integer, db.ForeignKey('ibge_ufs.id'))
    municipio_id = db.Column(db.Integer, db.ForeignKey('ibge_municipios.id'))
    qtd_minima = db.Column(db.Integer, nullable=False, default=0)
    vigente = db.Column(db.Boolean, nullable=False, default=True)
    descricao = db.Column(db.String(150))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class PlDeIp(db.Model):
    __tablename__ = 'pl_de_ip'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    ementa = db.Column(db.Text, nullable=False)
    texto_integral = db.Column(db.Text, nullable=False)
    escopo = db.Column(db.String(20), nullable=False)
    uf_id = db.Column(db.Integer, db.ForeignKey('ibge_ufs.id'))
    municipio_id = db.Column(db.Integer, db.ForeignKey('ibge_municipios.id'))
    status = db.Column(db.String(25), nullable=False, default='rascunho')
    autor_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    versao = db.Column(db.Integer, nullable=False, default=1)
    assinaturas_minimas_definidas = db.Column(db.Integer, default=0)
    quorum_alvo_id = db.Column(db.Integer, db.ForeignKey('quoruns_assinaturas.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    submitted_at = db.Column(db.DateTime)
    disponibilizado_em = db.Column(db.DateTime)
    retirado_em = db.Column(db.DateTime)
    concluido_em = db.Column(db.DateTime)

class PlRestricao(db.Model):
    __tablename__ = 'pl_restricoes'
    id = db.Column(db.Integer, primary_key=True)
    pl_id = db.Column(db.Integer, db.ForeignKey('pl_de_ip.id', ondelete='CASCADE'), nullable=False)
    restricao_legal_id = db.Column(db.Integer, db.ForeignKey('restricoes_legais.id'), nullable=False)
    observacao = db.Column(db.Text)
    __table_args__ = (db.UniqueConstraint('pl_id', 'restricao_legal_id'),)
