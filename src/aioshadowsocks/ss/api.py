from flask import Blueprint, jsonify, request

from ..models import SSUser, db

bp = Blueprint("ss", __name__)


@bp.post("/api/users")
def add_user():
    d = request.get_json(force=True, silent=True) or {}
    u = SSUser(
        port=d.get("port", 8388),
        password=d.get("password", ""),
        method=d.get("method", "aes-256-gcm"),
        total_bytes=d.get("traffic", 0),
    )
    db.session.add(u)
    db.session.commit()
    return jsonify({"id": u.id})


@bp.get("/api/stats")
def stats():
    users = SSUser.query.all()
    return jsonify(
        {
            "users": len(users),
            "active": sum(1 for u in users if u.enable),
            "today_bytes": sum(u.up_bytes + u.down_bytes for u in users),
            "per_user": [
                {"username": f"u{u.id}", "port": u.port, "up": u.up_bytes, "down": u.down_bytes}
                for u in users
            ],
        }
    )
