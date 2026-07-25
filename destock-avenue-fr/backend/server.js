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
app.get('/api/products', async (req, res) => {
  try {
    const result = await db.query('SELECT * FROM products ORDER BY category, name');
    res.json(result.rows || []);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/products/category/:category', async (req, res) => {
  try {
    const result = await db.query('SELECT * FROM products WHERE category = $1 ORDER BY name', [req.params.category]);
    res.json(result.rows || []);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/products', async (req, res) => {
  const { id, category, name, price, original_price, discount, stock, image } = req.body;
  try {
    await db.query(
      'INSERT INTO products (id, category, name, price, original_price, discount, stock, image) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)',
      [id, category, name, price, original_price, discount, stock, image]
    );
    res.json({ id, message: 'Produit ajouté' });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

app.put('/api/products/:id', async (req, res) => {
  const { name, price, original_price, discount, stock, image } = req.body;
  try {
    await db.query(
      'UPDATE products SET name=$1, price=$2, original_price=$3, discount=$4, stock=$5, image=$6 WHERE id=$7',
      [name, price, original_price, discount, stock, image, req.params.id]
    );
    res.json({ message: 'Produit mis à jour' });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

app.delete('/api/products/:id', async (req, res) => {
  try {
    await db.query('DELETE FROM products WHERE id=$1', [req.params.id]);
    res.json({ message: 'Produit supprimé' });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
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
