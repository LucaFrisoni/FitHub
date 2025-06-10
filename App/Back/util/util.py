from datetime import datetime
import bcrypt

def obtener_fecha(iso_str: str) -> datetime:
    return datetime.fromisoformat(iso_str)


def encryptar_pwd(passwd: str) -> str: 
    return bcrypt.hashpw(passwd.encode(), bcrypt.gensalt()).decode()

def check_pwd(passwd: str, hashed: str) -> bool: 
    return bcrypt.checkpw(passwd.encode(), hashed.encode())

def is_type(obj, required_type) -> bool:
    """
    ESte metodo se usa porque en las request HTTP, 
    todo es casteado a 'string'
    """ 
    try:
        if required_type == int:
            int(obj)
        elif required_type == str:
            str(obj)
        return True
    except Exception as e:
        return False