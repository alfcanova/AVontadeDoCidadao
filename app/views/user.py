from flask import Blueprint, render_template
user_bp = Blueprint('user', __name__)

@user_bp.route('/perfil')
def perfil():
    return render_template('user/perfil.html')
