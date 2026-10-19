<p align="center">
  <img src="docs/assets/screens/root.png" alt="sockrelay running" width="900">
</p>

<h1 align="center">sockrelay</h1>

<p align="center"><b>An async Shadowsocks server with a CLI-first operator surface.</b></p>

<p align="center">
  <a href="https://github.com/scar8969/sockrelay/actions/workflows/ci.yml"><img src="https://github.com/scar8969/sockrelay/actions/workflows/ci.yml/badge.svg" alt="ci"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-24%20passed-2ea44f" alt="tests: 24 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-64.4%-yellow" alt="coverage: 64.4%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-8%20live-0969da" alt="routes: 8 live"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

sockrelay is a Shadowsocks server built on asyncio with per-user ports, per-user traffic accounting and an HTTP surface for the numbers an operator needs: who exists, what they moved, and whether the relay is healthy.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [CLI](#cli) &nbsp;·&nbsp; [Configuration](#configuration) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [How a request flows](#how-a-request-flows) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Development](#development) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

## Why this exists

The reference implementations are configuration files plus a daemon with no accounting. This one keeps users in a database, counts bytes per user, and exposes the counters without asking you to parse a log.

## What it does

| Capability | How it works |
| --- | --- |
| **asyncio relay** | One event loop, one task per connection, AEAD ciphers via the cryptography package. |
| **Per-user accounting** | Up and down byte counters per account, updated as traffic flows. |
| **Operator CLI** | user add, user list and run, so provisioning does not need a database client. |
| **Stats endpoint** | GET /api/stats reports users, ports and totals; POST /api/users provisions. |

## Quickstart

```sh
git clone https://github.com/scar8969/sockrelay.git
cd sockrelay
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python wsgi.py                                 # http://127.0.0.1:8000
```

It is up when this answers:

```sh
curl -s http://127.0.0.1:8000/api/stats
```

## Screenshots

Captured from the running service with headless Chromium at 1440×900, one image per page, committed under [`docs/assets/screens/`](docs/assets/screens/).

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/healthz.png" alt="/healthz" width="100%"><br><sub><code>/healthz</code> &middot; 8.3 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/livez.png" alt="/livez" width="100%"><br><sub><code>/livez</code> &middot; 7.3 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/metrics.png" alt="/metrics" width="100%"><br><sub><code>/metrics</code> &middot; 14.8 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/readyz.png" alt="/readyz" width="100%"><br><sub><code>/readyz</code> &middot; 7.7 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/version.png" alt="/version" width="100%"><br><sub><code>/version</code> &middot; 29.1 KB</sub></td>
</tr>
</table>

## API

Every route below is declared in [`openapi/sockrelay.yaml`](openapi/sockrelay.yaml) and exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/api/users` | add user |
| `GET` | `/api/stats` | stats |

## CLI

The same operations without an HTTP client. Installed as `sockrelay`, and runnable from a checkout with no install:

```sh
python -m aioshadowsocks.cli --help
```

```text
usage: ss-server [-h] {run,user} ...

positional arguments:
  {run,user}
    run       start the asyncio shadowsocks server
    user      manage ss_users rows

options:
  -h, --help  show this help message and exit
```

## Configuration

Environment only — there is no config file. Copy `.env.example` to `.env` and edit; `APP_ENV=production` refuses to start without `SECRET_KEY`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `APP_ENV` | `development` | development \| staging \| production; production enforces the secret. |
| `SECRET_KEY` | `change-me-in-production` | Session/CSRF signing key. Required when APP_ENV=production. |
| `HOST` | `0.0.0.0` | Interface the dev server binds. |
| `PORT` | `8000` | Port the dev server and the container listen on. |
| `DEBUG` | `false` | Flask debug mode. Never true in production. |
| `MAX_CONTENT_LENGTH` | `8388608` | Largest accepted request body, in bytes. |
| `DATA_DIR` | `(empty)` | Where uploaded and generated files live. |
| `INSTANCE_DIR` | `(empty)` | Where the SQLite file and instance state live. |
| `LOG_DIR` | `(empty)` | Where rotated log files are written, if file logging is on. |
| `LOG_LEVEL` | `INFO` | DEBUG \| INFO \| WARNING \| ERROR. |
| `LOG_JSON` | `true` | true emits one JSON object per line; false is human-readable. |
| `REQUEST_ID_HEADER` | `X-Request-ID` | Header echoed on every response and stamped on every log line. |

## Measured, not estimated

Produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **24 / 24 passed** (2.6 s, exit 0) |
| Line coverage | **64.4%** — 391 of 586 statements |
| Source | 16 files / 1,333 lines |
| Test code | 4 files / 238 lines |
| Documented paths | 2 in the spec, 1 GET |
| Live probe | 8 GET requests to the booted app, **8 answered 200** |
| Median latency | **15.0 ms** (single uncached request, dev server) |
| Slowest / fastest | 153.2 ms `/api/health` / 3.3 ms `/healthz` |
| Bytes served | 6.2 KB across 8 responses |
| Screenshots | 6 captured |

## How a request flows

```text
client
  │  HTTP
  ▼
wsgi.py ──▶ aioshadowsocks/app.py:get_app()
                │  reads config once (aioshadowsocks/config.py)
                │  registers the `ss` blueprint
                ▼
           route handler
             ├──▶ aioshadowsocks/models.py        tables, via Flask-SQLAlchemy
             ├──▶ aioshadowsocks/errors.py        raises typed errors → one JSON envelope
             └──▶ aioshadowsocks/observability.py JSON log line + X-Request-ID
```

Every response carries `X-Request-ID`, and the matching log line is written once at the end of the request with the status and duration, so a report of "it failed" is one `grep` away from the traceback.

## Architecture

```
sockrelay/
├── src/aioshadowsocks/
│   ├── http.py                         379  HTTP plumbing for aioshadowsocks: correlation ids, a
│   ├── observability.py                169  Structured logging and request correlation for aiosh
│   ├── config.py                       168  Environment-driven configuration for aioshadowsocks
│   ├── app.py                          119  Application factory for aioshadowsocks
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── cli.py                           88  
│   ├── _app.py                          65  Flask application for aioshadowsocks
│   ├── ss/server.py                     60  
│   ├── paths.py                         52  Filesystem layout for aioshadowsocks
│   ├── ss/api.py                        36  
│   ├── ss/accounting.py                 26  
│   ├── ss/ciphers.py                    20  
├── openapi/sockrelay.yaml                 the contract of record
├── schema/sockrelay.sql                   the DDL
├── tests/                       the suite that has to stay green
├── docs/EVIDENCE.md             the recorded live route walk
├── Dockerfile                   multi-stage build
└── wsgi.py                      entry point
```

The package keeps one shape across the service: `config.py` reads the environment once, `observability.py` emits structured JSON logs carrying a request id, `errors.py` turns exceptions into a single JSON envelope, `models.py` holds the tables, and the `ss/` package holds the routes.

## Quality gates

| Gate | Command | Threshold |
| --- | --- | --- |
| Suite | `pytest -q` | all green |
| Coverage | `pytest --cov` | floor in `pyproject.toml`, set below the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 on every push to `main`, plus a container build — [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Development

```sh
pip install -e ".[dev]"
python -m pytest -q                      # the suite
python -m pytest --cov                   # with the coverage floor
python -m ruff check src tests           # lint
python -m ruff format --check src tests  # formatting
python -m mypy src                       # types
python -m bandit -c pyproject.toml -r src  # security
pre-commit install                       # the same checks on commit
```

Dependabot opens grouped PRs for the dev tooling weekly and for actions and the base image monthly.

## Deploy

```sh
docker build -t sockrelay .
docker run --rm -p 8000:8000 --env-file .env.example sockrelay
```

A `docker-compose.yml` is included for a local run with a volume for the SQLite file. The image runs as a non-root user and serves through gunicorn.

## Limits, stated rather than hidden

- Single-process relay; there is no multi-node coordination.
- Accounting is in-memory per user row and flushed on write, so a hard kill can lose the last interval.

## License

MIT — see [LICENSE](LICENSE).
