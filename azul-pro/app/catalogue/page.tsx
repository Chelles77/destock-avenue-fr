'use client';

import { useState } from 'react';

// Données de test - remplacer par API Supabase
const PRODUCTS = [
  {
    id: 1,
    name: 'Dreame H15 Aspirateur Robot',
    category: 'aspirateurs-robots',
    brand: 'Dreame',
    type: 'retour-client',
    priceNew: 899,
    priceOccasion: 449,
    condition: 'Bon État',
    image: '🤖',
    savings: 50,
  },
  {
    id: 2,
    name: 'Dyson V15 Detect - Bleu',
    category: 'aspirateurs-sans-fil',
    brand: 'Dyson',
    type: 'occasion',
    priceNew: 749,
    priceOccasion: 299,
    condition: 'Occasion',
    image: '🧹',
    savings: 60,
  },
  {
    id: 3,
    name: 'Philips Série 9000 Laserscan',
    category: 'aspirateurs-robots',
    brand: 'Philips',
    type: 'retour-client',
    priceNew: 1299,
    priceOccasion: 549,
    condition: 'Comme Neuf',
    image: '🤖',
    savings: 58,
  },
  {
    id: 4,
    name: 'Ninja Blender Pro Max',
    category: 'cuisine',
    brand: 'Ninja',
    type: 'retour-client',
    priceNew: 399,
    priceOccasion: 179,
    condition: 'Bon État',
    image: '🍳',
    savings: 55,
  },
  {
    id: 5,
    name: 'Bosch Lave-Vaisselle Serie 6',
    category: 'cuisine',
    brand: 'Bosch',
    type: 'occasion',
    priceNew: 599,
    priceOccasion: 199,
    condition: 'Occasion',
    image: '🍳',
    savings: 67,
  },
];

export default function Catalogue() {
  const [selectedCondition, setSelectedCondition] = useState<string | null>(null);
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null);

  const filtered = PRODUCTS.filter(p => {
    if (selectedCondition && p.condition !== selectedCondition) return false;
    if (selectedBrand && p.brand !== selectedBrand) return false;
    return true;
  });

  const brands = [...new Set(PRODUCTS.map(p => p.brand))];
  const conditions = [...new Set(PRODUCTS.map(p => p.condition))];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Catalogue</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Filtres */}
        <div className="md:col-span-1">
          <div className="bg-gray-50 p-6 rounded-lg sticky top-4">
            <h3 className="font-bold mb-4">État du produit</h3>
            <div className="space-y-2 mb-6">
              {conditions.map(c => (
                <label key={c} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="condition"
                    checked={selectedCondition === c}
                    onChange={() => setSelectedCondition(c === selectedCondition ? null : c)}
                  />
                  {c}
                </label>
              ))}
            </div>

            <h3 className="font-bold mb-4">Marque</h3>
            <div className="space-y-2">
              {brands.map(b => (
                <label key={b} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedBrand === b}
                    onChange={() => setSelectedBrand(selectedBrand === b ? null : b)}
                  />
                  {b}
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Produits */}
        <div className="md:col-span-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filtered.map(product => (
              <div key={product.id} className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition">
                <div className="bg-gray-100 h-64 flex items-center justify-center text-6xl">
                  {product.image}
                </div>
                <div className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="text-xs text-gray-500 uppercase">{product.brand}</p>
                      <h3 className="font-bold text-sm">{product.name}</h3>
                    </div>
                    <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-bold">
                      -{product.savings}%
                    </span>
                  </div>

                  <div className="mb-3">
                    <span className="inline-block bg-yellow-50 text-yellow-700 px-2 py-1 rounded text-xs mb-2">
                      {product.type === 'retour-client' ? '🔄 Retour Client' : '📦 Occasion'}
                    </span>
                    <p className="text-xs text-gray-600">{product.condition}</p>
                  </div>

                  <div className="mb-4">
                    <p className="text-lg md:text-2xl font-bold text-blue-600">{product.priceOccasion}€</p>
                    <p className="text-sm line-through text-gray-400">Prix neuf: {product.priceNew}€</p>
                  </div>

                  <button className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700">
                    Ajouter au panier
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
