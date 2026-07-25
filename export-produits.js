#!/usr/bin/env node

const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');

// Coleurs console
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

// Génère un slug à partir du titre
function generateSlug(title) {
  return title
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// Cherche le fichier .db dans le répertoire courant
function findDatabase() {
  const dir = process.cwd();
  const files = fs.readdirSync(dir);

  // Cherche d'abord dans ./instance/
  const instanceDir = path.join(dir, 'instance');
  if (fs.existsSync(instanceDir)) {
    const instanceFiles = fs.readdirSync(instanceDir);
    const dbFile = instanceFiles.find(f => f.endsWith('.db'));
    if (dbFile) {
      return path.join(instanceDir, dbFile);
    }
  }

  // Sinon cherche à la racine
  const dbFile = files.find(f => f.endsWith('.db'));
  if (dbFile) {
    return path.join(dir, dbFile);
  }

  return null;
}

// Main
async function exportProducts() {
  console.log(`${colors.blue}🔍 Recherche de la base de données SQLite...${colors.reset}`);

  const dbPath = findDatabase();
  if (!dbPath) {
    console.error(`${colors.red}❌ Erreur: Aucun fichier .db trouvé${colors.reset}`);
    process.exit(1);
  }

  console.log(`${colors.green}✓ DB trouvée: ${dbPath}${colors.reset}`);

  try {
    const db = new Database(dbPath, { readonly: true });
    console.log(`${colors.blue}📂 Connexion à la base de données établie${colors.reset}`);

    // Cherche la bonne table
    const tableNames = ['stock_items', 'products', 'raw_products'];
    let tableName = null;
    for (const name of tableNames) {
      const exists = db.prepare(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
      ).get(name);
      if (exists) {
        tableName = name;
        break;
      }
    }

    if (!tableName) {
      console.error(`${colors.red}❌ Erreur: Aucune table de produits trouvée${colors.reset}`);
      console.log(`${colors.yellow}Tables disponibles:${colors.reset}`);
      const tables = db.prepare(
        "SELECT name FROM sqlite_master WHERE type='table'"
      ).all();
      tables.forEach(t => console.log(`  - ${t.name}`));
      db.close();
      process.exit(1);
    }

    console.log(`${colors.green}✓ Table utilisée: ${tableName}${colors.reset}`);

    // Récupère les colonnes de la table
    const columns = db.pragma(`table_info(${tableName})`);
    console.log(`${colors.blue}📋 Colonnes trouvées:${colors.reset}`);
    columns.forEach(col => console.log(`  - ${col.name}`));

    // Récupère tous les produits
    const products = db.prepare(`SELECT * FROM ${tableName}`).all();
    console.log(`${colors.green}✓ ${products.length} produits trouvés${colors.reset}`);

    // Mappe les produits au format cible
    const exportedProducts = products.map((product, idx) => {
      const slug = generateSlug(product.name || 'produit');

      // Génère des valeurs de test réalistes si vides
      const purchase = product.purchase_price || 199 + (idx % 3) * 100;
      const sale = product.sale_price || Math.max(0, purchase - 30 - (idx % 4) * 20);
      const brands = ['Samsung', 'LG', 'Philips', 'Dyson', 'Shark', 'Electrolux'];
      const categories = ['Électroménager', 'Robotique', 'Nettoyage', 'Cuisine', 'Multimédia'];

      // Génère une image placeholder pour le produit
      const placeholderImage = `placeholder-${product.id}.jpg`;

      return {
        id: product.id,
        slug: slug,
        title: product.name || 'Produit',
        brand: product.brand || brands[idx % brands.length],
        category: product.category || categories[idx % categories.length],
        condition: product.condition || 'Comme neuf',
        priceNew: purchase,
        priceSale: sale,
        purchasePrice: purchase,
        score: product.score || (12 + (idx % 5)),
        images: product.image_url ? [product.image_url] : [placeholderImage],
        description: product.description || `Produit de qualité ${product.condition || 'Comme neuf'} - Stock #${product.id}`,
        inStock: (product.quantity_available || 1) > 0,
        dateAdded: product.date_added || new Date().toISOString()
      };
    });

    // Prépare le chemin d'export (parent du répertoire courant)
    const parentDir = path.dirname(process.cwd());
    const siteDir = path.join(parentDir, 'site-ecommerce');
    const outputPath = path.join(siteDir, 'produits.json');

    // Crée le répertoire site-ecommerce s'il n'existe pas
    if (!fs.existsSync(siteDir)) {
      fs.mkdirSync(siteDir, { recursive: true });
      console.log(`${colors.green}✓ Répertoire créé: ${siteDir}${colors.reset}`);
    }

    // Écrit le JSON
    fs.writeFileSync(
      outputPath,
      JSON.stringify(exportedProducts, null, 2),
      'utf8'
    );

    console.log(`${colors.green}✓ Export réussi: ${outputPath}${colors.reset}`);
    console.log(`${colors.blue}📊 Statistiques:${colors.reset}`);
    console.log(`  - Produits exportés: ${exportedProducts.length}`);
    console.log(`  - Catégories: ${[...new Set(exportedProducts.map(p => p.category))].length}`);
    console.log(`  - Marques: ${[...new Set(exportedProducts.map(p => p.brand))].length}`);

    db.close();
    console.log(`${colors.green}✓ Terminé${colors.reset}`);

  } catch (error) {
    console.error(`${colors.red}❌ Erreur:${colors.reset}`, error.message);
    process.exit(1);
  }
}

exportProducts();
