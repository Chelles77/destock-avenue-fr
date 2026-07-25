const db = require('./db');

const products = [
  // Aspirateurs
  { id: 'dreame-x50', category: 'aspirateurs', name: 'DREAME X50 Ultra', price: 899, original_price: 1686, discount: '-47%', stock: 2, image: 'https://picsum.photos/300/300?random=1' },
  { id: 'ecovacs-x11', category: 'aspirateurs', name: 'ECOVACS X11 Robot', price: 799, original_price: 1599, discount: '-50%', stock: 5, image: 'https://picsum.photos/300/300?random=2' },
  { id: 'samsung-jet', category: 'aspirateurs', name: 'Samsung Jet Bot', price: 699, original_price: 1349, discount: '-48%', stock: 3, image: 'https://picsum.photos/300/300?random=3' },
  { id: 'irobot-roomba', category: 'aspirateurs', name: 'iRobot Roomba j9+', price: 629, original_price: 1029, discount: '-39%', stock: 4, image: 'https://picsum.photos/300/300?random=4' },

  // Cafetières
  { id: 'krups-essential', category: 'cafetiere', name: 'Krups Essential', price: 299, original_price: 516, discount: '-42%', stock: 8, image: 'https://picsum.photos/300/300?random=5' },
  { id: 'philips-3100', category: 'cafetiere', name: 'Philips Series 3100', price: 399, original_price: 614, discount: '-35%', stock: 5, image: 'https://picsum.photos/300/300?random=6' },
  { id: 'nespresso-vertuo', category: 'cafetiere', name: 'Nespresso Vertuo Pro', price: 499, original_price: 714, discount: '-30%', stock: 3, image: 'https://picsum.photos/300/300?random=7' },
  { id: 'jura-impressa', category: 'cafetiere', name: 'Jura Impressa Z10', price: 799, original_price: 1065, discount: '-25%', stock: 2, image: 'https://picsum.photos/300/300?random=8' },

  // Air Fryers
  { id: 'ninja-af101', category: 'airfryer', name: 'Ninja AF101 Air Fryer', price: 129, original_price: 222, discount: '-42%', stock: 8, image: 'https://picsum.photos/300/300?random=9' },
  { id: 'tefal-easyfy', category: 'airfryer', name: 'Tefal Easy Fry Compact', price: 89, original_price: 137, discount: '-35%', stock: 5, image: 'https://picsum.photos/300/300?random=10' },
  { id: 'philips-xxl', category: 'airfryer', name: 'Philips Airfryer XXL', price: 349, original_price: 499, discount: '-30%', stock: 3, image: 'https://picsum.photos/300/300?random=11' },
  { id: 'delonghi-pro', category: 'airfryer', name: 'De\'Longhi Air Fryer', price: 199, original_price: 265, discount: '-25%', stock: 2, image: 'https://picsum.photos/300/300?random=12' },

  // Robots Cuiseur
  { id: 'magimix-5200', category: 'robots', name: 'Magimix Robot Multifonction', price: 599, original_price: 1032, discount: '-42%', stock: 8, image: 'https://picsum.photos/300/300?random=13' },
  { id: 'cuiseur-connect', category: 'robots', name: 'Monsieur Cuisine Connect', price: 449, original_price: 691, discount: '-35%', stock: 5, image: 'https://picsum.photos/300/300?random=14' },
  { id: 'thermomix-pro', category: 'robots', name: 'Thermomix Pro', price: 789, original_price: 1127, discount: '-30%', stock: 3, image: 'https://picsum.photos/300/300?random=15' },
  { id: 'kenwood-chef', category: 'robots', name: 'Kenwood Chef Titanium', price: 399, original_price: 532, discount: '-25%', stock: 2, image: 'https://picsum.photos/300/300?random=16' },

  // Électroménager
  { id: 'samsung-micro', category: 'electromenager', name: 'Samsung Microwave 28L', price: 199, original_price: 344, discount: '-42%', stock: 8, image: 'https://picsum.photos/300/300?random=17' },
  { id: 'honeywell-humidi', category: 'electromenager', name: 'Honeywell Humidifier', price: 79, original_price: 122, discount: '-35%', stock: 5, image: 'https://picsum.photos/300/300?random=18' },
  { id: 'karcher-steam', category: 'electromenager', name: 'Kärcher Steam Cleaner', price: 249, original_price: 356, discount: '-30%', stock: 3, image: 'https://picsum.photos/300/300?random=19' },
  { id: 'lg-washtower', category: 'electromenager', name: 'LG WashTower XL', price: 1199, original_price: 1599, discount: '-25%', stock: 2, image: 'https://picsum.photos/300/300?random=20' },

  // Autres
  { id: 'bbq-pro', category: 'autres', name: 'BBQ Grill Pro Stainless', price: 189, original_price: 326, discount: '-42%', stock: 8, image: 'https://picsum.photos/300/300?random=21' },
  { id: 'rowenta-iron', category: 'autres', name: 'Rowenta Steam Compact', price: 59, original_price: 91, discount: '-35%', stock: 5, image: 'https://picsum.photos/300/300?random=22' },
  { id: 'air-monitor', category: 'autres', name: 'Smart Air Quality Monitor', price: 89, original_price: 127, discount: '-30%', stock: 3, image: 'https://picsum.photos/300/300?random=23' },
  { id: 'storage-xl', category: 'autres', name: 'Organisateur Rangement', price: 49, original_price: 65, discount: '-25%', stock: 2, image: 'https://picsum.photos/300/300?random=24' }
];

db.serialize(() => {
  db.run('DELETE FROM products', (err) => {
    if (err) console.error('Erreur DELETE:', err);
  });

  products.forEach(p => {
    db.run(
      'INSERT INTO products (id, category, name, price, original_price, discount, stock, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [p.id, p.category, p.name, p.price, p.original_price, p.discount, p.stock, p.image],
      (err) => {
        if (err) console.error('Erreur INSERT:', err);
      }
    );
  });

  console.log('✅ BD initialisée avec ' + products.length + ' produits');
  process.exit(0);
});
