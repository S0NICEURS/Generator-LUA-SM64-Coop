import subprocess
import importlib
import json
import os

# Chemin vers le fichier JSON
json_file = 'modules_installed.json'

# Fonction pour vérifier et installer les modules
def check_and_install_modules(modules):
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"{module} is already installed.")
        except ImportError:
            print(f"{module} is not installed, install in progress...")
            subprocess.check_call(['pip', 'install', module])

# Liste des modules nécessaires
required_modules = [
    'tkinter',
    'ctypes',
    
]

# Vérifier si le fichier JSON existe
if not os.path.exists(json_file):
    # Vérifier et installer les modules nécessaires
    check_and_install_modules(required_modules)
    
    # Créer le fichier JSON pour indiquer que les modules sont installés
    with open(json_file, 'w') as file:
        json.dump({"modules_installed": True}, file)

# Lancer le script Python désiré
subprocess.run(['python', 'Generator LUA [CS] v1.2.py'])

