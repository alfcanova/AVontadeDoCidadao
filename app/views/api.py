from flask import Blueprint, jsonify, request
from ..models.ibge import IbgeUf, IbgeMunicipio, IbgeDistrito
from ..models.pl import QuorumAssinatura

api_bp = Blueprint('api', __name__)

@api_bp.route('/ufs')
def ufs():
    return jsonify([{'sigla':u.sigla,'nome':u.nome,'id':u.id,'codigo_uf':u.codigo_uf} for u in IbgeUf.query.order_by(IbgeUf.sigla)])

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
    if escopo=='municipal' and municipio_id:
        spec = q.filter_by(municipio_id=municipio_id).first()
        if spec: return jsonify({'qtd_minima':spec.qtd_minima,'quorum_alvo_id':spec.id})
    if escopo=='estadual' and uf:
        from ..models.ibge import IbgeUf
        ufobj = IbgeUf.query.filter_by(sigla=uf).first()
        if ufobj:
            spec = q.filter_by(uf_id=ufobj.id).first()
            if spec: return jsonify({'qtd_minima':spec.qtd_minima,'quorum_alvo_id':spec.id})
    geral = q.filter_by(uf_id=None, municipio_id=None).first()
    if geral: return jsonify({'qtd_minima':geral.qtd_minima,'quorum_alvo_id':geral.id})
    return jsonify({'qtd_minima':0,'quorum_alvo_id':None})
