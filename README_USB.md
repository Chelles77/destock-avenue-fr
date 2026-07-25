# 🚀 ReventePro V4 - Portable sur Clé USB

## 📋 Contenu de la clé USB

```
CLÉ USB
├── ReventePro_V4/                    ← Dossier principal
│   ├── launch_reventepro.bat         ← ⭐ Lancer l'app (clic rapide)
│   ├── install_dependencies.bat      ← 📦 Installer les dépendances
│   ├── requirements.txt              ← Liste des dépendances Python
│   ├── app/                          ← Code source
│   ├── templates/                    ← Pages HTML
│   ├── static/                       ← CSS, JS, images
│   ├── app.db                        ← Base de données
│   └── ... (autres fichiers)
└── README_USB.md                     ← Ce fichier
```

## ⚙️ PREMIÈRE UTILISATION (une seule fois)

### 1️⃣ Installez Python (si pas déjà fait)
- Téléchargez Python 3.9+ depuis : https://www.python.org/downloads/
- ⚠️ **IMPORTANT** : Cochez "Add Python to PATH" pendant l'installation

### 2️⃣ Installez les dépendances
- Double-cliquez : `install_dependencies.bat`
- Attendez que l'installation se termine
- ✅ Vous verrez : "INSTALLATION RÉUSSIE !"

---

## 🎯 UTILISATION QUOTIDIENNE

### Pour lancer l'app :
1. **Double-cliquez** : `launch_reventepro.bat`
2. Attendez le message : `✅ Lancement de ReventePro V4...`
3. Ouvrez votre navigateur : **http://127.0.0.1:5000**
4. Connectez-vous avec vos identifiants

### Pour arrêter l'app :
- Fermez la fenêtre du terminal (ou Ctrl+C)

---

## 💡 Points importants

✅ **Fonctionne sur n'importe quelle clé USB** (D:, E:, F:, etc.)  
✅ **Fonctionne sur n'importe quel ordinateur** (avec Python installé)  
✅ **Les données sont sauvegardées** dans `app.db`  
✅ **Pas besoin de terminal** - Juste double-cliquer sur le batch  

---

## ⚠️ Troubleshooting

### Erreur : "Python n'est pas installé"
→ Installez Python 3.9+ (cochez "Add Python to PATH")

### Erreur : "Port 5000 déjà utilisé"
→ Un autre programme utilise le port. Fermez l'autre app ou changez le port dans le batch

### L'app se ferme immédiatement
→ Vérifiez qu'il n'y a pas d'erreur dans la fenêtre (lisez bien les messages)

---

## 📱 Accès à l'app

- **Local** : http://127.0.0.1:5000
- **Autre ordinateur du réseau** : http://[votre_ip]:5000
  (ex: http://192.168.1.100:5000)

---

**Version** : ReventePro V4  
**Créé** : 2026-07-18
