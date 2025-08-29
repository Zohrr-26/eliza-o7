# Eliza - API de Prédiction Immobilière sur Azure Functions

Ce projet déploie une API de prédiction de prix immobiliers en tant qu'Azure Function App. L'architecture est conçue pour être robuste, évolutive et maintenable, en tirant parti des services cloud natifs d'Azure.

## 🏛️ Architecture

- **Compute**: Azure Function App (Python) pour l'exécution du code sans serveur.
- **Base de données**: Azure SQL Database pour le stockage persistant de l'historique des prédictions.
- **Stockage du Modèle**: Azure Blob Storage pour héberger le modèle de Machine Learning (XGBoost), qui est chargé en mémoire au démarrage de la fonction.

Le code est structuré de manière modulaire pour séparer les responsabilités :
- `function_app.py`: Points d'entrée de l'API (endpoints).
- `ml_service.py`: Logique de chargement du modèle et de prédiction.
- `database.py`: Gestion de la connexion et des opérations sur la base de données.

---

## 🚀 Guide de Déploiement de A à Z

Suivez ces étapes pour déployer l'application sur Azure.

### Étape 1 : Prérequis

1.  Installez [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli).
2.  Installez [Azure Functions Core Tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local).
3.  Connectez-vous à votre compte Azure :
    ```bash
    az login
    ```
4.  Clonez ce dépôt et placez-vous à la racine du projet.

### Étape 2 : Définir les variables

Pour simplifier les commandes, définissez ces variables dans votre terminal.

```bash
export RESOURCE_GROUP=""
export LOCATION="francecentral"
export STORAGE_ACCOUNT="elizastorage$RANDOM" # Nom unique pour le compte de stockage (only lowercase letter)
export FUNCTION_APP="eliza-function-app"
export SQL_SERVER="eliza-sqlserver-$RANDOM" # Nom unique pour le serveur SQL
export SQL_DATABASE="eliza-db"
export SQL_ADMIN_USER="admin_username"
export SQL_ADMIN_PASSWORD="admin_password" # 3 types of char: upper-lower-digit-special
```

### Étape 3 : Créer les ressources Azure

1.  **Groupe de Ressources**
    ```bash
    az group create --name $RESOURCE_GROUP --location $LOCATION
    ```

2.  **Compte de Stockage** (utilisé par la Function App et pour le modèle)
    ```bash
    az storage account create --name $STORAGE_ACCOUNT --location $LOCATION --resource-group $RESOURCE_GROUP --sku Standard_LRS
    ```

3.  **Base de Données SQL**
    ```bash
    # Créer le serveur SQL
    az sql server create --name $SQL_SERVER --resource-group $RESOURCE_GROUP --location $LOCATION --admin-user $SQL_ADMIN_USER --admin-password $SQL_ADMIN_PASSWORD

    # Créer la base de données (S0 ou vCore)
    az sql db create --resource-group $RESOURCE_GROUP --server $SQL_SERVER --name $SQL_DATABASE --service-objective S0

    # Autoriser les services Azure à accéder au serveur SQL
    az sql server firewall-rule create --resource-group $RESOURCE_GROUP --server $SQL_SERVER --name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
    ```

4.  **Function App**
    ```bash
    az functionapp create --name $FUNCTION_APP --storage-account $STORAGE_ACCOUNT --consumption-plan-location $LOCATION --resource-group $RESOURCE_GROUP --runtime python --runtime-version 3.12 --functions-version 4
    ```

### Étape 4 : Gérer le Modèle avec Blob Storage

1.  **Créer un conteneur pour les modèles**
    ```bash
    az storage container create --name models --account-name $STORAGE_ACCOUNT
    ```

2.  **Uploader le modèle** (assurez-vous que `model.ubj` est à la racine)
    ```bash
    az storage blob upload --account-name $STORAGE_ACCOUNT --container-name models --name model.ubj --file model.ubj
    ```

### Étape 5 : Configurer la Function App

1.  **Récupérer les chaînes de connexion**
    ```bash
    # Chaîne de connexion du compte de stockage
    STORAGE_CONNECTION_STRING=$(az storage account show-connection-string --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP --query connectionString -o tsv)

    # Chaîne de connexion SQL
    SQL_CONNECTION_STRING="DRIVER={ODBC Driver 18 for SQL Server};\
    SERVER=tcp:${SQL_SERVER}.database.windows.net,1433;\
    DATABASE=${SQL_DATABASE};\
    UID=${SQL_ADMIN_USER};\
    PWD=${SQL_ADMIN_PASSWORD};\
    Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    ```

2.  **Appliquer les paramètres à la Function App**
    ```bash
    az functionapp config appsettings set --name $FUNCTION_APP --resource-group $RESOURCE_GROUP --settings \
        "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING" \
        "SQLALCHEMY_DATABASE_URI=$SQL_CONNECTION_STRING" \
        "AzureWebJobsStorage=$STORAGE_CONNECTION_STRING"
    ```

### Étape 6 : Déployer le code

Le fichier `.funcignore` à la racine du projet empêche l'upload du modèle `model.ubj` et d'autres fichiers inutiles.

```bash
func azure functionapp publish $FUNCTION_APP
```

### Étape 7 : Tester l'API

- **Endpoint de test (POST)**: Vérifie que le modèle se charge et effectue une prédiction.
  ```bash
  curl -X POST https://$FUNCTION_APP.azurewebsites.net/api/test
  ```

- **Endpoint de prédiction (POST)**: Envoyez vos propres données.
  ```bash
  curl -X POST https://$FUNCTION_APP.azurewebsites.net/api/predict \
       -H "Content-Type: application/json" \
       -d '{"type": 1, "subtype": 1, "bedroomCount": 3, "habitableSurface": 120, "postCode": 1000, "province": 3, "locality": 1234, "bathroomCount": 2, "roomCount": 5, "hasAttic": 0, "hasBasement": 1, "hasDressingRoom": 0, "diningRoomSurface": 15, "hasDiningRoom": 1, "buildingCondition": 2, "buildingConstructionYear": 1990, "facedeCount": 1, "floorCount": 2, "streetFacadeWidth": 8, "hasLift": 0, "floodZoneType": 0, "heatingType": 2, "hasHeatPump": 0, "hasPhotovoltaicPanels": 0, "hasThermicPanels": 0, "kitchenSurface": 12.0, "kitchenType": 2, "landSurface": 500.0, "hasLivingRoom": 1, "livingRoomSurface": 25.0, "hasGarden": 1, "gardenSurface": 200.0, "gardenOrientation": 2, "parkingCountIndoor": 0, "parkingCountOutdoor": 2, "hasAirConditioning": 0, "hasArmoredDoor": 1, "hasVisiophone": 0, "hasOffice": 0, "toiletCount": 2, "hasSwimmingPool": 0, "hasFireplace": 1, "hasTerrace": 1, "terraceSurface": 20, "terraceOrientation": 2, "epcScore": 3, "longitude": 4.3517, "latitude": 50.8503, "cadastralIncome": 1200.0, "primaryEnergyConsumptionPerSqm": 150.0}'
  ```

- **Endpoint d'historique (GET)**: Récupère les dernières prédictions.
  ```bash
  curl https://$FUNCTION_APP.azurewebsites.net/api/history
  ```
