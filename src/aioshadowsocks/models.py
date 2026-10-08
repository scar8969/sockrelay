from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SSUser(db.Model):
    __tablename__ = "ss_users"
    id = db.Column(db.Integer, primary_key=True)
    port = db.Column(db.Integer, unique=True)
    password = db.Column(db.String(64), default="")
    method = db.Column(db.String(32), default="aes-256-gcm")
    up_bytes = db.Column(db.BigInteger, default=0)
    down_bytes = db.Column(db.BigInteger, default=0)
    total_bytes = db.Column(db.BigInteger, default=0)
    enable = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
