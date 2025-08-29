# Guide de Déploiement avec Terraform

Ce guide vous explique comment déployer l'infrastructure Eliza sur Azure en utilisant Terraform.

## 🔧 Prérequis

1. **Terraform** : [Téléchargez et installez Terraform](https://www.terraform.io/downloads)
2. **Azure CLI** : [Installez Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
3. **Azure Functions Core Tools** : [Installez les outils](https://docs.microsoft.com/azure/azure-functions/functions-run-local)

## 🚀 Étapes de déploiement

### 1. Connexion à Azure

```bash
# Connectez-vous à votre compte Azure
az login

# Vérifiez votre abonnement actif
az account show

# Si nécessaire, changez d'abonnement
az account set --subscription "your-subscription-id"
```

### 2. Déploiement de l'infrastructure

```bash
# Initialisez Terraform
terraform init

# Planifiez le déploiement (optionnel)
terraform plan

# Appliquez la configuration
terraform apply
```

Terraform vous demandera confirmation avant de créer les ressources. Tapez `yes` pour continuer.

### 3. Récupération des informations de déploiement

```bash
# Affichez toutes les sorties
terraform output

# Affichez une sortie spécifique
terraform output function_app_name
terraform output function_app_url

# Affichez les chaînes de connexion (sensibles)
terraform output -raw storage_connection_string
terraform output -raw sql_connection_string
```

### 4. Upload du modèle ML

```bash
# Remontez au répertoire racine du projet
cd ..

# Uploadez le modèle vers le blob storage
az storage blob upload \
  --account-name $(cd terraform && terraform output -raw storage_account_name) \
  --container-name models \
  --name model.ubj \
  --file model.ubj
```

### 5. Déploiement du code de la Function App

```bash
# Déployez votre code vers la Function App
func azure functionapp publish $(cd terraform && terraform output -raw function_app_name)
```

### 6. Test de l'API

```bash
# Testez l'endpoint de test
curl -X POST $(cd terraform && terraform output -raw function_app_url)/api/test

# Testez l'endpoint de prédiction
curl -X POST $(cd terraform && terraform output -raw function_app_url)/api/predict \
  -H "Content-Type: application/json" \
  -d '{"type": 1, "subtype": 1, "bedroomCount": 3, "habitableSurface": 120, "postCode": 1000, "province": 3, "locality": 1234, "bathroomCount": 2, "roomCount": 5, "buildingConstructionYear": 1990, "longitude": 4.3517, "latitude": 50.8503}'

# Testez l'historique
curl $(cd terraform && terraform output -raw function_app_url)/api/history
```

## 📦 Ressources créées

Terraform créera les ressources suivantes :

- **Groupe de ressources** : `rg-eliza-dev`
- **Compte de stockage** : Pour Azure Functions et le modèle ML
- **Conteneur blob** : `models` pour stocker le modèle XGBoost
- **Function App** : Application serverless Python
- **Serveur SQL Azure** : Base de données managée
- **Base de données SQL** : Stockage des prédictions
- **Web App Azure** : Déploiement du frontend

## 🔄 Mise à jour

Pour mettre à jour l'infrastructure :

```bash
cd terraform

# Appliquez les changements
terraform plan
terraform apply
```

## 🧹 Nettoyage

Pour supprimer toutes les ressources :

```bash
cd terraform

# Supprimez toutes les ressources
terraform destroy
```

⚠️ **Attention** : Cette commande supprimera définitivement toutes les ressources créées par Terraform, y compris les données.

## 🔐 Sécurité

```

### Stockage de l'état Terraform

Pour un environnement de production, configurez un backend distant pour stocker l'état Terraform :

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "terraformstate"
    container_name       = "tfstate"
    key                  = "eliza.terraform.tfstate"
  }
}
```

## 🚨 Dépannage

### Erreurs communes

1. **Nom de ressource déjà utilisé** : Les noms de Storage Account et SQL Server doivent être uniques globalement. Terraform utilise un suffixe aléatoire pour éviter ce problème.

2. **Droits insuffisants** : Assurez-vous que votre compte Azure a les droits Contributor sur l'abonnement.

3. **Quota dépassé** : Vérifiez les quotas de votre abonnement Azure si des ressources ne peuvent pas être créées.

### Commandes utiles

```bash
# Voir l'état des ressources
terraform state list

# Rafraîchir l'état
terraform refresh

# Voir les logs détaillés
TF_LOG=DEBUG terraform apply
```
