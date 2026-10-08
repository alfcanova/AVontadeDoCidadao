import os,sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app, db
from app.models.ibge import IbgeUf, IbgeMunicipio

app=create_app()
with app.app_context():
    ufs=[('DF','Distrito Federal',53),('SP','Sao Paulo',35),('RJ','Rio de Janeiro',33),('MG','Minas Gerais',31),('RS','Rio Grande do Sul',43)]
    for sigla,nome,cod in ufs:
        if not IbgeUf.query.filter_by(sigla=sigla).first():
            db.session.add(IbgeUf(codigo_uf=cod,sigla=sigla,nome=nome))
    db.session.commit()
    print('ok')
