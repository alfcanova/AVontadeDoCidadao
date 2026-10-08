import re
from datetime import date

CPF_RE = re.compile(r'^\d{11}$')
TITULO_RE = re.compile(r'^\d{4,12}$')
ZONA_RE = re.compile(r'^\d{1,4}$')
SECAO_RE = re.compile(r'^\d{1,4}$')
CEP_RE = re.compile(r'^\d{8}$')

def calc_idade(dn: date) -> int:
    today = date.today()
    return today.year - dn.year - ((today.month, today.day) < (dn.month, dn.day))

def is_cpf_valid_digits(digits: str) -> bool:
    if not CPF_RE.match(digits):
        return False
    if len(set(digits)) == 1:
        return False
    def dv(s):
        n = 0
        for i,c in enumerate(s):
            n += int(c)*(len(s)+1-i)
        r = 11 - n%11
        return '0' if r>=10 else str(r)
    d1 = dv(digits[:9])
    d2 = dv(digits[:9]+d1)
    return digits[-2:] == d1+d2
