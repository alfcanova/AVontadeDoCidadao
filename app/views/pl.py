from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .. import db
from ..models.pl import PlDeIp, QuorumAssinatura
from ..models.assinatura import Assinatura
from ..models.ibge import IbgeUf, IbgeMunicipio
from ..models.user import User
from ..services import tse

pl_bp = Blueprint('pl', __name__)

ESCOPO_LABEL = {
    'municipal': 'Municipal',
    'estadual': 'Estadual',
    'federal': 'Federal',
}
STATUS_LABEL = {
    'rascunho': 'Rascunho',
    'submetido': 'Submetido',
    'em_votacao': 'Em votação',
    'disponivel': 'Disponível',
    'retirado': 'Retirado',
    'concluido': 'Concluído',
    'reprovado': 'Reprovado',
    'arquivado': 'Arquivado',
}

def pode_editar(pl):
    return pl.status == 'rascunho'

def _campos_validos():
    erros = {}
    escopo = (request.form.get('escopo') or '').strip()
    uf_id = None
    municipio_id = None
    if request.form.get('uf_id'):
        uf_id = int(request.form['uf_id'])
    if request.form.get('municipio_id'):
        municipio_id = int(request.form['municipio_id'])
    titulo = (request.form.get('titulo') or '').strip()
    ementa = (request.form.get('ementa') or '').strip()
    texto = (request.form.get('texto_integral') or '').strip()
    if not titulo:
        erros['titulo'] = 'Informe o título do projeto.'
    if not ementa:
        erros['ementa'] = 'Informe a ementa.'
    if not texto:
        erros['texto_integral'] = 'Informe o texto integral.'
    if escopo not in ESCOPO_LABEL:
        erros['escopo'] = 'Escopo inválido.'
    if escopo == 'municipal' and not municipio_id:
        erros['municipio_id'] = 'Informe o município no escopo municipal.'
    if escopo == 'estadual' and not uf_id:
        erros['uf_id'] = 'Informe a UF no escopo estadual.'
    if escopo == 'federal':
        uf_id = None
        municipio_id = None
    return titulo, ementa, texto, escopo, uf_id, municipio_id, erros

def _resolver_quorum(escopo, uf_id, municipio_id):
    q = QuorumAssinatura.query.filter_by(escopo=escopo, vigente=True)
    if escopo == 'municipal' and municipio_id:
        spec = q.filter_by(municipio_id=municipio_id).first()
        if spec:
            return spec
    if escopo == 'estadual' and uf_id:
        spec = q.filter_by(uf_id=uf_id).first()
        if spec:
            return spec
    return q.filter_by(uf_id=None, municipio_id=None).first()

def _alvo_escopo(escopo, uf_id, municipio_id):
    uf_sigla = None
    codigo_ibge = None
    if escopo == 'municipal' and municipio_id:
        mun = db.session.get(IbgeMunicipio, municipio_id)
        if mun:
            uf_sigla = mun.uf_sigla
            codigo_ibge = mun.codigo_ibge
    elif escopo == 'estadual' and uf_id:
        uf = db.session.get(IbgeUf, uf_id)
        if uf:
            uf_sigla = uf.sigla
    return uf_sigla, codigo_ibge

@pl_bp.route('/')
def listar():
    rows = (db.session.query(PlDeIp, User.nome_completo)
            .join(User, PlDeIp.autor_user_id == User.id)
            .order_by(PlDeIp.created_at.desc()).all())
    contagens = dict(db.session.query(Assinatura.pl_id, db.func.count(Assinatura.id))
                     .group_by(Assinatura.pl_id).all())
    projetos = []
    for pl, autor in rows:
        projetos.append({
            'id': pl.id,
            'titulo': pl.titulo,
            'ementa': pl.ementa,
            'escopo': ESCOPO_LABEL.get(pl.escopo, pl.escopo),
            'status': STATUS_LABEL.get(pl.status, pl.status),
            'status_raw': pl.status,
            'autor': autor,
            'autor_id': pl.autor_user_id,
            'created_at': pl.created_at,
            'minimo': pl.assinaturas_minimas_definidas or 0,
            'assinaturas': contagens.get(pl.id, 0),
        })
    return render_template('pl/listar.html', projetos=projetos)

@pl_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    ufs = IbgeUf.query.order_by(IbgeUf.sigla).all()
    if request.method == 'POST':
        titulo, ementa, texto, escopo, uf_id, municipio_id, erros = _campos_validos()
        if erros:
            for v in erros.values():
                flash(v)
            return render_template('pl/form.html', pl=None, ufs=ufs,
                                   vals=request.form.to_dict(), erros=erros)
        pl = PlDeIp(titulo=titulo, ementa=ementa, texto_integral=texto,
                    escopo=escopo, uf_id=uf_id, municipio_id=municipio_id,
                    status='rascunho', autor_user_id=current_user.id, versao=1)
        db.session.add(pl)
        db.session.commit()
        flash('Projeto criado como rascunho. Finalize e submeta quando estiver pronto.')
        return redirect(url_for('pl.listar'))
    return render_template('pl/form.html', pl=None, ufs=ufs, vals={}, erros={})

@pl_bp.route('/<int:pid>/editar', methods=['GET', 'POST'])
@login_required
def editar(pid):
    pl = db.session.get(PlDeIp, pid) or abort(404)
    if pl.autor_user_id != current_user.id:
        abort(403)
    if not pode_editar(pl):
        flash('Este projeto está em processo de coleta de assinaturas e não pode mais ser editado.')
        return redirect(url_for('pl.listar'))
    ufs = IbgeUf.query.order_by(IbgeUf.sigla).all()
    if request.method == 'POST':
        titulo, ementa, texto, escopo, uf_id, municipio_id, erros = _campos_validos()
        if erros:
            for v in erros.values():
                flash(v)
            return render_template('pl/form.html', pl=pl, ufs=ufs,
                                   vals=request.form.to_dict(), erros=erros)
        pl.titulo = titulo
        pl.ementa = ementa
        pl.texto_integral = texto
        pl.escopo = escopo
        pl.uf_id = uf_id
        pl.municipio_id = municipio_id
        pl.versao += 1
        db.session.commit()
        flash('Rascunho atualizado.')
        return redirect(url_for('pl.editar', pid=pl.id))
    vals = {'titulo': pl.titulo, 'ementa': pl.ementa, 'texto_integral': pl.texto_integral,
            'escopo': pl.escopo, 'uf_id': str(pl.uf_id or ''),
            'municipio_id': str(pl.municipio_id or '')}
    uf_label = uf_sigla = mun_label = ''
    if pl.uf_id:
        uf = db.session.get(IbgeUf, pl.uf_id)
        if uf:
            uf_label = f"{uf.sigla} - {uf.nome}"
            uf_sigla = uf.sigla
    if pl.municipio_id:
        mun = db.session.get(IbgeMunicipio, pl.municipio_id)
        if mun:
            mun_label = mun.nome
    return render_template('pl/form.html', pl=pl, ufs=ufs, vals=vals, erros={},
                           uf_label=uf_label, uf_sigla=uf_sigla, mun_label=mun_label)

@pl_bp.route('/<int:pid>/submeter', methods=['POST'])
@login_required
def submeter(pid):
    pl = db.session.get(PlDeIp, pid) or abort(404)
    if pl.autor_user_id != current_user.id:
        abort(403)
    if not pode_editar(pl):
        flash('Este projeto já está em processo de coleta de assinaturas e não pode ser submetido novamente.')
        return redirect(url_for('pl.listar'))
    q = _resolver_quorum(pl.escopo, pl.uf_id, pl.municipio_id)
    uf_sigla, codigo_ibge = _alvo_escopo(pl.escopo, pl.uf_id, pl.municipio_id)
    info = tse.calcular(pl.escopo, uf_sigla=uf_sigla, codigo_ibge=codigo_ibge)
    minimo = info.get('qtd_assinaturas')
    if not minimo:
        if not q:
            flash('Não há quórum vigente definido para o alvo deste projeto. Contate a administração.')
            return redirect(url_for('pl.editar', pid=pl.id))
        minimo = q.qtd_minima
    pl.quorum_alvo_id = q.id if q else None
    pl.assinaturas_minimas_definidas = minimo
    pl.status = 'submetido'
    pl.submitted_at = datetime.utcnow()
    pl.versao += 1
    db.session.commit()
    flash('Projeto submetido. A coleta de assinaturas começou e ele não pode mais ser editado.')
    return redirect(url_for('pl.listar'))