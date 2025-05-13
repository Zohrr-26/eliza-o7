
import os
import json
import requests

import streamlit as st
import pandas as pd

def add_data(label, var): # add id_data or class
    for i, name in enumerate(labels[label]):
        if name == var:
            id_data[label] = i + 1
            break

#-----------------------------------------
#----------------- SETUP -----------------
#-----------------------------------------

current_dir = os.path.dirname(os.path.abspath(__file__))

json_file = os.path.join(current_dir, "model-label.json")

with open(json_file, "r", encoding="utf-8") as f:
    labels = json.load(f); print("json loaded as labels")

province = {
    5:  'Brussels',

    11: 'Antwerp',
    12: 'Flemish Brabant',
    13: 'East Flanders',
    14: 'West Flanders',
    15: 'Limburg',

    21: 'Luxembourg',
    22: 'Liège',
    23: 'Walloon Brabant',
    24: 'Namur',
    25: 'Hainaut',
}

#-----------------------------------------
#-----------------------------------------
#-------------- Streamlit ----------------
#-----------------------------------------
#-----------------------------------------

st.markdown("""
    <style>
    /* Cible le premier (et ici unique) bouton dans un stButton container */
            
    div.stButton > button:first-child {
        background-color: #FF5722 !important;  /* couleur vive */
        color: white !important;               /* texte contrasté */
        font-size: 1.2rem !important;          /* taille de police plus grande */
        height: 3.5em !important;              /* hauteur accrue */
        width: 100% !important;                /* pleine largeur */
        border-radius: 0.75rem !important;     /* coins arrondis */
        border: 2px solid #E64A19 !important;  /* bordure sombre pour contraste */
    }
            
    /* Au hover, on peut ajouter un effet visuel */
    div.stButton > button:first-child:hover {
        background-color: #E64A19 !important;
    }
    </style>
""", unsafe_allow_html=True)

#-----------------------------------------
#---------------- Setup ------------------
#-----------------------------------------

st.title("Real estate price estimate")

tab1, tab2 = st.tabs(["Basic", "Advanced"])
id_data = {}

#-----------------------------------------
#----------------- Tab 1 -----------------
#-----------------------------------------

with tab1:
    left, right = st.columns(2)

    province_name = left.selectbox("Province", list(province.values()))
    for code, name in province.items():
        if name == province_name:
            id_data['province'] = code
            break
    
    zip_code = left.number_input("Code Postal", min_value=1000)
    
    locality = right.selectbox("Localité", labels['locality'])
    add_data('locality', locality)

    surface = right.number_input("Surface habitable (m²)", min_value=0)

#-----------------------------------------

    is_house = st.selectbox("Type", ['Apartment', 'House'])

    hl, hr = st.columns(2)

    if is_house == "Apartment":
        has_lift = st.checkbox('Lift')
        garden = 0
        pool = 0
        st.write('-----')

    else: 
        has_lift = 0
        pool = hr.checkbox('Swimming Pool')
        garden = hl.checkbox('Garden')
        id_data['hasGarden'] = garden

        if id_data.get('hasGarden'):
            id_data['gardenSurface'] = hl.number_input(
                "Garden Surface (m²)", min_value=0, key="gardenSurface")
        st.write('-----')

    left, right = st.columns(2)

    chambres = left.slider("Chambres", min_value=0, max_value=9, step=1)
    facade = right.slider("Facades", min_value=0, max_value=4, step=1)
    bathroom = left.slider("Bathrooms", min_value=0, max_value=5, step=1)
    toilet = right.slider("Toilettes", min_value=0, max_value=5, step=1)

#----------------------------------------------------------------

    id_data['hasLift'] = has_lift
    id_data['type'] = 1 if is_house == "House" else 2
    id_data['habitableSurface'] = surface
    id_data['bedroomCount'] = chambres
    id_data['facedeCount'] = facade
    id_data['toiletCount'] = toilet
    id_data['postCode'] = zip_code
    id_data['bathroomCount'] = bathroom
    id_data['hasSwimmingPool'] = pool

    id_data['adresse'] = -1

#-----------------------------------------
#----------------- Tab 2 -----------------
#-----------------------------------------

with tab2:

    cols = st.columns(2)
    
    bool_cols = [
        'Attic', 'Basement', 'DressingRoom', 'DiningRoom',
        'HeatPump', 'PhotovoltaicPanels', 'ThermicPanels',
        'parkingCountIndoor', 'parkingCountOutdoor',
        'AirConditionning', 'ArmoredDoor', 'Visiophone',
        'Office', 'Fireplace', 'Terrace', 'LivingRoom',
    ]
    for idx, key in enumerate(bool_cols):
        col = cols[idx % 2]
        checked = col.checkbox(key)
        id_data['has' + key] = checked

    st.write("---")

    if id_data.get('hasparkingCountIndoor'):
        id_data['parkingCountIndoor'] = st.number_input(
            "Parking Indoor Count", min_value=0, key="parkingIndoorCount"
        )
    if id_data.get('hasparkingCountOutdoor'):
        id_data['parkingCountOutdoor'] = st.number_input(
            "Parking Outdoor Count", min_value=0, key="parkingOutdoorCount"
        )
    if id_data.get('hasTerrace'):
        id_data['terraceSurface'] = st.number_input(
            "Terrace Surface (m²)", min_value=0, key="terraceSurface"
        )    
    if id_data.get('hasLivingRoom'):
        id_data['livingRoomSurface'] = st.number_input(
            "Living room Surface (m²)", min_value=0, key="livingRoomSurface"
        )    
    if id_data.get('hasDiningRoom'):
        id_data['diningRoomSurface'] = st.number_input(
            "Dining room Surface (m²)", min_value=0, key="diningRoomSurface"
        )

    numeric_fields = [
        ("Kitchen Surface", 'kitchenSurface'),
        ("Building Year", 'buildingConstructionYear'),
        ("Street Facade Width", 'streetFacadeWidth'),
        ("Property Land Surface (m²)", 'landSurface'),
        ("Cadastre Income", 'cadastralIncome'),
        ("Energy Consumption per m²", 'primaryEnergyConsumptionPerSqm'),
    ]
    for label, key in numeric_fields:
        id_data[key] = st.number_input(label, min_value=0, step=1)

    select_fields = {
        'Subtype': 'subtype',
        'Kitchen Type': 'kitchenType',
        'Terrace Orientation': 'terraceOrientation',
        'Flood Zone': 'floodZoneType',
        'Heating Type': 'heatingType',
        'Garden Orientation': 'gardenOrientation',
        'EPC Score': 'epcScore',
        'Building Condition': 'buildingCondition'
    }
    for label, data_key in select_fields.items():
        choice = st.selectbox(label, labels[data_key])
        add_data(data_key, choice)

#-----------------------------------------
#---------------- SideBar-----------------
#-----------------------------------------

with st.sidebar:
    if st.button("Prediction"):

    #-----------------------------------------
    #--------------- FastAPI -----------------
    #-----------------------------------------

        prediction_url = "https://eliza-o7.onrender.com/predict"
        req = requests.post(prediction_url, json=id_data, timeout=5)

        if req.status_code == 200:
            price = req.json()["price"]
            st.write(f"price of the property: {price:,.0f} €")

        else:
            st.error(f"Erreur API {req.status_code}: {req.text}")

    st.title('History:')

    history_url = "https://eliza-o7.onrender.com/history"
    history = requests.get(history_url, timeout=5)

    for row in history['rows']:
        st.write(row)
    
    st.write("555 : locality : price")
    st.write("666 : bruxelles : 150.000")