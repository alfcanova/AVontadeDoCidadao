import hashlib
import hmac
import os

def hmac_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    key = os.getenv('IP_HMAC_KEY', 'dev-ip-hmac-key').encode('utf-8')
    return hmac.new(key, ip.encode('utf-8'), hashlib.sha256).hexdigest()

def cpf_hash(cpf_digits: str) -> str:
    return hashlib.sha256(cpf_digits.encode('utf-8')).hexdigest()

def mask_cpf(cpf_digits: str) -> str:
    if not cpf_digits or len(cpf_digits) != 11:
        return '***.***.***-**'
    return f'***.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:11]}'
