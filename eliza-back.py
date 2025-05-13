import os

import uvicorn
import pandas as pd
import xgboost as xgb
from fastapi import FastAPI, Body

from eliza_new_id import New_ID

app = FastAPI()

#------------------------------------------------

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "model.ubj")

booster = xgb.Booster()
booster.load_model(model_path)
print("model loaded as booster")

#-----------------------------------------
#------------ History CSV ----------------
#-----------------------------------------

csv_path = os.path.join(current_dir, "history.csv")

if not os.path.exists(csv_path):
    empty_df = pd.DataFrame(columns=New_ID.fields)
    empty_df.to_csv(csv_path, index=False, encoding="utf-8")

history = pd.read_csv(csv_path, encoding="utf-8")

#-----------------------------------------
#------------ Predict Price --------------
#-----------------------------------------

@app.post('/predict')
def predict(input_data: dict = Body(...)): # convert json into dict

    new_id = New_ID(**input_data)
    model_input = new_id.to_list()

    df_input = pd.DataFrame([model_input], columns=New_ID.fields)

    dmat = xgb.DMatrix(df_input)
    id_pred = booster.predict(dmat)[0]

## add columns price, add id_pred to rows
    df_input['price'] = id_pred
    df_input.to_csv(csv_path, mode='a', headers=False)

    return {"price": float(id_pred)} # return a json / dict

#-----------------------------------------
#---------- Store Prediction -------------
#-----------------------------------------

@app.get('/history')
def history():
    history = pd.read_csv(csv_path, encoding="utf-8")
    head_13 = history.head(13).values.tolist()
    return {"rows": head_13}

#-----------------------------------------
#----- Start Asgi Server Uvicorn ---------
#-----------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8555)

