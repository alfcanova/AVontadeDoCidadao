from datetime import datetime
from .. import db

class EleitoradoTse(db.Model):
    __tablename__ = 'eleitorado_tse'
    id = db.Column(db.Integer, primary_key=True)
    escopo = db.Column(db.String(20), nullable=False)
    uf_sigla = db.Column(db.String(2))
    codigo_ibge = db.Column(db.Integer)
    qtd_eleitores = db.Column(db.Integer, nullable=False, default=0)
    ano_referencia = db.Column(db.Integer)
    fonte = db.Column(db.String(120))
    coletado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        db.UniqueConstraint('escopo', 'uf_sigla', 'codigo_ibge', name='uq_eleitorado_tse_alvo'),
    )

    def __repr__(self):
        return f'<EleitoradoTse {self.escopo} {self.uf_sigla} {self.codigo_ibge}={self.qtd_eleitores}>'
