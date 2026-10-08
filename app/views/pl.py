from flask import Blueprint, render_template
pl_bp = Blueprint('pl', __name__)

@pl_bp.route('/')
def listar():
    return render_template('pl/listar.html')
