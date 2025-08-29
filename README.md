# 🏠 Eliza - Prédicteur de Prix Immobilier sur Azure

Une solution complète de **machine learning en production** pour la prédiction de prix immobiliers belges, déployée sur Azure avec Terraform.

![Azure](https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-623CE4?style=for-the-badge&logo=terraform&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

👉 Testez l'application déployée ici :  
---
🔗 [https://eliza-streamlit.azurewebsites.net](https://eliza-streamlit.azurewebsites.net) 

## 🎯 Vue d'ensemble du projet

Ce projet démontre un **pipeline ML complet de A à Z** :

1. **🕷️ Scraping de données** immobilières belges
2. **📊 Preprocessing et feature engineering** du dataset  
3. **🤖 Entraînement d'un modèle XGBoost** pour la prédiction de prix

---
- sur ce dépot actuellement:

4. **🚀 Déploiement en production** avec une architecture cloud-native sur Azure
5. **🌐 Interface utilisateur** intuitive avec Streamlit
6. **⚡ Infrastructure as Code** avec Terraform pour un déploiement reproductible


## 🏗️ Architecture

### Composants principaux :

- **Frontend** : Interface Streamlit containerisée pour la saisie utilisateur
- **Backend** : Azure Functions exposant une API REST pour les prédictions
- **Base de données** : Azure SQL Database pour l'historique des estimations
- **Stockage** : Azure Blob Storage pour le modèle ML (format UBJSON)
- **Infrastructure** : Déployement automatisé avec Terraform

---

## 📁 Structure du projet

```
📦 Azure-TF/
├── 🤖 model.ubj                 # Modèle XGBoost entraîné (format UBJSON)
├── 🌐 eliza-front/              # Frontend Streamlit
│   ├── Dockerfile
│   ├── eliza-front.py           # Interface utilisateur
│   ├── model-label.json         # Mappings des features catégorielles
│   ├── requirements.txt
│   └── README.md
├── ⚡ eliza-o7/                 # Backend Azure Functions
│   ├── function_app.py          # Endpoints API (/predict, /history)
│   ├── ml_service.py            # Service de prédiction ML
│   ├── database.py              # Connexion et opérations DB
│   ├── models.py                # Modèles de données Pydantic
│   ├── host.json                # Configuration Azure Functions
│   ├── requirements.txt
│   └── README.md
└── 🏗️ terraform/               # Infrastructure as Code
    ├── main.tf                  # Ressources Azure principales
    ├── variables.tf             # Variables de configuration
    ├── locals.tf                # Valeurs calculées
    ├── outputs.tf               # Sorties du déploiement
    └── README.md
```

---

## 🚀 Déploiement rapide

### Prérequis

- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) installé et configuré
- [Terraform](https://www.terraform.io/downloads) ≥ 1.0
- [Azure Functions Core Tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local)
- [Docker](https://docs.docker.com/get-docker/) pour le frontend

### 1. Cloner le projet

```bash
git clone <votre-repo>
cd Azure-TF
```

### 2. Configurer l'authentification Azure

```bash
# Connexion à Azure
az login

# Configurer les variables d'environnement pour Terraform
export ARM_SUBSCRIPTION_ID="your-subscription-id"
export ARM_TENANT_ID="your-tenant-id"

# Variables pour le projet
export TF_VAR_project_name="eliza"
export TF_VAR_environment="prod"
export TF_VAR_sql_admin_password="VotreMotDePasseSecure123!"
```

### 3. Déployer l'infrastructure

```bash
cd terraform/

# Initialiser Terraform
terraform init

# Déployer
terraform plan
terraform apply
```

### 4. Déployer le backend (Function App)

```bash
cd ../eliza-o7/

# Publier la Function App
func azure functionapp publish <nom-function-app-généré>
```

### 5. Déployer le frontend (Container)

```bash
cd ../eliza-front/

# Construire et pousser l'image Docker
docker buildx build --platform linux/arm64,linux/amd64 -t <votre-registry>/eliza-front:latest --push .

# Mettre à jour l'Azure Container Instance via Terraform
```

---

## 🔧 Configuration

### Variables Terraform principales

| Variable | Description | Exemple |
|----------|-------------|---------|
| `project_name` | Nom du projet | `"eliza"` |
| `environment` | Environnement de déploiement | `"prod"` |
| `location` | Région Azure | `"France Central"` |
| `sql_admin_password` | Mot de passe admin SQL | `"SecurePass123!"` |
| `allowed_ip_addresses` | IPs autorisées pour SQL | `[0.0.0.0"]` |

### API Endpoints

- **POST** `/api/predict` - Prédiction de prix immobilier
- **GET** `/api/history` - Historique des prédictions

#### Exemple d'appel API :

```bash
curl -X POST https://your-function-app.azurewebsites.net/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "property_type": "HOUSE",
    "room_count": 3,
    "area": 120,
    "land_area": 500,
    "zip_code": "1000",
    "locality": "Brussels"
  }'
```

---

## 🔍 Fonctionnalités

### Frontend (Streamlit)
- 🎨 Interface utilisateur intuitive
- 📝 Formulaire de saisie des caractéristiques du bien
- 💰 Affichage du prix estimé en temps réel
- 📊 Historique des estimations précédentes
- 📱 Interface responsive

### Backend (Azure Functions)
- ⚡ API REST
- 🤖 Modèle XGBoost (format UBJSON)
- 🗄️ Persistance en base de données

### Infrastructure (Terraform)
- 🏗️ Infrastructure as Code complète
- 🔄 Déploiement reproductible



## 📝 Documentation détaillée

Chaque composant dispose de sa propre documentation :

- [📖 Frontend (Streamlit)](./eliza-front/README.md)
- [📖 Backend (Azure Functions)](./eliza-o7/README.md)
- [📖 Infrastructure (Terraform)](./terraform/README.md)

