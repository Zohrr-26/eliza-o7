"""
Azure Functions App pour les prédictions de prix immobilier Eliza
"""
import azure.functions as func
import json
import logging
from models import New_ID
from ml_service import predict_price
from database import save_prediction, get_predictions_history, init_database

init_database()

app = func.FunctionApp()

#-------------------------------------------
#---------------- Predict ------------------
#-------------------------------------------

@app.route(route="predict", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def predict(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Please pass input data in the request body"}),
                status_code=400,
                mimetype="application/json"
            )

        prediction_data = New_ID(**req_body)
        predicted_price = predict_price(prediction_data)
        save_prediction(prediction_data, predicted_price)
        
        response = {
            "price": float(predicted_price),
            "environment": "azure"
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        logging.error(f"Validation error: {e}")
        return func.HttpResponse(
            json.dumps({"error": f"Invalid input data: {str(e)}"}),
            status_code=400,
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

#-------------------------------------------
#----------------- History -----------------
#-------------------------------------------

@app.route(route="history", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def history(req: func.HttpRequest) -> func.HttpResponse:    
    try:
        history_data = get_predictions_history(limit=13)
        
        response = {
            "history": history_data,
            "count": len(history_data),
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"History retrieval error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to retrieve history"}),
            status_code=500,
            mimetype="application/json"
        )
    
#-------------------------------------------
#--------------- test useless --------------
#-------------------------------------------

@app.route(route="test", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def test(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Données d'exemple pour test
        test_data = {
            'type': 1,
            'subtype': 1,
            'bedroomCount': 3,
            'bathroomCount': 2,
            'province': 3,
            'locality': 1234,
            'postCode': 1000,
            'habitableSurface': 120.0,
            'roomCount': 5,
            'hasAttic': 0,
            'hasBasement': 1,
            'hasDressingRoom': 0,
            'diningRoomSurface': 15,
            'hasDiningRoom': 1,
            'buildingCondition': 2,
            'buildingConstructionYear': 1990,
            'facedeCount': 1,
            'floorCount': 2,
            'streetFacadeWidth': 8,
            'hasLift': 0,
            'floodZoneType': 0,
            'heatingType': 2,
            'hasHeatPump': 0,
            'hasPhotovoltaicPanels': 0,
            'hasThermicPanels': 0,
            'kitchenSurface': 12.0,
            'kitchenType': 2,
            'landSurface': 500.0,
            'hasLivingRoom': 1,
            'livingRoomSurface': 25.0,
            'hasGarden': 1,
            'gardenSurface': 200.0,
            'gardenOrientation': 2,
            'parkingCountIndoor': 0,
            'parkingCountOutdoor': 2,
            'hasAirConditioning': 0,
            'hasArmoredDoor': 1,
            'hasVisiophone': 0,
            'hasOffice': 0,
            'toiletCount': 2,
            'hasSwimmingPool': 0,
            'hasFireplace': 1,
            'hasTerrace': 1,
            'terraceSurface': 20,
            'terraceOrientation': 2,
            'epcScore': 3,
            'longitude': 4.3517,
            'latitude': 50.8503,
            'cadastralIncome': 1200.0,
            'primaryEnergyConsumptionPerSqm': 150.0
        }
        
        # Effectuer la prédiction avec les données de test
        prediction_data = New_ID(**test_data)
        predicted_price = predict_price(prediction_data)
        
        response = {
            "test_result": "success",
            "predicted_price": float(predicted_price),
            "test_data": test_data
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Test failed: {e}")
        return func.HttpResponse(
            json.dumps({
                "test_result": "failed",
                "error": str(e),
            }),
            status_code=500,
            mimetype="application/json"
        )
