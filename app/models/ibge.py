from .. import db

class IbgeUf(db.Model):
    __tablename__ = 'ibge_ufs'
    id = db.Column(db.Integer, primary_key=True)
    codigo_uf = db.Column(db.Integer, unique=True, nullable=False)
    sigla = db.Column(db.String(2), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)

class IbgeMunicipio(db.Model):
    __tablename__ = 'ibge_municipios'
    id = db.Column(db.Integer, primary_key=True)
    codigo_ibge = db.Column(db.Integer, unique=True, nullable=False, index=True)
    nome = db.Column(db.String(150), nullable=False, index=True)
    codigo_uf = db.Column(db.Integer, db.ForeignKey('ibge_ufs.codigo_uf'), nullable=False)
    uf_sigla = db.Column(db.String(2), nullable=False, index=True)
    nome_mesorregiao = db.Column(db.String(100))
    nome_microrregiao = db.Column(db.String(100))

class IbgeDistrito(db.Model):
    __tablename__ = 'ibge_distritos'
    id = db.Column(db.Integer, primary_key=True)
    codigo_distrito = db.Column(db.BigInteger, unique=True, nullable=False, index=True)
    nome = db.Column(db.String(150), nullable=False, index=True)
    codigo_municipio = db.Column(db.Integer, db.ForeignKey('ibge_municipios.codigo_ibge'), nullable=False, index=True)
    municipio_id = db.Column(db.Integer, db.ForeignKey('ibge_municipios.id'))
    is_sede = db.Column(db.Boolean, nullable=False, default=False)
