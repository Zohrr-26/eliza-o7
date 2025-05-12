
import pandas as pd
import os
import json
import xgboost as xgb
import streamlit as st
import requests

def add_data(label: str, var): # add input_data or class
    for i, name in enumerate(labels[label]):
        if name == var:
            input_data[label] = i + 1
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

st.title("Estimation de prix immobilier")

tab1, tab2, tab3 = st.tabs(["Basic", "Bool", "Advanced"])
input_data = {}

#-----------------------------------------
#----------------- Tab 1 -----------------
#-----------------------------------------

with tab1:
    left, right = st.columns(2)

    is_house = left.selectbox("Type", ['Appartement', 'House'])

    if is_house == "Appartment":
        has_lift = st.checkbox('Lift')
    else: has_lift = 0

    surface = left.number_input("Surface habitable (m²)", min_value=0)
    chambres = left.number_input("Chambres", min_value=0, step=1)
    zip_code = right.number_input("Code Postal", min_value=1000)
    
    province_name = right.selectbox("Province", list(province.values()))
    for code, name in province.items():
        if name == province_name:
            input_data['province'] = code
            break

    locality = right.selectbox("Localité", labels['locality'])
    add_data('locality', locality)

    st.write('---------')

    sl, sm, sr = st.columns(3)
    facade = sl.number_input("Facades", min_value=0, step=1)
    toilet = sl.number_input("Toilettes", min_value=0, step=1)
    land_surface = sl.number_input("Surface de la propriété (m²)", min_value=0)
    bathroom = sm.number_input("Bathrooms", min_value=0, step=1)
    cadastre = sm.number_input("Cadastre Income", min_value=0, step=1)
    energy = sm.number_input("Consommation d'énergie par m2", min_value=0, step=1)

    flood_zone_type = sr.selectbox("Flood Zone", labels['floodZoneType'])
    heating_type = sm.selectbox("Heating Type", labels['heatingType'])
    garden_orientation = sr.selectbox("Garden Orientatione", labels['gardenOrientation'])
    epc_score = sl.selectbox("EPC Score", labels['epcScore'])
    building_condition = sr.selectbox("Building Condition", labels['buildingCondition'])

#----------------------------------------------------------------

    input_data['hasLift'] = has_lift
    add_data('buildingCondition', building_condition)
    add_data('floodZoneType', flood_zone_type)
    add_data('heatingType', heating_type)
    add_data('gardenOrientation', garden_orientation)
    add_data('epcScore', epc_score)
    input_data['type'] = 1 if is_house == "House" else 2
    input_data['habitableSurface'] = surface
    input_data['bedroomCount'] = chambres
    input_data['facedeCount'] = facade
    input_data['toiletCount'] = toilet
    input_data['landSurface'] = land_surface
    input_data['postCode'] = zip_code
    input_data['bathroomCount'] = bathroom
    input_data['cadastralIncome'] = cadastre
    input_data['primaryEnergyConsumptionPerSqm'] = energy

    input_data['adresse'] = -1

#-----------------------------------------
#----------------- Tab 2 -----------------
#-----------------------------------------

with tab2:
    st.write("Sélection des équipements (cochez si présent):")

    bool_cols = ['Attic', 'Basement', 'DressingRoom', 'DiningRoom',
        'HeatPump', 'PhotovoltaicPanels', 'ThermicPanels', 'LivingRoom', 'Garden',
        'parkingCountIndoor', 'parkingCountOutdoor', 'AirConditionning', 'ArmoredDoor', 'Visiophone',
        'Office', 'SwimmingPool', 'Fireplace', 'Terrace',]

    cols = st.columns(2)
    for key in bool_cols:
        checked = cols[0 if bool_cols.index(key) % 2 == 0 else 1].checkbox(key)
        input_data['has' + key] = checked

#-----------------------------------------
#----------------- Tab 3 -----------------
#-----------------------------------------

with tab3:
    st.write("Advanced Section")
    cols = st.columns(2)

    select_fields = {
        'Subtype': 'subtype',
        'Kitchen Type': 'kitchenType',
        'Terrace Orientation': 'terraceOrientation'
    }
    # for label_key, data_key in select_fields.items():
    #     choice = st.selectbox(label_key, labels[data_key])
    #     add_data(data_key, choice)
    
    numeric_fields = [
        ("Parking Indoor", 'parkingCountIndoor'),
        ("Parking Outdoor", 'parkingCountOutdoor'),
        ("Terrace Surface", 'terraceSurface'),
        ("Living Room Surface", 'livingRoomSurface'),
        ("Kitchen Surface", 'kitchenSurface'),
        ("Garden Surface", 'gardenSurface'),
        ("Dining Room Surface", 'diningRoomSurface'),
        ("Building Year", 'buildingConstructionYear'),
        ("Street Facade Width", 'streetFacadeWidth'),
    ]
    # for prompt, key in numeric_fields:
    #     val = st.number_input(prompt, min_value=0, step=1)
    #     input_data[key] = val

    fields = (
        [(label, key, 'select') for label, key in select_fields.items()] +
        [(label, key, 'numeric') for label, key in numeric_fields]
    )

    for idx, (label_text, data_key, kind) in enumerate(fields):
        col = cols[idx % 2]
        if kind == 'select':
            choice = col.selectbox(label_text, labels[data_key])
            add_data(data_key, choice) # need to add 1 somewhere
        else:
            val = col.number_input(label_text, min_value=0, step=1)
            input_data[data_key] = val
            
#-----------------------------------------
#---------------- SideBar-----------------
#-----------------------------------------

with st.sidebar:
    if st.button("Prediction"):

    #-----------------------------------------
    #--------------- FastAPI -----------------
    #-----------------------------------------

        url = "http://localhost:8555/predict"
        req = requests.post(url, json=input_data, timeout=5)

        if req.status_code == 200:
            price = req.json()["price"]
            st.write(f"price of the property: {price:,.0f} €")

        else:
            st.error(f"Erreur API {req.status_code}: {req.text}")