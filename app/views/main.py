from flask import Blueprint, render_template
from sqlalchemy import func
from .. import db
from ..models.pl import PlDeIp
from ..models.user import User
from ..models.assinatura import Assinatura

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    total_pl = db.session.query(func.count(PlDeIp.id)).scalar() or 0
    total_mun = db.session.query(func.count(PlDeIp.id)).filter(PlDeIp.escopo=='municipal').scalar() or 0
    total_est = db.session.query(func.count(PlDeIp.id)).filter(PlDeIp.escopo=='estadual').scalar() or 0
    total_fed = db.session.query(func.count(PlDeIp.id)).filter(PlDeIp.escopo=='federal').scalar() or 0
    total_users = db.session.query(func.count(User.id)).scalar() or 0
    total_ass = db.session.query(func.count(Assinatura.id)).scalar() or 0
    em_votacao = db.session.query(func.count(PlDeIp.id)).filter(PlDeIp.status=='em_votacao').scalar() or 0
    encerrados = db.session.query(func.count(PlDeIp.id)).filter(PlDeIp.status.in_(['concluido','reprovado','arquivado'])).scalar() or 0
    ativos = PlDeIp.query.filter(PlDeIp.status=='em_votacao').order_by(PlDeIp.created_at.desc()).limit(10).all()
    return render_template('index.html',
        total_pl=total_pl,
        total_mun=total_mun, total_est=total_est, total_fed=total_fed,
        total_users=total_users,
        total_ass=total_ass,
        em_votacao=em_votacao,
        encerrados=encerrados,
        ativos=ativos
    )
