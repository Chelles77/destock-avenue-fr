export default function Home() {
  const products = [
    { id: 1, name: "Dreame H15", price: 449, original: 899, condition: "Retour Client", img: "🤖" },
    { id: 2, name: "Dyson V15", price: 299, original: 749, condition: "Occasion", img: "🧹" },
    { id: 3, name: "Philips S9000", price: 549, original: 1299, condition: "Comme Neuf", img: "🤖" },
    { id: 4, name: "Ninja Blender", price: 179, original: 399, condition: "Retour Client", img: "🍳" },
    { id: 5, name: "Bosch Lave-Vaisselle", price: 199, original: 599, condition: "Occasion", img: "🧽" },
    { id: 6, name: "AEG Aspirateur", price: 249, original: 599, condition: "Bon État", img: "🧹" },
  ];

  return (
    <div className="w-full">
      {/* Hero Carrousel */}
      <section className="bg-gradient-to-r from-blue-700 via-blue-600 to-teal-600 text-white py-24">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h1 className="text-5xl font-bold mb-6">Électroménager Premium</h1>
              <p className="text-lg md:text-2xl mb-4">C'est de l'appareil au même</p>
              <p className="text-lg mb-8 text-blue-100">Occasion & Retours Clients reconditionnés - Jusqu'à -60% - Testés & Certifiés</p>
              <a href="/catalogue" className="inline-block bg-white text-blue-700 px-8 py-3 rounded-full font-bold hover:bg-gray-100 transition">
                Voir tous les produits
              </a>
            </div>
            <div className="text-9xl opacity-20">⚙️</div>
          </div>
        </div>
      </section>

      {/* Promo Banner */}
      <section className="bg-yellow-50 border-b-4 border-yellow-400 py-4">
        <div className="max-w-7xl mx-auto px-4 text-center font-semibold text-yellow-900">
          🎁 Offre spéciale Août : Découvrez nos reconditionnements avec garantie 12 mois
        </div>
      </section>

      {/* Nos petits chouchous - Carrousel Produits */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold">Nos petits chouchous</h2>
          <div className="flex gap-2">
            <a href="/catalogue?sort=best" className="text-blue-600 hover:underline">Bons plans</a>
            <span className="text-gray-400">|</span>
            <a href="/catalogue?sort=popular" className="text-blue-600 hover:underline">Meilleures ventes</a>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(p => (
            <div key={p.id} className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-xl transition">
              <div className="bg-gray-100 h-64 flex items-center justify-center text-6xl">{p.img}</div>
              <div className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-sm">{p.name}</h3>
                  <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-bold">
                    -{Math.round((1 - p.price / p.original) * 100)}%
                  </span>
                </div>
                <span className="inline-block bg-yellow-50 text-yellow-700 px-2 py-1 rounded text-xs mb-3 font-semibold">
                  🔄 {p.condition}
                </span>
                <p className="text-xs text-gray-600 mb-3">✓ Fonctionnement 100% | Testé</p>
                <div className="mb-4">
                  <p className="text-lg md:text-2xl font-bold text-blue-600">{p.price}€</p>
                  <p className="text-sm line-through text-gray-400">Prix neuf: {p.original}€</p>
                </div>
                <button className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 transition">
                  Ajouter au panier
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Avis Clients */}
      <section className="max-w-7xl mx-auto px-4 py-12 border-t">
        <h2 className="text-lg md:text-2xl font-bold mb-8">Les avis clients</h2>
        <div className="bg-gradient-to-r from-yellow-400 to-yellow-300 p-8 rounded-lg text-center">
          <div className="text-5xl font-bold text-white mb-2">⭐ 4.7/5</div>
          <p className="text-gray-800 font-semibold">Basé sur 2,854 avis vérifiés</p>
          <a href="#" className="text-blue-600 hover:underline mt-4 inline-block">Voir tous les avis →</a>
        </div>
      </section>

      {/* FAQ */}
      <section className="max-w-7xl mx-auto px-4 py-12 border-t">
        <h2 className="text-lg md:text-2xl font-bold mb-8">Questions fréquentes</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-bold mb-2">Qu'est-ce qu'un produit reconditionné?</h3>
            <p className="text-gray-600 text-sm">Un produit reconditionnée est un appareil qui a déjà eu un propriétaire, nettoyé et testé en profondeur par nos équipes...</p>
          </div>
          <div>
            <h3 className="font-bold mb-2">Pourquoi acheter reconditionné chez Azul Pro?</h3>
            <p className="text-gray-600 text-sm">Azul Pro est un acteur de confiance avec équipes expertes, garantie 12 mois, retour gratuit 14j, et reconditionnement français...</p>
          </div>
          <div>
            <h3 className="font-bold mb-2">Quelle est la garantie?</h3>
            <p className="text-gray-600 text-sm">Tous nos produits bénéficient d'une garantie commerciale de 12 mois et d'une assistance SAV réactive...</p>
          </div>
          <div>
            <h3 className="font-bold mb-2">Quel est le délai de retour?</h3>
            <p className="text-gray-600 text-sm">Vous avez 14 jours pour tester votre produit. Retour gratuit si vous n'êtes pas satisfait...</p>
          </div>
        </div>
        <div className="mt-6 text-center">
          <a href="#" className="text-blue-600 hover:underline font-semibold">Toutes nos FAQ →</a>
        </div>
      </section>

      {/* Newsletter */}
      <section className="bg-gray-50 py-12 border-t">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h2 className="text-lg md:text-2xl font-bold mb-3">Recevez les meilleures offres</h2>
          <p className="text-gray-600 mb-6">Inscrivez-vous à notre newsletter pour les bons plans en exclusivité</p>
          <form className="flex gap-2 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Votre email..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg"
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-700 transition"
            >
              S'inscrire
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}
