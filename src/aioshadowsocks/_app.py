"""Flask application for aioshadowsocks.

The wiring a blueprint cannot express lives here: an absolute template folder so render_template()
resolves from any working directory, an instance folder that exists before
Flask-SQLAlchemy resolves the relative sqlite path, and the dashboard route that
feeds templates/index.html from real query results.
"""

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from . import paths
from .models import SSUser, db
from .ss.api import bp

paths.ensure_runtime_dirs()


def build_app():
    """Build the application: configuration, database, then routes."""
    app = Flask(
        __name__, template_folder=str(paths.TEMPLATES_DIR), instance_path=str(paths.INSTANCE_DIR)
    )
    app.secret_key = "aioshadowsocks-dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(paths.INSTANCE_DIR / "ss.db")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(bp)

    @app.get("/")
    def index():
        users = SSUser.query.order_by(SSUser.port).all()
        totals = {
            "count": len(users),
            "active": sum(1 for u in users if u.enable),
            "bytes": sum((u.up_bytes or 0) + (u.down_bytes or 0) for u in users),
        }
        return render_template("index.html", users=users, totals=totals)

    @app.post("/users")
    def user_add():
        """HTML form handler.  The JSON equivalent is POST {{ /api/users }}."""
        u = SSUser(
            port=request.form.get("port", type=int) or 8388,
            password=request.form.get("password", ""),
            method=request.form.get("method") or "aes-256-gcm",
            total_bytes=request.form.get("traffic", type=int) or 0,
        )
        db.session.add(u)
        db.session.commit()
        flash("created user u%d on port %s" % (u.id, u.port))
        return redirect(url_for("index"))

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "users": SSUser.query.count()})

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000)

    return app


app = build_app()
