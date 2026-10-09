import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.services import tse


def main():
    parser = argparse.ArgumentParser(
        description='Importa o eleitorado do TSE (perfil por seção) agregado por município e UF.'
    )
    parser.add_argument('--uf', action='append', default=[],
                        help='Sigla(s) da UF (repetível). Ex: --uf AC --uf SP')
    parser.add_argument('--all', action='store_true',
                        help='Importa todas as UFs e recalcula o total federal')
    args = parser.parse_args()

    if not args.uf and not args.all:
        parser.error('Informe --uf SIGLA (repetível) ou --all')

    app = create_app()
    with app.app_context():
        db.create_all()
        if args.all:
            resumo = tse.atualizar_tudo()
        else:
            resumo = [tse.atualizar_uf(u) for u in args.uf]
            resumo.append(tse.atualizar_federal())
        for item in resumo:
            print(item)


if __name__ == '__main__':
    main()
