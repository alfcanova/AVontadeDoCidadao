from datetime import datetime, date
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..models.user import User
from ..models.lgpd import LgpdConsent
from ..models.audit import AuditLog
from ..utils.security import hmac_ip, cpf_hash, mask_cpf
from ..utils.validators import calc_idade, is_cpf_valid_digits, TITULO_RE, ZONA_RE, SECAO_RE, CEP_RE
from ..config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        ident = request.form.get('ident','').strip()
        senha = request.form.get('senha','')
        user = User.query.filter((User.username==ident)|(User.email==ident)).first()
        if not user or not check_password_hash(user.password_hash, senha) or not user.is_active:
            flash('Credenciais inválidas ou usuário inativo', 'danger')
            return redirect(url_for('auth.login'))
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        login_user(user)
        if user.must_change_password:
            flash('Altere sua senha no primeiro acesso', 'warning')
            return redirect(url_for('auth.change_password'))
        return redirect(url_for('main.index'))
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    from ..models.ibge import IbgeUf
    ufs = IbgeUf.query.order_by(IbgeUf.sigla).all()
    if request.method=='POST':
        username = request.form.get('username','').strip().lower()
        email = request.form.get('email','').strip().lower()
        senha = request.form.get('senha','')
        nome = request.form.get('nome_completo','').strip()
        cpf = ''.join(re.findall(r'\d', request.form.get('cpf','')))
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
        consent = request.form.get('lgpd_consent')=='on'

        erros=[]
        if User.query.filter_by(username=username).first(): erros.append('Usuário já existe')
        if User.query.filter_by(email=email).first(): erros.append('E-mail já cadastrado')
        if not is_cpf_valid_digits(cpf): erros.append('CPF inválido')
        if User.query.filter_by(cpf_hash=cpf_hash(cpf)).first(): erros.append('CPF já cadastrado')
        if not TITULO_RE.match(titulo): erros.append('Título eleitoral inválido')
        if User.query.filter_by(titulo_eleitoral=titulo).first(): erros.append('Título já cadastrado')
        if not ZONA_RE.match(zona): erros.append('Zona inválida')
        if not SECAO_RE.match(secao): erros.append('Seção inválida')
        if not CEP_RE.match(cep): erros.append('CEP inválido')
        try:
            dn = date.fromisoformat(dn_str)
            if calc_idade(dn) < 16: erros.append('Deve ser maior de 16 anos')
        except Exception: erros.append('Data de nascimento inválida')
        if not consent: erros.append('Consentimento LGPD obrigatório')
        if municipio_id:
            try: municipio_id=int(municipio_id)
            except Exception: municipio_id=None
        if not municipio_id: erros.append('Município obrigatório')

        if erros:
            for e in erros: flash(e,'danger')
            return render_template('auth/register.html', ufs=ufs, form=request.form)

        user = User(
            username=username,email=email,
            password_hash=generate_password_hash(senha),
            role='user', is_active=True, must_change_password=False,
            nome_completo=nome,
            cpf_hash=cpf_hash(cpf), cpf_mask=mask_cpf(cpf),
            rg_numero=rg_num, rg_orgao=rg_org, rg_uf=rg_uf,
            data_nascimento=dn,
            titulo_eleitoral=titulo, zona_eleitoral=zona, secao_eleitoral=secao,
            cep=cep, uf=uf, municipio_id=municipio_id,
            bairro=bairro, logradouro=logradouro, numero=numero, complemento=complemento
        )
        db.session.add(user)
        db.session.flush()
        c = LgpdConsent(
            user_id=user.id, actor_type='user',
            ip_hash=hmac_ip(request.remote_addr),
            user_agent=request.headers.get('User-Agent','')[:255],
            consent_version=Config.LGPD_CONSENT_VERSION,
            legal_link_used=Config.LGPD_INTEGRAL_LINK,
            consented_at=datetime.utcnow(), created_at=datetime.utcnow()
        )
        db.session.add(c)
        db.session.add(AuditLog(actor_id=user.id, actor_role='user', action='user.register', entity='user', entity_id=user.id, ip_hash=hmac_ip(request.remote_addr), metadata={'email':email}))
        db.session.commit()
        flash('Cadastro realizado com sucesso. Faça login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', ufs=ufs)

@auth_bp.route('/change-password', methods=['GET','POST'])
@login_required
def change_password():
    if request.method=='POST':
        nova = request.form.get('nova','')
        conf = request.form.get('conf','')
        if len(nova)<4 or nova!=conf:
            flash('Senhas não conferem ou muito curta', 'danger')
            return render_template('auth/change_password.html')
        current_user.password_hash = generate_password_hash(nova)
        current_user.must_change_password = False
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Senha alterada', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/change_password.html')

@auth_bp.route('/consent-lgpd')
@login_required
def consent_lgpd():
    return render_template('auth/consent_lgpd.html')
