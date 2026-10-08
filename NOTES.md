== curl ==
# POST /api/users  {"port":8390,"password":"x","method":"aes-256-gcm","traffic":10737418240}
# GET  /api/stats
# CLI: ss-server run --config config.json
# CLI: ss-server user add 8388 mypassword --method aes-256-gcm

== session plan ==
# Session 1: ciphers (AEAD vectors) + header parse → tests
# Session 2: TCP relay loopback + multi-user auth → tests
# Session 3: UDP + accounting + deploy (systemd/Docker) → README → tag
