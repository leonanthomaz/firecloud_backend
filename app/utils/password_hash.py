import bcrypt

def hash_password(password: str) -> str:
    """Gera um hash da senha usando bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')