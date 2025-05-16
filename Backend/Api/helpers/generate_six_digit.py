import secrets

def generate_code():
    code = ''.join(str(secrets.randbelow(10)) for _ in range(6))
    return code