
import os
import json
import requests

import streamlit as st

def add_data(label, var): # add id_data or class
    for i, name in enumerate(labels[label]):
        if name == var:
            id_data[label] = i + 1 # good if 0 but need +1 for the model
            break

def update_zip():
    """
    change zip code when the user choose a locality
    """
    z = str(st.session_state.zip)
    st.session_state.zip = labels[z]
    pass

def update_locality():
    """
    change locality when the use change the zip code
    """
    pass

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

    left.selectbox("Province", list(province.values()), key='province')
    for code, name in province.items():
        if name == st.session_state.province:
            id_data['province'] = code
            break
    
    left.number_input("Postal Code", 
                      min_value=0, 
                      key='zip_code',
                      ) ## on_change=update_locality ## and province
    
    right.selectbox("Locality",
                     labels['locality'], 
                     key='locality',
                     ) ## on_change=update_zip ## and province
    
    add_data('locality', st.session_state.locality)

    right.number_input("Living Space (m²)", min_value=0, key='surface')

#-----------------------------------------

    st.selectbox("Type", ['Apartment', 'House'], key='type')

    hl, hr = st.columns(2)

    if st.session_state.type == "Apartment":
        st.checkbox('Lift', key='hasLift')
        st.session_state.garden = 0
        st.session_state.pool = 0
        st.write('-----')

    else: 
        st.session_state.hasLift = 0
        hl.checkbox('Swimming Pool', key="pool")
        hr.checkbox("Garden", key="hasGarden")
        id_data["hasGarden"] = st.session_state.hasGarden

        if id_data.get('hasGarden'):

            id_data['gardenSurface'] = hr.number_input(
                "Garden Surface (m²)", min_value=0, key="gardenSurface")
                
            id_data['tgardenOrientation'] = hr.selectbox(
                'Garden Orientation', labels['gardenOrientation'])  

        st.write('-----')

    left, right = st.columns(2)

    left.slider("Bedroom", min_value=0, max_value=9, step=1, key='bedroomCount')
    right.slider("Facade", min_value=0, max_value=4, step=1, key='facade')
    left.slider("Bathroom", min_value=0, max_value=5, step=1, key='bathroomCount')
    right.slider("Toilet", min_value=0, max_value=5, step=1, key='toiletCount')

#-----------------------------------------

    id_data['hasLift'] = st.session_state.hasLift
    id_data['type'] = 1 if st.session_state.type == "House" else 2
    id_data['habitableSurface'] = st.session_state.surface
    id_data['bedroomCount'] = st.session_state.bedroomCount
    id_data['facedeCount'] = st.session_state.facade
    id_data['toiletCount'] = st.session_state.toiletCount
    id_data['postCode'] = st.session_state.zip_code
    id_data['bathroomCount'] = st.session_state.bathroomCount
    id_data['hasSwimmingPool'] = st.session_state.pool

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
            "Parking Indoor Count", min_value=0, key="parkingIndoorCount")
        
    if id_data.get('hasparkingCountOutdoor'):
        id_data['parkingCountOutdoor'] = st.number_input(
            "Parking Outdoor Count", min_value=0, key="parkingOutdoorCount")
        
    if id_data.get('hasTerrace'):
        id_data['terraceSurface'] = st.number_input(
            "Terrace Surface (m²)", min_value=0, key="terraceSurface")
            
        id_data['terraceOrientation'] = st.selectbox(
            'Terrace Orientation', labels['terraceOrientation'])
           
    if id_data.get('hasLivingRoom'):
        id_data['livingRoomSurface'] = st.number_input(
            "Living room Surface (m²)", min_value=0, key="livingRoomSurface")
            
    if id_data.get('hasDiningRoom'):
        id_data['diningRoomSurface'] = st.number_input(
            "Dining room Surface (m²)", min_value=0, key="diningRoomSurface")

#-----------------------------------------

    numeric_fields = [
        ("Kitchen Surface", 'kitchenSurface'),
        ("Building Year", 'buildingConstructionYear'),
        ("Street Facade Width", 'streetFacadeWidth'),
        ("Property Land Surface (m²)", 'landSurface'),
        ("Cadastre Income", 'cadastralIncome'),
        ("Energy Consumption per m²", 'primaryEnergyConsumptionPerSqm'),
        # room count, floor count
    ]
    for label, key in numeric_fields:
        id_data[key] = st.number_input(label, min_value=0, step=1)

#-----------------------------------------

    select_fields = {
        'Subtype': 'subtype',
        'Kitchen Type': 'kitchenType',
        'Flood Zone': 'floodZoneType',
        'Heating Type': 'heatingType',
        'EPC Score': 'epcScore',
        'Building Condition': 'buildingCondition'
    }
    for label, data_key in select_fields.items():
        choice = st.selectbox(label, labels[data_key])
        add_data(data_key, choice)

#-----------------------------------------
#--------------- SideBar -----------------
#--------------- FastAPI -----------------
#-----------------------------------------

with st.sidebar:

    if st.button("Prediction"):
        prediction_url = "https://eliza-back.onrender.com/predict"
        #prediction_url = "http://0.0.0.0:8555/predict"
        req = requests.post(prediction_url, json=id_data, timeout=5)

        if req.status_code == 200:
            price = req.json()["price"]
            st.write(f"price of the property: {price:,.0f} €")

        else:
            st.error(f"Erreur API {req.status_code}: {req.text}")

    #-----------------------------------------
    #--------------- History -----------------
    #-----------------------------------------

    st.write('---')
    st.title('History:')

    history_url = "https://eliza-back.onrender.com/history"
    #history_url = "http://0.0.0.0:8555/history"
    resp = requests.get(history_url, timeout=5)

    if resp.status_code == 200:
        data = resp.json()

        for row in reversed(data.get('rows', [])):

            locality_data = row[5] -1 
            locality_name = labels['locality'][locality_data]
            price = row[-1]

            st.write(f"{locality_name} -- {price:,.0f} €")

    else:
        st.error(f"Erreur historique {resp.status_code}: {resp.text}")
    
    #-----------------------------------------
    #------------- to do list-----------------
    #-----------------------------------------

    #### deploy render

    #### address => reverse geocode

    #### if locality => postcode
    #### if postcode => locality