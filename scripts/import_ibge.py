import os
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models.ibge import IbgeUf, IbgeMunicipio

BASE = 'https://servicodados.ibge.gov.br/api/v1/localidades'
HEADERS = {'User-Agent': 'AVontadeDoCidadao/1.0'}


def carregar_ufs():
    resp = requests.get(f'{BASE}/estados', timeout=30, headers=HEADERS)
    resp.raise_for_status()
    total = 0
    for uf in resp.json():
        reg = IbgeUf.query.filter_by(sigla=uf['sigla']).first()
        if not reg:
            reg = IbgeUf(sigla=uf['sigla'])
            db.session.add(reg)
        reg.codigo_uf = int(uf['id'])
        reg.nome = uf['nome']
        total += 1
    db.session.commit()
    return total


def carregar_municipios(sigla):
    resp = requests.get(f'{BASE}/estados/{sigla}/municipios', timeout=60, headers=HEADERS)
    resp.raise_for_status()
    dados = resp.json()
    uf = IbgeUf.query.filter_by(sigla=sigla).first()
    total = 0
    for m in dados:
        cod = int(m['id'])
        reg = IbgeMunicipio.query.filter_by(codigo_ibge=cod).first()
        if not reg:
            reg = IbgeMunicipio(codigo_ibge=cod)
            db.session.add(reg)
        reg.nome = m['nome']
        reg.codigo_uf = uf.codigo_uf
        reg.uf_sigla = sigla
        micro = m.get('microrregiao') or {}
        meso = micro.get('mesorregiao') or {}
        reg.nome_microrregiao = micro.get('nome')
        reg.nome_mesorregiao = meso.get('nome')
        total += 1
    db.session.commit()
    return total


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        n_ufs = carregar_ufs()
        print(f'UFs importadas: {n_ufs}')
        siglas = [u.sigla for u in IbgeUf.query.order_by(IbgeUf.sigla)]
        for sigla in siglas:
            try:
                n = carregar_municipios(sigla)
                print(f'  {sigla}: {n} municípios')
            except Exception as e:
                print(f'  {sigla}: ERRO {e}')
        print('Total municípios:', IbgeMunicipio.query.count())


if __name__ == '__main__':
    main()
