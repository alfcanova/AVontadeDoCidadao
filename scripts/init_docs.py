import os,sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.config import Config
os.makedirs(Config.DOCS_DIR, exist_ok=True)
for name in ['politica_privacidade.md','termos_uso.md','politica_cookies.md']:
    p=os.path.join(Config.DOCS_DIR,name)
    if not os.path.exists(p):
        with open(p,'w',encoding='utf-8') as f:
            f.write(f'# {name.replace(".md","").replace("_"," ").title()}\nEm breve\n')
print('docs ok')
