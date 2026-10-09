import re
import requests
from flask import Blueprint, jsonify, request, current_app
from .. import db
from ..models.ibge import IbgeUf, IbgeMunicipio, IbgeDistrito
from ..models.pl import QuorumAssinatura

api_bp = Blueprint('api', __name__)

@api_bp.route('/ufs')
def ufs():
    return jsonify([{'sigla':u.sigla,'nome':u.nome,'id':u.id,'codigo_uf':u.codigo_uf} for u in IbgeUf.query.order_by(IbgeUf.sigla)])

@api_bp.route('/cep/<cep>')
def cep(cep):
    digits = re.sub(r'\D', '', cep or '')
    if len(digits) != 8:
        return jsonify({'error': 'CEP inválido'}), 400
    url = current_app.config['CEP_LOOKUP_URL'].rstrip('/') + f'/{digits}/json/'
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'AVontadeDoCidadao/1.0'})
        data = resp.json()
    except Exception:
        return jsonify({'error': 'Serviço de CEP indisponível'}), 502
    if not isinstance(data, dict) or data.get('erro'):
        return jsonify({'error': 'CEP não encontrado'}), 404
    uf_sigla = (data.get('uf') or '').upper()
    codigo_ibge = data.get('ibge') or ''
    nome_mun = data.get('localidade', '')
    municipio_id = _garantir_municipio(uf_sigla, codigo_ibge, nome_mun)
    return jsonify({
        'cep': digits,
        'logradouro': data.get('logradouro', ''),
        'bairro': data.get('bairro', ''),
        'uf': uf_sigla,
        'municipio': nome_mun,
        'municipio_id': municipio_id,
        'codigo_ibge': codigo_ibge
    })

def _garantir_municipio(uf_sigla, codigo_ibge, nome):
    if not (uf_sigla and codigo_ibge and nome):
        return None
    try:
        cod = int(codigo_ibge)
        ufobj = IbgeUf.query.filter_by(sigla=uf_sigla).first()
        if not ufobj:
            return None
        mun = IbgeMunicipio.query.filter_by(codigo_ibge=cod).first()
        if not mun:
            mun = IbgeMunicipio(codigo_ibge=cod, nome=nome, codigo_uf=ufobj.codigo_uf, uf_sigla=uf_sigla)
            db.session.add(mun)
            db.session.commit()
        return mun.id
    except Exception:
        db.session.rollback()
        return None


@api_bp.route('/municipios')
def municipios():
    uf = request.args.get('uf','').upper()
    q = IbgeMunicipio.query
    if uf: q = q.filter_by(uf_sigla=uf)
    return jsonify([{'id':m.id,'nome':m.nome,'codigo_ibge':m.codigo_ibge,'uf_sigla':m.uf_sigla} for m in q.order_by(IbgeMunicipio.nome)])

@api_bp.route('/municipios/<int:mid>/distritos')
def distritos(mid):
    return jsonify([{'id':d.id,'nome':d.nome,'codigo_distrito':d.codigo_distrito,'is_sede':d.is_sede} for d in IbgeDistrito.query.filter_by(municipio_id=mid).order_by(IbgeDistrito.nome)])

@api_bp.route('/quorum')
def quorum():
    escopo = request.args.get('escopo')
    uf = request.args.get('uf','').upper()
    municipio_id = request.args.get('municipio_id', type=int)

    q = QuorumAssinatura.query.filter_by(escopo=escopo, vigente=True)
    qtd_minima = 0
    quorum_alvo_id = None
    if escopo == 'municipal' and municipio_id:
        spec = q.filter_by(municipio_id=municipio_id).first()
        if spec:
            qtd_minima, quorum_alvo_id = spec.qtd_minima, spec.id
    elif escopo == 'estadual' and uf:
        ufobj = IbgeUf.query.filter_by(sigla=uf).first()
        if ufobj:
            spec = q.filter_by(uf_id=ufobj.id).first()
            if spec:
                qtd_minima, quorum_alvo_id = spec.qtd_minima, spec.id
    if quorum_alvo_id is None:
        geral = q.filter_by(uf_id=None, municipio_id=None).first()
        if geral:
            qtd_minima, quorum_alvo_id = geral.qtd_minima, geral.id

    from ..services import tse
    uf_sigla = uf
    codigo_ibge = None
    if escopo == 'municipal' and municipio_id:
        mun = db.session.get(IbgeMunicipio, municipio_id)
        if mun:
            uf_sigla = mun.uf_sigla
            codigo_ibge = mun.codigo_ibge
    info = tse.calcular(escopo, uf_sigla=uf_sigla, codigo_ibge=codigo_ibge)
    payload = {'qtd_minima': qtd_minima, 'quorum_alvo_id': quorum_alvo_id}
    payload.update(info)
    return jsonify(payload)
