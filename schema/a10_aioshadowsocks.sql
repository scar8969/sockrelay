-- 🚀 aioshadowsocks schema
CREATE TABLE ss_users(id INTEGER PRIMARY KEY, port INTEGER UNIQUE, password TEXT, method TEXT DEFAULT 'aes-256-gcm', up_bytes INTEGER DEFAULT 0, down_bytes INTEGER DEFAULT 0, total_bytes INTEGER DEFAULT 0, enable INTEGER DEFAULT 1, created_at DATETIME);
