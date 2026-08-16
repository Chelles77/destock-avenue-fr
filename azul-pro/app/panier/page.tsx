export default function Panier() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Votre Panier</h1>
      <div className="text-center py-12">
        <p className="text-gray-600 mb-4">Votre panier est vide</p>
        <a href="/catalogue" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700">
          Continuer vos achats
        </a>
      </div>
    </div>
  );
}
