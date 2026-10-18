import argparse
import asyncio
import json

from . import paths


def _db():
    """Open the SQLite session lazily.

    models.py imports Flask-SQLAlchemy, which is an install-time dependency of the
    server, not of `--help`: building the parser must work on a bare interpreter.
    """
    from flask import Flask

    from .models import db

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(paths.INSTANCE_DIR / "ss.db")
    db.init_app(app)
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    return db


def cmd_run(args):
    # Imported here, not at module level: ss.server and ss.accounting reach
    # models.py -> Flask-SQLAlchemy, which must not be needed for `--help`.
    from .ss.accounting import TrafficCounter
    from .ss.server import ShadowSocksServer

    with open(args.config) as f:
        cfg = json.load(f)
    counter = TrafficCounter()
    server = ShadowSocksServer(cfg.get("host", "0.0.0.0"), cfg.get("port", 8388), counter)
    print(f"[ss] listening {cfg.get('host', '0.0.0.0')}:{cfg.get('port', 8388)}")
    asyncio.run(server.start())
    return 0


def cmd_user_add(args):
    from .models import SSUser

    db = _db()
    u = SSUser(port=args.port, password=args.password, method=args.method)
    db.session.add(u)
    db.session.commit()
    print(f"user {args.port} added")
    return 0


def cmd_user_list(_args):
    from .models import SSUser

    db = _db()
    for u in SSUser.query.order_by(SSUser.port).all():
        state = "on" if u.enable else "off"
        print(f"{u.port:<6} {u.method:<22} {u.up_bytes + u.down_bytes:>12} bytes  {state}")
    return 0


def main():
    p = argparse.ArgumentParser(prog="ss-server")
    sub = p.add_subparsers(dest="cmd")
    r = sub.add_parser("run", help="start the asyncio shadowsocks server")
    r.add_argument("--config", default="config.json")
    u = sub.add_parser("user", help="manage ss_users rows")
    us = u.add_subparsers(dest="sub")
    a = us.add_parser("add", help="add a user")
    a.add_argument("port", type=int)
    a.add_argument("password")
    a.add_argument("--method", default="aes-256-gcm")
    us.add_parser("list", help="list users")
    args = p.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "user" and args.sub == "add":
        return cmd_user_add(args)
    if args.cmd == "user" and args.sub == "list":
        return cmd_user_list(args)
    p.print_help()
    return 1
