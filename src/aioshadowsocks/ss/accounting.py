from ..models import SSUser, db

class TrafficCounter:
    def __init__(self):
        self._buf = {}

    def add(self, user_id: int, up: int, down: int) -> None:
        row = self._buf.setdefault(user_id, [0, 0])
        row[0] += up
        row[1] += down

    def flush(self) -> None:
        """Write buffer to DB."""
        if not self._buf:
            return
        for user_id, (up, down) in list(self._buf.items()):
            user = db.session.get(SSUser, user_id)
            if user is None:
                continue
            user.up_bytes = (user.up_bytes or 0) + up
            user.down_bytes = (user.down_bytes or 0) + down
            user.total_bytes = (user.total_bytes or 0) + up + down
        db.session.commit()
        self._buf.clear()
