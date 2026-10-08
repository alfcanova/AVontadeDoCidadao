from flask import Blueprint, render_template
from ..decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@admin_required
def index():
    return render_template('admin/index.html')
