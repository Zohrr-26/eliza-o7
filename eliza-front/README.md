

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
│   Frontend      │ ───────────────────▶│.    Backend      │
│  (Streamlit)    │                     │  (FastAPI + xgb) │
└─────────────────┘                     └──────────────────┘
       ▲                                    │
       │                                    │
       │             GET /history           │
       └────────────────────────────────────┘
```

- **`eliza-back.py`** (désormais remplacé par une azure function / lambda)
  - Sert le modèle XGBoost (format UBJSON `.ubj`)  
  - Expose deux endpoints :
    - `POST /predict` : reçoit un JSON de features, renvoie `{ "price": float }` 
    - `GET  /history` : renvoie les 13 dernières entrées de l’historique  
- **`eliza-front.py`**  
  - Interface utilisateur Streamlit  
  - Collecte des inputs, appel de l’API, affichage du prix estimé  
  - Affiche l’historique
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

⸻

📁 Structure du projet
```text
eliza-o7/
├── eliza-back.py       # Backend FastAPI + chargement du modèle + historique
├── eliza-front.py      # Frontend Streamlit
├── eliza_new_id.py     # Classe New_ID pour orchestrer les features
├── model.ubj           # Modèle XGBoost en format binaire UBJSON
├── model-label.json    # Labels JSON pour factorisation des catégories
└── requirements.txt    # Liste des dépendances Python
```
⸻

