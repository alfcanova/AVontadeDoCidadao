import os
import hashlib
from flask import Blueprint, send_from_directory, abort, current_app, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..decorators import admin_required
from .. import db
from ..models.css import UserCssPreference, CssFile
from ..models.audit import AuditLog
from ..utils.security import hmac_ip

css_bp = Blueprint('css', __name__)

@css_bp.route('/css/<path:filename>')
@login_required
def serve_css(filename):
    safe = secure_filename(filename)
    cssdir = current_app.config['CSS_DIR']
    full = os.path.realpath(os.path.join(cssdir, safe))
    if not full.startswith(os.path.realpath(cssdir)) or not safe.endswith('.css') or not os.path.exists(full):
        abort(404)
    return send_from_directory(cssdir, safe)

@css_bp.route('/user/theme', methods=['POST'])
@login_required
def set_theme():
    fname = request.form.get('css_filename','')
    safe = secure_filename(fname)
    if not safe or not safe.endswith('.css'): abort(400)
    pref = UserCssPreference.query.filter_by(user_id=current_user.id).first()
    if not pref: pref = UserCssPreference(user_id=current_user.id)
    pref.css_filename = safe
    db.session.add(pref); db.session.commit()
    flash('Tema aplicado', 'success')
    return redirect(request.referrer or url_for('main.index'))

@css_bp.route('/admin/css/upload', methods=['GET','POST'])
@admin_required
def upload_css():
    if request.method=='POST':
        f = request.files.get('file')
        if not f or not f.filename: flash('Arquivo inválido','danger'); return redirect(url_for('css.upload_css'))
        safe = secure_filename(f.filename)
        if not safe.endswith('.css'): flash('Apenas .css','danger'); return redirect(url_for('css.upload_css'))
        cssdir = current_app.config['CSS_DIR']
        path = os.path.join(cssdir, safe)
        if os.path.exists(path):
            flash('Arquivo já existe. Renomeie antes de enviar.', 'warning')
            return redirect(url_for('css.upload_css'))
        f.save(path)
        with open(path,'rb') as fh:
            h = hashlib.sha256(fh.read()).hexdigest()
        cf = CssFile(filename=safe, original_filename=f.filename, size_bytes=os.path.getsize(path), uploaded_by=current_user.id, sha256=h)
        db.session.add(cf)
        db.session.add(AuditLog(actor_id=current_user.id, actor_role='admin', action='css.upload', entity='css', entity_id=cf.id, ip_hash=hmac_ip(request.remote_addr), metadata={'file':safe}))
        db.session.commit()
        flash('CSS enviado', 'success')
        return redirect(url_for('css.upload_css'))
    from os import listdir
    files = sorted([x for x in os.listdir(current_app.config['CSS_DIR']) if x.endswith('.css')])
    return render_template('admin/css_upload.html', files=files)
