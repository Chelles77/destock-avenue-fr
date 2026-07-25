require('dotenv').config();
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors({
  origin: ['http://localhost:5500', 'http://localhost:3000', 'https://destock-avenue-fr.netlify.app'],
  credentials: true
}));
app.use(express.json());

// Config multer pour les uploads
const uploadsDir = path.join(__dirname, '../static/images');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: uploadsDir,
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'product-' + uniqueSuffix + path.extname(file.originalname));
  }
});
const upload = multer({ storage, limits: { fileSize: 5 * 1024 * 1024 } });

app.use(express.static(path.join(__dirname, '..')));

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5500';

app.post('/create-checkout-session', async (req, res) => {
  try {
    const { items } = req.body;

    if (!items || items.length === 0) {
      return res.status(400).json({ error: 'Panier vide' });
    }

    const line_items = items.map(item => ({
      price_data: {
        currency: 'eur',
        product_data: {
          name: item.name,
        },
        unit_amount: Math.round(item.price * 100),
      },
      quantity: item.qty,
    }));

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: line_items,
      mode: 'payment',
      success_url: `${FRONTEND_URL}/success.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${FRONTEND_URL}/cancel.html`,
    });

    res.json({ id: session.id });
  } catch (error) {
    console.error('Erreur:', error.message);
    res.status(500).json({ error: error.message });
  }
});

app.get('/session-status', async (req, res) => {
  try {
    const session = await stripe.checkout.sessions.retrieve(req.query.session_id);
    res.json({
      status: session.payment_status,
      customer_email: session.customer_details.email,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'OK' });
});

// === UPLOAD IMAGE ===
app.post('/api/upload', upload.single('image'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'Pas d\'image' });
  const imagePath = '/static/images/' + req.file.filename;
  res.json({ url: imagePath });
});

// === ROUTES PRODUITS ===
app.get('/api/products', (req, res) => {
  db.all('SELECT * FROM products ORDER BY category, name', (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows || []);
  });
});

app.get('/api/products/category/:category', (req, res) => {
  db.all('SELECT * FROM products WHERE category = ? ORDER BY name', [req.params.category], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows || []);
  });
});

app.post('/api/products', (req, res) => {
  const { id, category, name, price, original_price, discount, stock, image } = req.body;
  db.run(
    'INSERT INTO products (id, category, name, price, original_price, discount, stock, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
    [id, category, name, price, original_price, discount, stock, image],
    function(err) {
      if (err) return res.status(400).json({ error: err.message });
      res.json({ id, message: 'Produit ajouté' });
    }
  );
});

app.put('/api/products/:id', (req, res) => {
  const { name, price, original_price, discount, stock, image } = req.body;
  db.run(
    'UPDATE products SET name=?, price=?, original_price=?, discount=?, stock=?, image=? WHERE id=?',
    [name, price, original_price, discount, stock, image, req.params.id],
    function(err) {
      if (err) return res.status(400).json({ error: err.message });
      res.json({ message: 'Produit mis à jour' });
    }
  );
});

app.delete('/api/products/:id', (req, res) => {
  db.run('DELETE FROM products WHERE id=?', [req.params.id], function(err) {
    if (err) return res.status(400).json({ error: err.message });
    res.json({ message: 'Produit supprimé' });
  });
});

// === AUTH ===
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (username === 'admin' && password === 'admin123') {
    res.json({
      success: true,
      token: 'demo-token-12345',
      user: { id: 1, username: 'admin', role: 'admin' }
    });
  } else {
    res.json({ success: false, error: 'Identifiants incorrects' });
  }
});

// === CATEGORIES ===
app.get('/api/categories', (req, res) => {
  db.all('SELECT DISTINCT category as id, category as name FROM products ORDER BY category', (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows || []);
  });
});

app.listen(PORT, () => {
  console.log(`✅ Serveur lancé sur http://localhost:${PORT}`);
});
