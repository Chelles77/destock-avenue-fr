import os

# Architecture Professionnelle ReventePro V4
structure = {
    "app": [
        "__init__.py",      # Factory pattern
        "models.py",        # DB Schema
        "extensions.py",    # DB, LoginManager instances
        "config.py",        # Configs (Dev/Prod)
        # Blueprints
        "auth/__init__.py", "auth/routes.py", "auth/models.py",
        "dashboard/__init__.py", "dashboard/routes.py",
        "inventory/__init__.py", "inventory/routes.py", "inventory/utils.py",
        "sales/__init__.py", "sales/routes.py",
        "purchases/__init__.py", "purchases/routes.py",
        "finance/__init__.py", "finance/routes.py",
    ],
    "static": ["css/style.css", "js/main.js", "js/charts.js"],
    "templates": ["base.html", "macros.html"],
    "instance": [],
    "uploads": []
}

def create_project():
    base = os.path.dirname(os.path.abspath(__file__))
    print(f"🚀 Initialisation de ReventePro V4 dans : {base}\n")
    
    for folder, files in structure.items():
        dir_path = os.path.join(base, folder)
        os.makedirs(dir_path, exist_ok=True)
        print(f" {folder}/")
        
        for item in files:
            if "/" in item:
                sub, filename = item.rsplit("/", 1)
                sub_path = os.path.join(dir_path, sub)
                os.makedirs(sub_path, exist_ok=True)
                file_path = os.path.join(sub_path, filename)
            else:
                file_path = os.path.join(dir_path, item)
            
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    if item.endswith('.py'):
                        f.write("# ReventePro V4 Module\n")
                    elif item.endswith('.css'):
                        f.write("/* ReventePro V4 Styles */\n:root { --primary: #2563EB; }\n")
                    elif item.endswith('.html'):
                        f.write("<!DOCTYPE html>\n<html lang='fr'><body></body></html>\n")
                print(f"   ✨ {item}")

if __name__ == "__main__":
    create_project()
    print("\n✅ Projet V4 prêt ! Ouvrez le terminal et lancez 'pip install flask flask-login flask-sqlalchemy'")