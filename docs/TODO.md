# TODO - AVontadeDoCidadao

## 1. Objetivo
Sistema web para cadastro, submissão, assinatura e tramitação de Projetos de Lei de Iniciativa Popular (PLdeIP).

## 2. Requisitos Gerais
- Nome: AVontadeDoCidadao
- Raiz: D:\Projetos\AVontadeDoCidadao
- Banco: db/tables.db (SQLite + WAL + FK ON)
- Admin: user=admin / senha=@dmin123! (troca obrigatória no 1º login)
- Auto-cadastro: maior de 16 anos E possuir Título de Eleitor
- LGPD: consentimento obrigatório, resumo fixo, link integral Lei 13.709/2018, políticas internas em docs/
- CSS em css/ (seleção por usuário). Upload APENAS pelo Admin
- Assinaturas: digital_sistema, digital_govbr, física (PDF)
- IBGE: UFs + Municípios + Distritos (PL municipal = Município SEDE)
- Quóruns: por Município/Estado/Federação. Carregar IMEDIATAMENTE após definir escopo.

## 3. Index.html (header + footer + login/cadastro + dashboard)
### Header
- Nome, data/hora dinâmicos (JS setInterval), links, Entrar/Cadastrar
### Body
- Login OU Cadastro (tabs)
- Dashboard: total PL, por escopo (municipal/estadual/federal), total usuários, por status, total assinaturas, em votação x encerrados, % atingiram quórum, últimos abertos
### Footer
- Links LGPD + políticas internas + copyright © ano atual

## 4. Modelos Chave
- users (dados pessoais + endereço + eleitorais + idade>=16)
- ibge_ufs/municipios/distritos
- quoruns_assinaturas (escopo, uf_id, municipio_id, qtd_minima, vigente)
- pl_de_ip (escopo, uf_id, municipio_id, status, assinaturas_minimas_definidas, quorum_alvo_id)
- restricoes_legais (escopos_alvo JSON)
- assinaturas (3 tipos)
- css_files + user_css_preferences + audit_logs + lgpd_consents

## 5. Admin
Disponibilizar p/ votação, retirar, processo de conclusão (verificar quórum) -> concluir p/ autoridades ou reprovar, arquivar. CRUD quóruns/restrições. Upload CSS.

## 6. API
/api/ufs, /api/municipios, /api/municipios/<id>/distritos, /api/quorum

## 7. Roadmap
- [x] Base (config/models/views/templates/static/scripts)
- [ ] CRUD Quóruns (admin)
- [ ] PLdeIP completo (criar/editar/submeter + quórum dinâmico)
- [ ] Fluxo votação/conclusão
- [ ] Assinatura digital_sistema + PDF físico
- [ ] Ajustes finos

