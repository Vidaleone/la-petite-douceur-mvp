import sqlite3, json
from flask import current_app, g
from werkzeug.security import generate_password_hash

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'customer',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS products (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL, category TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
 price REAL NOT NULL CHECK(price >= 0), active INTEGER NOT NULL DEFAULT 1,
 ingredients TEXT NOT NULL DEFAULT '[]', image_emoji TEXT NOT NULL DEFAULT '🧁',
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS orders (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER NOT NULL, customer_name TEXT NOT NULL, phone TEXT NOT NULL,
 fulfillment TEXT NOT NULL, address TEXT NOT NULL DEFAULT '',
 payment TEXT NOT NULL, payment_status TEXT NOT NULL DEFAULT 'Pendente',
 subtotal REAL NOT NULL, discount REAL NOT NULL DEFAULT 0, total REAL NOT NULL,
 coupon_code TEXT, status TEXT NOT NULL DEFAULT 'Recebido',
 notes TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS order_items (
 id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL,
 product_id INTEGER, product_name TEXT NOT NULL, quantity INTEGER NOT NULL,
 unit_price REAL NOT NULL, customizations TEXT NOT NULL DEFAULT '[]',
 FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
 FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS favorites (
 user_id INTEGER NOT NULL, product_id INTEGER NOT NULL,
 PRIMARY KEY(user_id, product_id),
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
 FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS coupons (
 id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL UNIQUE,
 kind TEXT NOT NULL CHECK(kind IN ('percent','fixed')),
 value REAL NOT NULL, active INTEGER NOT NULL DEFAULT 1,
 min_total REAL NOT NULL DEFAULT 0, expires_at TEXT
);
CREATE TABLE IF NOT EXISTS reviews (
 id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL UNIQUE,
 user_id INTEGER NOT NULL, rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
 comment TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(order_id) REFERENCES orders(id), FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS settings (
 key TEXT PRIMARY KEY, value TEXT NOT NULL
);
"""

SEED_PRODUCTS = [
 ("Red Velvet Rose","Clássicos","Massa red velvet com cream cheese rosado e pétalas cristalizadas.",14.90,"🧁",["Farinha","Cacau","Cream cheese","Ovo"]),
 ("Morango & Baunilha","Clássicos","Massa de baunilha com buttercream de morango fresco.",13.90,"🍓",["Farinha","Baunilha","Morango","Leite"]),
 ("Caramelo Flor de Sal","Clássicos","Caramelo artesanal, toffee e flor de sal.",14.90,"🍮",["Farinha","Caramelo","Leite","Ovo"]),
 ("Chocolate Belga","Clássicos","Ganache de chocolate 70% e massa úmida de cacau.",15.90,"🍫",["Farinha","Cacau","Chocolate","Ovo"]),
 ("Matcha & Limão Siciliano","Especiais","Matcha japonês e cobertura cítrica.",16.90,"🍵",["Farinha","Matcha","Limão","Leite"]),
 ("Mirtilo & Mascarpone","Especiais","Mirtilos frescos e mascarpone italiano.",16.90,"🫐",["Farinha","Mirtilo","Mascarpone","Ovo"]),
 ("Lavanda & Mel Silvestre","Premium","Infusão de lavanda com mel silvestre.",17.90,"🌸",["Farinha","Lavanda","Mel","Leite"]),
 ("Maracujá Gold","Premium","Curd de maracujá com cream cheese.",18.90,"🥭",["Farinha","Maracujá","Cream cheese","Ovo"]),
 ("Hibisco & Framboesa","Premium","Hibisco orgânico e framboesa.",17.90,"🌺",["Farinha","Hibisco","Framboesa","Ovo"]),
 ("Coco & Açaí","Veganos","Coco e açaí orgânico. 100% vegetal.",15.90,"🥥",["Farinha","Coco","Açaí"]),
 ("Banana & Amendoim","Veganos","Banana madura, pasta de amendoim e chocolate amargo.",14.90,"🍌",["Farinha","Banana","Amendoim","Chocolate vegetal"])
]

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row
        db.executescript(SCHEMA)
        db.execute("INSERT OR IGNORE INTO settings(key,value) VALUES('opening_hours',?)",
                   (json.dumps({"mon":"09:00-18:00","tue":"09:00-18:00","wed":"09:00-18:00","thu":"09:00-18:00","fri":"09:00-18:00","sat":"09:00-16:00","sun":"Fechado"}, ensure_ascii=False),))
        db.execute("INSERT OR IGNORE INTO users(name,email,password_hash,role) VALUES(?,?,?,'admin')",
                   ("Administrador", "admin@lapetitedouceur.com.br", generate_password_hash("Admin123!")))
        if db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            db.executemany("INSERT INTO products(name,category,description,price,image_emoji,ingredients) VALUES(?,?,?,?,?,?)",
                [(n,c,d,p,e,json.dumps(i,ensure_ascii=False)) for n,c,d,p,e,i in SEED_PRODUCTS])
        db.commit()
        db.close()
