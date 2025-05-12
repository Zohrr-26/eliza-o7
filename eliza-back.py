import os
import pandas as pd
import xgboost as xgb
from fastapi import FastAPI, Body
import uvicorn

from eliza_new_id import New_ID

app = FastAPI()

#----------------------------------------------------------------

def load_model(path: str):
    booster = xgb.Booster()
    booster.load_model(path)
    return booster

#----------------------------------------------------------------

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "model.ubj")

@app.post('/predict')
def predict(input_data: dict = Body(...)): # convert json into dict

    new_id = New_ID(**input_data)
    model_input = new_id.to_list()

    booster = load_model(model_path)
    print("model loaded as booster")

    df_input = pd.DataFrame([model_input], columns=New_ID.fields)
    dmat = xgb.DMatrix(df_input)
    id_pred = booster.predict(dmat)[0]
    return {"price": float(id_pred)} # return a json / dict

#-----------------------------------------
#----- Start Asgi Server Uvicorn ---------
#-----------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8555)