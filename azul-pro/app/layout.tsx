import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Azul Pro - Électroménager d'Occasion Premium",
  description: "Achetez de l'électroménager premium reconditionnée jusqu'à -60% | Aspirateurs, Cuisine | Garantie 12 mois",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body className="min-h-full flex flex-col bg-white text-gray-900">
        {/* Trust Badges Bar */}
        <div className="bg-gradient-to-r from-teal-600 via-pink-500 to-orange-400 text-white text-sm">
          <div className="max-w-7xl mx-auto px-4 py-2 grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
            <div className="flex items-center justify-center gap-2">✓ Reconditionné en France</div>
            <div className="flex items-center justify-center gap-2">🛡️ Garantie 12 mois</div>
            <div className="flex items-center justify-center gap-2">↩️ 14j pour tester</div>
            <div className="flex items-center justify-center gap-2">🚚 Livraison rapide</div>
            <div className="flex items-center justify-center gap-2">💳 Paiement 3/4 fois</div>
          </div>
        </div>

        {/* Header */}
        <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4">
            {/* Top Bar */}
            <div className="flex justify-between items-center py-3 text-sm text-gray-600 border-b border-gray-100">
              <div className="flex gap-6">
                <a href="#" className="hover:text-blue-600">Pro</a>
                <a href="#" className="hover:text-blue-600">Contact</a>
              </div>
              <div className="flex gap-4">
                <a href="#" className="hover:text-blue-600">Mon compte</a>
                <a href="/panier" className="hover:text-blue-600">Panier</a>
              </div>
            </div>

            {/* Logo & Search */}
            <div className="flex items-center gap-8 py-4">
              <div className="text-lg md:text-2xl font-bold text-blue-600 whitespace-nowrap">AZUL PRO</div>
              <div className="flex-1">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Dreame, Dyson, Philips, Ninja..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm"
                  />
                  <button className="absolute right-3 top-2.5 text-gray-400">🔍</button>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex gap-6 py-3 text-sm font-medium border-t border-gray-100">
              <button className="hover:text-blue-600">Tous les produits</button>
              <div className="relative group">
                <button className="hover:text-blue-600">Aspirateurs</button>
              </div>
              <div className="relative group">
                <button className="hover:text-blue-600">Cuisine</button>
              </div>
              <div className="relative group">
                <button className="hover:text-blue-600">Marques</button>
              </div>
              <a href="#" className="hover:text-blue-600">Bons plans</a>
            </nav>
          </div>
        </header>

        {/* Main */}
        <main className="flex-1">{children}</main>

        {/* Footer */}
        <footer className="bg-gray-900 text-gray-300 mt-16">
          <div className="max-w-7xl mx-auto px-4 py-12">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
              <div>
                <h3 className="font-bold text-white mb-3">LA MARQUE</h3>
                <ul className="space-y-2 text-sm">
                  <li><a href="#" className="hover:text-white">Qui sommes-nous</a></li>
                  <li><a href="#" className="hover:text-white">Nos engagements</a></li>
                  <li><a href="#" className="hover:text-white">Recrutement</a></li>
                </ul>
              </div>
              <div>
                <h3 className="font-bold text-white mb-3">NOS PRODUITS</h3>
                <ul className="space-y-2 text-sm">
                  <li><a href="#" className="hover:text-white">Aspirateurs</a></li>
                  <li><a href="#" className="hover:text-white">Cuisine</a></li>
                  <li><a href="#" className="hover:text-white">Bons plans</a></li>
                </ul>
              </div>
              <div>
                <h3 className="font-bold text-white mb-3">INFORMATIONS</h3>
                <ul className="space-y-2 text-sm">
                  <li><a href="#" className="hover:text-white">Nous contacter</a></li>
                  <li><a href="#" className="hover:text-white">SAV</a></li>
                  <li><a href="#" className="hover:text-white">FAQ</a></li>
                </ul>
              </div>
              <div>
                <h3 className="font-bold text-white mb-3">SUIVEZ-NOUS</h3>
                <div className="flex gap-3 text-sm">
                  <a href="#" className="hover:text-white">Facebook</a>
                  <a href="#" className="hover:text-white">Instagram</a>
                </div>
              </div>
            </div>
            <div className="border-t border-gray-700 pt-8 text-center text-sm">
              <p>© 2026 Azul Pro - Électroménager d'Occasion Premium</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
