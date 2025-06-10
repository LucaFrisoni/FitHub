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

def convert_value(value, target_type):
    """Convierte el valor al tipo especificado"""
    from datetime import datetime
    
    try:
        if target_type == int:
            return int(value)
        elif target_type == str:
            return str(value)
        elif target_type == datetime:
            # Solo formato ISO: 2024-12-25T14:30:00 o 2024-12-25T14:30:00Z
            try:
                # Primero intentar con Z (UTC)
                if value.endswith('Z'):
                    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
                else:
                    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                return None
        else:
            return value
    except (ValueError, TypeError):
        return None