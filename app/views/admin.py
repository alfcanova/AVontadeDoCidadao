from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from ..decorators import admin_required
from .. import db
from ..models.ibge import IbgeUf, IbgeMunicipio
from ..models.pl import QuorumAssinatura

admin_bp = Blueprint('admin', __name__)

ESCOPOS = ('municipal', 'estadual', 'federal')

def _alvo_nome(q):
    if q.escopo == 'municipal' and q.municipio_id:
        m = db.session.get(IbgeMunicipio, q.municipio_id)
        return m.nome if m else ''
    if q.escopo == 'estadual' and q.uf_id:
        u = db.session.get(IbgeUf, q.uf_id)
        return f"{u.nome}" if u else ''
    return 'Federação'

def _validar_form():
    erros = []
    escopo = request.form.get('escopo', '').strip()
    if escopo not in ESCOPOS:
        erros.append('Escopo inválido.')
    qtd_raw = request.form.get('qtd_minima', '').strip()
    try:
        qtd = int(qtd_raw)
    except ValueError:
        qtd = None
        erros.append('Quantidade mínima deve ser um número inteiro.')
    if qtd is not None and qtd < 0:
        erros.append('Quantidade mínima não pode ser negativa.')
    uf_id, municipio_id = None, None
    if escopo == 'estadual':
        if not request.form.get('uf_id'):
            erros.append('Informe a UF no escopo estadual.')
        else:
            uf_id = int(request.form['uf_id'])
    if escopo == 'municipal':
        if not request.form.get('municipio_id'):
            erros.append('Informe o município no escopo municipal.')
        else:
            municipio_id = int(request.form['municipio_id'])
    if escopo == 'estadual' and request.form.get('uf_id'):
        uf_id = int(request.form['uf_id'])
    descricao = (request.form.get('descricao') or '').strip()
    vigente = request.form.get('vigente') == 'on'
    return escopo, qtd, uf_id, municipio_id, descricao, vigente, erros

def _inativar_outros_vigentes(escopo, uf_id, municipio_id, keep_id=None):
    qs = QuorumAssinatura.query.filter_by(
        escopo=escopo, uf_id=uf_id, municipio_id=municipio_id, vigente=True)
    if keep_id:
        qs = qs.filter(QuorumAssinatura.id != keep_id)
    for q in qs:
        q.vigente = False
        q.updated_by = current_user.id

@admin_bp.route('/')
@admin_required
def index():
    return render_template('admin/index.html')

@admin_bp.route('/quoruns')
@admin_required
def quoruns():
    quoruns = QuorumAssinatura.query.order_by(
        QuorumAssinatura.vigente.desc(), QuorumAssinatura.escopo).all()
    ufs = IbgeUf.query.order_by(IbgeUf.sigla).all()
    lista = [{'q': q, 'alvo': _alvo_nome(q)} for q in quoruns]
    return render_template('admin/quoruns.html', quoruns=lista,
                           ufs=ufs, escopos=ESCOPOS,
                           selected={'escopo': '', 'uf_id': '', 'municipio_id': '',
                                      'qtd_minima': '', 'descricao': '', 'vigente': True,
                                      'id': None})

@admin_bp.route('/quoruns/novo', methods=['POST'])
@admin_required
def quoruns_novo():
    escopo, qtd, uf_id, municipio_id, descricao, vigente, erros = _validar_form()
    if erros:
        for e in erros:
            flash(e)
        return redirect(url_for('admin.quoruns'))
    if vigente:
        _inativar_outros_vigentes(escopo, uf_id, municipio_id)
    q = QuorumAssinatura(escopo=escopo, uf_id=uf_id, municipio_id=municipio_id,
                         qtd_minima=qtd, vigente=vigente, descricao=descricao,
                         updated_by=current_user.id)
    db.session.add(q)
    db.session.commit()
    flash('Quórum criado.')
    return redirect(url_for('admin.quoruns'))

@admin_bp.route('/quoruns/<int:qid>/editar', methods=['POST'])
@admin_required
def quoruns_editar(qid):
    q = db.session.get(QuorumAssinatura, qid)
    if not q:
        abort(404)
    escopo, qtd, uf_id, municipio_id, descricao, vigente, erros = _validar_form()
    if erros:
        for e in erros:
            flash(e)
        return redirect(url_for('admin.quoruns'))
    if vigente:
        _inativar_outros_vigentes(escopo, uf_id, municipio_id, keep_id=q.id)
    q.escopo = escopo
    q.qtd_minima = qtd
    q.uf_id = uf_id
    q.municipio_id = municipio_id
    q.descricao = descricao
    q.vigente = vigente
    q.updated_by = current_user.id
    db.session.commit()
    flash('Quórum atualizado.')
    return redirect(url_for('admin.quoruns'))

@admin_bp.route('/quoruns/<int:qid>/toggle', methods=['POST'])
@admin_required
def quoruns_toggle(qid):
    q = db.session.get(QuorumAssinatura, qid)
    if not q:
        abort(404)
    if q.vigente:
        q.vigente = False
        flash('Quórum inativado.')
    else:
        _inativar_outros_vigentes(q.escopo, q.uf_id, q.municipio_id, keep_id=q.id)
        q.vigente = True
        flash('Quórum ativado.')
    q.updated_by = current_user.id
    db.session.commit()
    return redirect(url_for('admin.quoruns'))