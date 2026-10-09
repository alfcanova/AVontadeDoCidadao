import csv
import io
import math
import threading
import zipfile
from datetime import datetime, timedelta

import requests
from flask import current_app

from .. import db
from ..models.tse import EleitoradoTse

_crosswalk = None
_crosswalk_lock = threading.Lock()
_em_andamento = set()
_agenda_lock = threading.Lock()


def percentual(escopo):
    return current_app.config.get('QUORUM_PERCENTUAIS', {}).get(escopo)


def _cache_valido(reg):
    if not reg or not reg.coletado_em:
        return False
    dias = current_app.config.get('TSE_CACHE_DIAS', 30)
    return (datetime.utcnow() - reg.coletado_em) < timedelta(days=dias)


def obter_registro(escopo, uf_sigla=None, codigo_ibge=None):
    q = EleitoradoTse.query.filter_by(escopo=escopo)
    if escopo == 'municipal':
        q = q.filter_by(uf_sigla=uf_sigla, codigo_ibge=codigo_ibge)
    elif escopo == 'estadual':
        q = q.filter_by(uf_sigla=uf_sigla)
    return q.first()


def calcular(escopo, uf_sigla=None, codigo_ibge=None):
    pct = percentual(escopo)
    if pct is None:
        return {'escopo': escopo, 'percentual': None, 'qtd_eleitores': None,
                'qtd_assinaturas': None, 'coletado_em': None, 'fonte': None}
    reg = obter_registro(escopo, uf_sigla, codigo_ibge)
    if not _cache_valido(reg):
        agendar_atualizacao(uf_sigla if escopo != 'federal' else None)
    eleitores = reg.qtd_eleitores if reg else None
    assinaturas = int(math.ceil(eleitores * pct)) if (eleitores and pct) else None
    return {
        'escopo': escopo,
        'percentual': pct,
        'qtd_eleitores': eleitores,
        'qtd_assinaturas': assinaturas,
        'coletado_em': reg.coletado_em.isoformat() if reg else None,
        'fonte': reg.fonte if reg else None,
    }


def agregar_por_municipio(rows):
    total = {}
    for r in rows:
        code = r.get('CD_MUNICIPIO')
        qt = r.get('QT_ELEITORES')
        if code is None or qt is None:
            continue
        try:
            code = int(str(code).strip())
            qt = int(str(qt).strip())
        except (TypeError, ValueError):
            continue
        total[code] = total.get(code, 0) + qt
    return total


def _baixar_zip_bytes(url):
    resp = requests.get(
        url,
        timeout=current_app.config.get('TSE_FETCH_TIMEOUT', 600),
        headers={'User-Agent': 'AVontadeDoCidadao/1.0'},
        stream=True,
    )
    resp.raise_for_status()
    buf = io.BytesIO()
    for chunk in resp.iter_content(chunk_size=1024 * 256):
        if chunk:
            buf.write(chunk)
    buf.seek(0)
    return buf


def _primeiro_csv(zf):
    for name in zf.namelist():
        if name.lower().endswith('.csv'):
            return name
    raise ValueError('CSV não encontrado no arquivo do TSE')


def _dicionario_crosswalk():
    global _crosswalk
    with _crosswalk_lock:
        if _crosswalk is not None:
            return _crosswalk
        buf = _baixar_zip_bytes(current_app.config['TSE_CROSSWALK_URL'])
        mapa = {}
        with zipfile.ZipFile(buf) as zf:
            with zf.open(_primeiro_csv(zf)) as fh:
                reader = csv.DictReader(io.TextIOWrapper(fh, encoding='latin-1'), delimiter=';')
                for r in reader:
                    try:
                        tse = int(str(r['CD_MUNICIPIO_TSE']).strip())
                        ibge = int(str(r['CD_MUNICIPIO_IBGE']).strip())
                    except (KeyError, TypeError, ValueError):
                        continue
                    mapa[(r.get('SG_UF', '').upper(), tse)] = ibge
        _crosswalk = mapa
        return _crosswalk


def _upsert(escopo, uf_sigla, codigo_ibge, qtd, fonte):
    reg = obter_registro(escopo, uf_sigla, codigo_ibge)
    if reg is None:
        reg = EleitoradoTse(escopo=escopo, uf_sigla=uf_sigla, codigo_ibge=codigo_ibge)
        db.session.add(reg)
    reg.qtd_eleitores = int(qtd)
    reg.fonte = fonte
    reg.ano_referencia = current_app.config.get('YEAR')
    reg.coletado_em = datetime.utcnow()
    return reg


def atualizar_uf(uf_sigla):
    uf_sigla = (uf_sigla or '').upper()
    if not uf_sigla:
        raise ValueError('UF obrigatória')
    url = current_app.config['TSE_ELEITORADO_URL_TEMPLATE'].format(uf=uf_sigla)
    fonte = f'TSE/perfil_eleitor_secao_ATUAL_{uf_sigla}'
    crosswalk = _dicionario_crosswalk()
    buf = _baixar_zip_bytes(url)
    with zipfile.ZipFile(buf) as zf:
        with zf.open(_primeiro_csv(zf)) as fh:
            reader = csv.DictReader(io.TextIOWrapper(fh, encoding='latin-1'), delimiter=';')
            por_municipio = agregar_por_municipio(reader)
    total_uf = 0
    nao_mapeados = 0
    for tse_code, qt in por_municipio.items():
        total_uf += qt
        codigo_ibge = crosswalk.get((uf_sigla, tse_code))
        if codigo_ibge is None:
            nao_mapeados += 1
            continue
        _upsert('municipal', uf_sigla, codigo_ibge, qt, fonte)
    _upsert('estadual', uf_sigla, None, total_uf, fonte)
    db.session.commit()
    return {'uf': uf_sigla, 'total': total_uf, 'municipios': len(por_municipio), 'nao_mapeados': nao_mapeados}


def atualizar_federal():
    total = db.session.query(
        db.func.coalesce(db.func.sum(EleitoradoTse.qtd_eleitores), 0)
    ).filter_by(escopo='estadual').scalar()
    _upsert('federal', None, None, int(total), 'TSE/agregado_estadual')
    db.session.commit()
    return {'uf': None, 'total': int(total)}


def atualizar_tudo(ufs=None):
    from ..models.ibge import IbgeUf
    siglas = ufs or [u.sigla for u in IbgeUf.query.order_by(IbgeUf.sigla)]
    resumo = []
    for sigla in siglas:
        try:
            resumo.append(atualizar_uf(sigla))
        except Exception as e:
            resumo.append({'uf': sigla, 'erro': str(e)})
    resumo.append(atualizar_federal())
    return resumo


def agendar_atualizacao(uf_sigla=None):
    if not current_app.config.get('TSE_AUTO_FETCH', True):
        return False
    key = uf_sigla or '__all__'
    with _agenda_lock:
        if key in _em_andamento:
            return False
        _em_andamento.add(key)
    app = current_app._get_current_object()

    def worker():
        try:
            with app.app_context():
                if uf_sigla:
                    atualizar_uf(uf_sigla)
                else:
                    atualizar_tudo()
        except Exception:
            pass
        finally:
            with _agenda_lock:
                _em_andamento.discard(key)

    threading.Thread(target=worker, name=f'tse-{key}', daemon=True).start()
    return True
