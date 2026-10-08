import os,sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
from datetime import date

app=create_app()
with app.app_context():
    if User.query.filter_by(username='admin').first():
        print('admin exists'); sys.exit(0)
    u=User(
        username='admin', email='admin@localhost',
        password_hash=generate_password_hash('@dmin123!'),
        role='admin', is_active=True, must_change_password=True,
        nome_completo='Administrador', cpf_hash='seed', cpf_mask='***.***.***-**',
        rg_numero='000000', rg_orgao='SSP', rg_uf='DF',
        data_nascimento=date(2000,1,1),
        titulo_eleitoral='000000000000', zona_eleitoral='000', secao_eleitoral='000',
        cep='70000000', uf='DF', municipio_id=1, bairro='Centro', logradouro='S/N', numero='0'
    )
    db.session.add(u); db.session.commit(); print('admin criado')
