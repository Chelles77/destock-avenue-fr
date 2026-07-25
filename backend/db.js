const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'products.db');
const db = new sqlite3.Database(dbPath);

db.serialize(() => {
  // Table des utilisateurs
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      email TEXT,
      role TEXT DEFAULT 'collaborateur',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Table des catégories
  db.run(`
    CREATE TABLE IF NOT EXISTS categories (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      image TEXT,
      badge TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Table des produits
  db.run(`
    CREATE TABLE IF NOT EXISTS products (
      id TEXT PRIMARY KEY,
      category TEXT NOT NULL,
      name TEXT NOT NULL,
      price REAL NOT NULL,
      original_price REAL NOT NULL,
      discount TEXT,
      stock INTEGER DEFAULT 0,
      image TEXT,
      description TEXT,
      brand TEXT,
      model TEXT,
      warranty TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Migrations pour les colonnes manquantes
  db.run(`ALTER TABLE products ADD COLUMN description TEXT`, function(err) {
    if (!err) console.log('✅ Colonne description ajoutée aux produits');
  });
  db.run(`ALTER TABLE products ADD COLUMN brand TEXT`, function(err) {
    if (!err) console.log('✅ Colonne brand ajoutée aux produits');
  });
  db.run(`ALTER TABLE products ADD COLUMN model TEXT`, function(err) {
    if (!err) console.log('✅ Colonne model ajoutée aux produits');
  });
  db.run(`ALTER TABLE products ADD COLUMN warranty TEXT`, function(err) {
    if (!err) console.log('✅ Colonne warranty ajoutée aux produits');
  });
  db.run(`ALTER TABLE products ADD COLUMN images TEXT`, function(err) {
    if (!err) console.log('✅ Colonne images ajoutée aux produits');
  });

  // Créer l'admin par défaut si n'existe pas
  db.run(`INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)`,
    ['admin', 'admin123', 'admin'],
    function(err) {
      if (!err) console.log('✅ Admin par défaut créé (login: admin / password: admin123)');
    }
  );

  // Créer les catégories par défaut
  const defaultCategories = [
    ['aspirateurs', 'Aspirateurs Robots', 'https://picsum.photos/300/180?random=1'],
    ['cafetiere', 'Cafetières', 'https://picsum.photos/300/180?random=2'],
    ['airfryer', 'Air Fryers', 'https://picsum.photos/300/180?random=3'],
    ['robots', 'Robots Cuiseur', 'https://picsum.photos/300/180?random=4'],
    ['electromenager', 'Électroménager', 'https://picsum.photos/300/180?random=5'],
    ['autres', 'Autres', 'https://picsum.photos/300/180?random=6']
  ];

  defaultCategories.forEach(([id, name, image]) => {
    db.run(`INSERT OR IGNORE INTO categories (id, name, image) VALUES (?, ?, ?)`, [id, name, image]);
  });

  // Migration: ajouter la colonne badge si elle n'existe pas
  db.run(`ALTER TABLE categories ADD COLUMN badge TEXT`, function(err) {
    if (!err) console.log('✅ Colonne badge ajoutée aux catégories');
  });
});

module.exports = db;
