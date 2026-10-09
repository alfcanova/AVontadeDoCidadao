import re
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .. import db
from ..models.user import User
from ..utils.validators import calc_idade, TITULO_RE, ZONA_RE, SECAO_RE, CEP_RE

user_bp = Blueprint('user', __name__)

@user_bp.route('/perfil', methods=['GET','POST'])
@login_required
def perfil():
    from ..models.ibge import IbgeUf
    u = current_user
    ufs = IbgeUf.query.order_by(IbgeUf.sigla).all()
    if request.method=='POST':
        email = request.form.get('email','').strip().lower()
        nome = request.form.get('nome_completo','').strip()
        senha = request.form.get('senha','')
        senha_conf = request.form.get('senha_confirm','')
        rg_num = request.form.get('rg_numero','').strip()
        rg_org = request.form.get('rg_orgao','').strip().upper()
        rg_uf = request.form.get('rg_uf','').strip().upper()
        dn_str = request.form.get('data_nascimento','')
        titulo = request.form.get('titulo_eleitoral','').strip()
        zona = request.form.get('zona_eleitoral','').strip()
        secao = request.form.get('secao_eleitoral','').strip()
        cep = ''.join(re.findall(r'\d', request.form.get('cep','')))
        uf = request.form.get('uf','').strip().upper()
        municipio_id = request.form.get('municipio_id') or None
        bairro = request.form.get('bairro','').strip()
        logradouro = request.form.get('logradouro','').strip()
        numero = request.form.get('numero','').strip()
        complemento = request.form.get('complemento','').strip() or None

        erros=[]
        if senha or senha_conf:
            if len(senha) < 4: erros.append('Senha deve ter ao menos 4 caracteres')
            if senha != senha_conf: erros.append('Senhas não conferem')
        outro = User.query.filter(User.email==email, User.id!=u.id).first()
        if outro: erros.append('E-mail já cadastrado')
        if not TITULO_RE.match(titulo): erros.append('Título eleitoral inválido')
        outro = User.query.filter(User.titulo_eleitoral==titulo, User.id!=u.id).first()
        if outro: erros.append('Título já cadastrado')
        if not ZONA_RE.match(zona): erros.append('Zona inválida')
        if not SECAO_RE.match(secao): erros.append('Seção inválida')
        if not CEP_RE.match(cep): erros.append('CEP inválido')
        try:
            dn = date.fromisoformat(dn_str)
            if calc_idade(dn) < 16: erros.append('Deve ser maior de 16 anos')
        except Exception: erros.append('Data de nascimento inválida')
        if municipio_id:
            try: municipio_id=int(municipio_id)
            except Exception: municipio_id=None
        if not municipio_id: erros.append('Município obrigatório')

        if erros:
            for e in erros: flash(e,'danger')
            return render_template('user/perfil.html', ufs=ufs, form=request.form)

        u.email = email
        u.nome_completo = nome
        u.rg_numero = rg_num
        u.rg_orgao = rg_org
        u.rg_uf = rg_uf
        u.data_nascimento = dn
        u.titulo_eleitoral = titulo
        u.zona_eleitoral = zona
        u.secao_eleitoral = secao
        u.cep = cep
        u.uf = uf
        u.municipio_id = municipio_id
        u.bairro = bairro
        u.logradouro = logradouro
        u.numero = numero
        u.complemento = complemento
        if senha:
            u.password_hash = generate_password_hash(senha)
        db.session.commit()
        flash('Perfil atualizado com sucesso.', 'success')
        return redirect(url_for('user.perfil'))
    return render_template('user/perfil.html', ufs=ufs, form=None)