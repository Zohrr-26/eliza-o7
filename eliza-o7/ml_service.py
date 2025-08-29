"""
Services pour la gestion du modèle XGBoost
"""
import xgboost as xgb
import numpy as np
from azure.storage.blob import BlobServiceClient
import os
import logging
from models import New_ID

# Variables globales pour le cache du modèle
booster = None

def load_model():
    """Charge le modèle XGBoost depuis Azure Blob Storage"""
    
    global booster
    if booster is not None:
        return booster

    logging.info("Tentative de chargement du modèle XGBoost...")
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    
    temp_booster = xgb.Booster()

    try:

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container="models", blob="model.ubj")
        
        downloader = blob_client.download_blob()
        model_bytes = downloader.readall()
        
        temp_booster.load_model(bytearray(model_bytes))
        logging.info("Modèle chargé avec succès depuis le blob en mémoire.")

        booster = temp_booster
        return booster

    except Exception as e:
        logging.error(f"Erreur lors du chargement du modèle : {e}")
        raise

def predict_price(input_data) -> float:
    """Effectue une prédiction de prix"""
    try:

        model = load_model()

        if isinstance(input_data, New_ID):
            new_id = input_data
        else:
            new_id = New_ID(**input_data)

        model_input = new_id.to_list()
        
        # Prédiction
        model_input = np.array([model_input], dtype=float)
        dmat = xgb.DMatrix(model_input, feature_names=New_ID.fields)
        prediction = model.predict(dmat)[0]
        
        return float(prediction)
        
    except Exception as e:
        logging.error(f"Error in prediction: {str(e)}")
        raise e

