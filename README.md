

# Eliza o7

Une application web de **prédiction de prix immobilier** qui combine un backend FastAPI pour la prédiction et un frontend Streamlit pour l’interface utilisateur.

---

## 🎯 Fonctionnalités

- **Collecte d’informations** détaillées sur un bien (type, surface, équipements, etc.) via une interface Streamlit  
- **Prédiction en temps réel** du prix à l’aide d’un modèle XGBoost pré-entraîné  
- **Historique des estimations** sauvegardé dans un fichier CSV et consultable depuis la sidebar  
- **Système de labels** JSON pour factoriser les variables catégorielles sans recourir à `pickle` ou `joblib`

---

## 🚀 Architecture

```text
┌─────────────────┐     POST /predict   ┌──────────────────┐
│   Frontend      │ ───────────────────▶│   Backend        │
│  (Streamlit)    │                     │(FastAPI + xgb)   │
└─────────────────┘                     └──────────────────┘
       ▲                                    │
       │                                    │
       │             GET /history           │
       └────────────────────────────────────┘
```

- **`eliza-back.py`**  
  - Sert le modèle XGBoost (format UBJSON `.ubj`)  
  - Expose deux endpoints :
    - `POST /predict` : reçoit un JSON de features, renvoie `{ "price": float }`, et append la ligne au `history.csv`  
    - `GET  /history` : renvoie les 13 dernières entrées de l’historique  
- **`eliza-front.py`**  
  - Interface utilisateur Streamlit  
  - Collecte des inputs, appel de l’API, affichage du prix estimé  
  - Affiche l’historique et permet de recharger un ancien jeu de données  
- **`eliza_new_id.py`**  
  - Classe `New_ID` qui gère l’ordre des variables, les valeurs par défaut et la conversion en liste pour le modèle  
- **`model.ubj`** & **`model-label.json`**  
  - Fichiers du modèle entraîné et des mappings de labels pour les features catégorielles  

---

## 📦 Prérequis

- Python ≥ 3.9  
- Pip  

### Dépendances principales

- `fastapi`, `uvicorn[standard]`  
- `streamlit`  
- `xgboost`, `pandas`, `requests`

---

## ⚙️ Installation

1. **Cloner le dépôt**  
   ```bash
   git clone https://github.com/ton-utilisateur/eliza-o7.git
   cd eliza-o7

	2.	Créer et activer un environnement virtuel

python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.venv\Scripts\activate       # Windows


	3.	Installer les dépendances

pip install -r requirements.txt



⸻

🛠️ Lancement en local

Backend (FastAPI + Uvicorn)

uvicorn eliza-back:app --host 0.0.0.0 --port 8555

	•	L’API sera disponible sur http://localhost:8555
	•	Docs interactives Swagger : http://localhost:8555/docs

Frontend (Streamlit)

Ouvrir un nouveau terminal (avec le même virtuel activé) :

streamlit run eliza-front.py --server.port 8501

	•	L’interface s’ouvrira automatiquement ou via http://localhost:8501

⸻

🎛️ Configuration

	•	model.ubj : fichier UBJSON du modèle XGBoost
	•	model-label.json : mapping de tous les labels catégoriels généré par pd.factorize
	•	history.csv : créé automatiquement à la première prédiction, contient l’historique des inputs + prix
	•	Pour changer le port ou l’adresse, modifie les variables --port et --host dans la commande uvicorn

⸻

📁 Structure du projet
```text
eliza-o7/
├── eliza-back.py       # Backend FastAPI + chargement du modèle + historique CSV
├── eliza-front.py      # Frontend Streamlit
├── eliza_new_id.py     # Classe New_ID pour orchestrer les features
├── model.ubj           # Modèle XGBoost en format binaire UBJSON
├── model-label.json    # Labels JSON pour factorisation des catégories
├── history.csv         # (créé à la volée) historique des prédictions
└── requirements.txt    # Liste des dépendances Python
```
⸻

Made with ❤️ pour l’estimation immobilière rapide !

