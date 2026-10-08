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
        'endereço, dados pessoais/eleitorais necessários à submissão e assinatura de PLdeIP (digital no sistema, gov.br ou física). '
        'Usa-se minimização, mascaramento, hash de CPF e hash de IP. '
        'Links para Lei 13.709/2018 e políticas internas.'
    )
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
