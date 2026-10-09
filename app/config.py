import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    APP_NAME = os.getenv('APP_NAME', 'A VONTADE DO CIDADÃO: essa é a lei!')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "db", "tables.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LGPD_CONSENT_VERSION = os.getenv('LGPD_CONSENT_VERSION', '1.0.0')
    LGPD_INTEGRAL_LINK = 'https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm'
    LGPD_SUMMARY = (
        'Resumo aplicável ao A VONTADE DO CIDADÃO: essa é a lei!: '
        'coleta-se dados mínimos para cadastro, comprovação de elegibilidade (maior de 16 anos e título de eleitor), '
        'endereço, dados pessoais/eleitorais necessários à submissão e assinatura de Projeto de Lei de Iniciativa Popular, '
        'podendo ser: assinatura física, pelo sistema gov.br e digital no sistema.'
    )
    CEP_LOOKUP_URL = os.getenv('CEP_LOOKUP_URL', 'https://viacep.com.br/ws')
    QUORUM_PERCENTUAIS = {
        'federal': 0.01,
        'estadual': 0.02,
        'municipal': 0.05,
    }
    TSE_CROSSWALK_URL = os.getenv(
        'TSE_CROSSWALK_URL',
        'https://cdn.tse.jus.br/estatistica/sead/odsele/municipio_tse_ibge/municipio_tse_ibge.zip'
    )
    TSE_ELEITORADO_URL_TEMPLATE = os.getenv(
        'TSE_ELEITORADO_URL_TEMPLATE',
        'https://cdn.tse.jus.br/estatistica/sead/odsele/perfil_eleitor_secao/perfil_eleitor_secao_ATUAL_{uf}.zip'
    )
    TSE_CACHE_DIAS = int(os.getenv('TSE_CACHE_DIAS', '30'))
    TSE_FETCH_TIMEOUT = int(os.getenv('TSE_FETCH_TIMEOUT', '600'))
    TSE_AUTO_FETCH = os.getenv('TSE_AUTO_FETCH', '1') == '1'
    CSS_DIR = os.path.join(BASE_DIR, 'css')
    DOCS_DIR = os.path.join(BASE_DIR, 'docs')
    DB_DIR = os.path.join(BASE_DIR, 'db')
    YEAR = datetime.now().year

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False

config = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'default': DevConfig
}
