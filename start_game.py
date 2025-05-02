"""
Script de démarrage pour le jeu Puissance 4.
Ce script vérifie la configuration et démarre le serveur.
"""

import os
import sys
import webbrowser
import threading
import time
import importlib.util

def check_module(module_name):
    """Vérifie si un module est installé."""
    return importlib.util.find_spec(module_name) is not None

def install_flask():
    """Installe Flask si nécessaire."""
    print("Installation de Flask...")
    os.system(f"{sys.executable} -m pip install flask")
    print("Flask installé avec succès.")

def open_browser():
    """Ouvre le navigateur après un court délai."""
    time.sleep(2)
    url = "http://127.0.0.1:5000"
    webbrowser.open(url)
    print("Navigateur ouvert à l'adresse:", url)

def check_files():
    """Vérifie si tous les fichiers nécessaires sont présents."""
    required_files = ["app.py", "heuristic.py", "index.html", "script.js", "styles.css"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("Erreur: Fichiers manquants:", ", ".join(missing_files))
        print("Assurez-vous que tous les fichiers sont dans le même dossier.")
        return False
    return True

def start_game():
    """Démarre le jeu."""
    # Vérifier que Flask est installé
    if not check_module("flask"):
        print("Flask n'est pas installé.")
        install_flask()
    
    # Vérifier les fichiers
    if not check_files():
        return
    
    print("\n=== Démarrage du jeu Puissance 4 ===\n")
    print("Serveur en cours de démarrage...")
    
    # Ouvrir le navigateur automatiquement
    threading.Thread(target=open_browser).start()
    
    # Exécuter le serveur Flask
    os.system(f"{sys.executable} app.py")

if __name__ == "__main__":
    start_game()