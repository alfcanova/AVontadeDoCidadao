# A VONTADE DO CIDADÃO: essa é a lei!

Sistema web para cadastro, submissão, assinatura e tramitação de **Projetos de Lei de Iniciativa Popular (PLdeIP)**.

## Recursos

- **Autenticação** — login, auto-cadastro (maior de 16 anos e Título de Eleitor), troca obrigatória de senha no 1º acesso
- **Dashboard** — métricas de PLdeIP por escopo (municipal/estadual/federal), cidadãos, assinaturas, ativos e encerrados; listagem de projetos ativos
- **LGPD** — consentimento obrigatório, resumo fixo, link da Lei 13.709/2018 e políticas internas (privacidade, uso, cookies)
- **IBGE** — UFs, municípios e distritos para definição de escopo do PL
- **Assinaturas** — digital no sistema, digital gov.br e física (PDF)
- **Painel Admin** — tramitação (disponibilizar para votação, concluir, reprovar, arquivar), CRUD de quóruns/restrições e upload de temas CSS
- **Temas CSS** — seleção pelo usuário; upload apenas pelo admin
- **Auditoria** — log de ações relevantes

## Stack

- Python 3 + Flask 3 (Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate/Alembic)
- SQLite (WAL + foreign keys) em `db/tables.db`
- HTML/Jinja2 + CSS puro + JavaScript vanilla

## Como executar

```bash
pip install -r requirements.txt
python server.py
```

Servidor em `http://127.0.0.1:5000` (modo debug).

Admin padrão: `admin` / `@dmin123!` — troca de senha obrigatória no 1º login.

### Variáveis de ambiente (opcional)

Ver `.env.example`: `APP_NAME`, `SECRET_KEY`, `DATABASE_URL`, `LGPD_CONSENT_VERSION`.

## Estrutura

```
app/
  __init__.py      # create_app, blueprints, context processor
  config.py        # Config/Dev/Prod
  models/          # users, pl_de_ip, assinaturas, ibge, lgpd, css, audit
  views/           # main, auth, user, pl, admin, api, css
  templates/       # Jinja2 (base, index, auth, admin)
  static/          # css, js, docs (políticas)
css/               # temas disponíveis
docs/              # TODO, licença, políticas
scripts/           # seed_admin, init_docs, import_ibge
migrations/        # Alembic
server.py          # dev server
wsgi.py            # entrypoint WSGI
```

## API

| Rota | Descrição |
|---|---|
| `/api/ufs` | Lista UFs |
| `/api/cep/<cep>` | Consulta endereço por CEP (base Correios) |
| `/api/municipios` | Municípios (parâmetro `uf_id`) |
| `/api/municipios/<id>/distritos` | Distritos do município |
| `/api/quorum` | Quórum vigente por escopo |

## Roadmap

- [x] Base (config/models/views/templates/static/scripts)
- [ ] CRUD Quóruns (admin)
- [ ] PLdeIP completo (criar/editar/submeter + quórum dinâmico)
- [ ] Fluxo votação/conclusão
- [ ] Assinatura digital_sistema + PDF físico
- [ ] Ajustes finos

## Licença
Este projeto é desenvolvido para fins de pesquisa e desenvolvimento de linguagens de programação. Consulte a documentação em docs/ para obter detalhes completos da especificação e licença.

       GNU GENERAL PUBLIC LICENSE

Version 3, 29 June 2007 Copyright (C) 2007 Free Software
