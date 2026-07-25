# Déploiement AZULAN sur Render

## 🔑 Étape 1: Configurer tes clés Stripe

1. Va sur [Stripe Dashboard](https://dashboard.stripe.com)
2. Copie ta **clé publique** (commence par `pk_test_` ou `pk_live_`)
3. Copie ta **clé secrète** (commence par `sk_test_` ou `sk_live_`)

## ✏️ Étape 2: Mettre à jour les fichiers locaux

### A) `backend/.env`
Remplace les placeholders par tes vraies clés:
```env
STRIPE_SECRET_KEY=sk_test_XXXXX
STRIPE_PUBLIC_KEY=pk_test_XXXXX
```

### B) `panier.html`
Remplace `pk_test_YOUR_STRIPE_PUBLIC_KEY_HERE` par ta vraie clé publique (ligne ~614):
```javascript
const stripe = Stripe('pk_test_XXXXX');
```

## 🚀 Étape 3: Déployer sur Render

### Option A: Via Interface Render (Facile)
1. Va sur [render.com](https://render.com)
2. Clique "New +" → "Web Service"
3. Choisis "Build and deploy from a Git repository"
4. Connecte ton repo GitHub avec le code
5. Remplis:
   - **Name**: `azulan-backend`
   - **Runtime**: `Node`
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Port**: `3000`

### Option B: Via render.yaml (Auto)
1. Crée `render.yaml` à la racine du repo
2. Copie le contenu du fichier render.yaml fourni
3. Push sur GitHub
4. Render va automatiquement détecter et déployer

### Option C: Via CLI Render
```bash
npm install -g @render/cli
render login
render deploy
```

## 🔐 Étape 4: Ajouter Variables d'Environnement sur Render

1. Dans Render Dashboard → Ton service
2. Clique "Environment"
3. Ajoute:
   ```
   STRIPE_SECRET_KEY = sk_test_XXXXX
   STRIPE_PUBLIC_KEY = pk_test_XXXXX
   FRONTEND_URL = https://ton-site.netlify.app (ou ton URL frontend)
   NODE_ENV = production
   ```

## 🔗 Étape 5: Configurer le Frontend

### Pour Netlify/GitHub Pages:
1. Mets à jour l'URL API dans les fichiers HTML:
   ```javascript
   const API = 'https://azulan-backend.onrender.com/api';
   ```

2. Mets à jour les URLs de redirect Stripe:
   - Success: `https://ton-site.netlify.app/success.html?session_id={CHECKOUT_SESSION_ID}`
   - Cancel: `https://ton-site.netlify.app/cancel.html`

## ✅ Tester le Déploiement

1. Va sur `https://azulan-backend.onrender.com/health`
2. Tu dois voir: `{"status":"OK"}`
3. Teste un achat avec la carte Stripe de test: `4242 4242 4242 4242`
4. Remplis n'importe quelle date future et n'importe quel CVC

## 🐛 Dépannage

### "Cannot find module 'sqlite3'"
```bash
cd backend
npm install
npm start
```

### Port déjà utilisé (localhost)
Change le PORT dans `.env` ou tu peux ignorer, ce n'est qu'en local.

### CORS errors
Ajoute ton URL frontend dans `server.js` ligne 14:
```javascript
origin: ['https://ton-site.netlify.app', 'http://localhost:5500', ...]
```

### Stripe redirect ne fonctionne pas
Vérifie que:
- La clé publique est la bonne
- L'URL du checkout est correcte
- FRONTEND_URL est mise à jour dans `.env`

## 📊 Fichiers à modifier:

- ✅ `backend/.env` - Clés Stripe + URLs
- ✅ `panier.html` - Clé publique Stripe
- ✅ `index.html`, `produit.html`, `categorie.html` - URL API (optionnel)
- ✅ `server.js` - CORS origins (optionnel)

Voilà! Ton site sera en ligne! 🎉
