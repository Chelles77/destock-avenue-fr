const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const db = require('./db');

const app = express();
const PORT = 3000;
const sessions = {};

app.use(cors());
app.use(express.json());

// Créer le dossier images
const uploadDir = path.join(__dirname, '..', 'destock-avenue-fr', 'images');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: uploadDir,
  filename: (req, file, cb) => {
    const name = Date.now() + '-' + file.originalname;
    cb(null, name);
  }
});

const upload = multer({ storage });

// Middleware d'authentification
const checkAuth = (req, res, next) => {
  const token = req.headers['x-token'];
  if (!token || !sessions[token]) {
    return res.status(401).json({ error: 'Non authentifié' });
  }
  req.user = sessions[token];
  next();
};

const checkAdmin = (req, res, next) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Accès refusé - Admin seulement' });
  }
  next();
};

app.use('/images', express.static(uploadDir));
const siteDir = path.join(__dirname, '..', 'destock-avenue-fr');
app.use(express.static(siteDir));

// ========== AUTHENTIFICATION ==========
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  db.get('SELECT * FROM users WHERE username = ? AND password = ?', [username, password], (err, user) => {
    if (err || !user) {
      return res.status(401).json({ error: 'Identifiants incorrects' });
    }
    const token = Math.random().toString(36).substr(2);
    sessions[token] = user;
    res.json({ success: true, token, user: { id: user.id, username: user.username, role: user.role } });
  });
});

app.post('/api/logout', (req, res) => {
  const token = req.headers['x-token'];
  delete sessions[token];
  res.json({ success: true });
});

// ========== GESTION DES UTILISATEURS ==========
app.get('/api/users', (req, res) => {
  db.all('SELECT id, username, email, role, created_at FROM users', (err, rows) => {
    res.json(rows || []);
  });
});

app.post('/api/users', (req, res) => {
  const { username, password, email, role } = req.body;
  db.run('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
    [username, password, email, role || 'collaborateur'],
    function(err) {
      if (err) return res.status(400).json({ error: err.message });
      res.json({ success: true, id: this.lastID });
    }
  );
});

app.delete('/api/users/:id', (req, res) => {
  db.run('DELETE FROM users WHERE id = ?', [req.params.id], (err) => {
    if (err) return res.status(400).json({ error: err.message });
    res.json({ success: true });
  });
});

// ========== GESTION DES CATÉGORIES ==========
app.get('/api/categories', (req, res) => {
  db.all('SELECT * FROM categories ORDER BY name', (err, rows) => {
    res.json(rows || []);
  });
});

app.post('/api/categories', (req, res) => {
  const { id, name, image, badge } = req.body;
  db.run('INSERT OR REPLACE INTO categories (id, name, image, badge) VALUES (?, ?, ?, ?)',
    [id, name, image, badge || null],
    (err) => {
      if (err) return res.status(400).json({ error: err.message });
      res.json({ success: true });
    }
  );
});

app.delete('/api/categories/:id', (req, res) => {
  db.run('DELETE FROM categories WHERE id = ?', [req.params.id], (err) => {
    if (err) return res.status(400).json({ error: err.message });
    res.json({ success: true });
  });
});

app.put('/api/categories/:id', (req, res) => {
  const { name, badge, image } = req.body;
  db.run('UPDATE categories SET name = ?, badge = ?, image = ? WHERE id = ?',
    [name, badge || null, image || null, req.params.id],
    function(err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ success: true });
    }
  );
});

// ========== GESTION DES IMAGES ==========
app.post('/api/upload', upload.single('image'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
  const fileUrl = `http://localhost:3000/images/${req.file.filename}`;
  res.json({ url: fileUrl });
});

// ========== GESTION DES PRODUITS ==========
app.get('/api/products', (req, res) => {
  db.all('SELECT * FROM products ORDER BY created_at DESC', (err, rows) => {
    res.json(rows || []);
  });
});

app.get('/api/products/category/:category', (req, res) => {
  db.all('SELECT * FROM products WHERE category = ? ORDER BY created_at DESC', [req.params.category], (err, rows) => {
    res.json(rows || []);
  });
});

app.post('/api/products', (req, res) => {
  const { id, category, name, price, original_price, discount, stock, image, images, description, brand, model, warranty, annonce } = req.body;
  if (!id || !category || !name) return res.status(400).json({ error: 'Missing fields' });

  const imagesJson = images && images.length > 0 ? JSON.stringify(images) : null;

  db.run('INSERT OR REPLACE INTO products (id, category, name, price, original_price, discount, stock, image, images, description, brand, model, warranty, annonce) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
    [id, category, name, price, original_price, discount, stock, image, imagesJson, description || null, brand || null, model || null, warranty || null, annonce || null],
    function(err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ success: true, id });
    }
  );
});

app.delete('/api/products/:id', (req, res) => {
  db.run('DELETE FROM products WHERE id = ?', [req.params.id], (err) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ success: true });
  });
});

app.put('/api/products/:id', (req, res) => {
  const { name, category, price, original_price, stock, brand, model, warranty, description, image, images, discount, annonce } = req.body;
  const imagesJson = images && images.length > 0 ? JSON.stringify(images) : null;
  db.run('UPDATE products SET name = ?, category = ?, price = ?, original_price = ?, stock = ?, brand = ?, model = ?, warranty = ?, description = ?, image = ?, images = ?, discount = ?, annonce = ? WHERE id = ?',
    [name, category, price, original_price, stock, brand || null, model || null, warranty || null, description || null, image || null, imagesJson, discount || null, annonce || null, req.params.id],
    function(err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ success: true });
    }
  );
});

app.put('/api/users/:id', (req, res) => {
  const { username, email, role } = req.body;
  db.run('UPDATE users SET username = ?, email = ?, role = ? WHERE id = ?',
    [username, email || null, role, req.params.id],
    function(err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ success: true });
    }
  );
});

app.listen(PORT, () => {
  console.log(`✅ Serveur lancé sur http://localhost:${PORT}`);
  console.log('✅ Login par défaut: admin / admin123');
});
