from ..models import SSUser

def find_user(port: int) -> SSUser:
    return SSUser.query.filter_by(port=port, enable=1).first()
