import streamlit as st

def init_data():
    if 'resources' not in st.session_state:
        st.session_state.resources = [
            {"id": "1", "name": "Бензин автомобильный", "unit": "т", "coefTUT": 1.49, "coefCO2": 3.129, "tariff": 450000, "active": True},
            {"id": "2", "name": "Газ природный", "unit": "тыс. м³", "coefTUT": 1.154, "coefCO2": 2.423, "tariff": 150000, "active": True},
            {"id": "3", "name": "Дизельное топливо", "unit": "т", "coefTUT": 1.45, "coefCO2": 3.045, "tariff": 420000, "active": True},
            {"id": "4", "name": "Электроэнергия", "unit": "тыс. кВт·ч", "coefTUT": 0.123, "coefCO2": 0.258, "tariff": 25000, "active": True},
            {"id": "5", "name": "Уголь Экибастузский", "unit": "т", "coefTUT": 0.628, "coefCO2": 1.319, "tariff": 25000, "active": True},
            {"id": "6", "name": "Тепловая энергия", "unit": "Гкал", "coefTUT": 0.1429, "coefCO2": 0.300, "tariff": 8500, "active": True},
        ]
    if 'tags' not in st.session_state:
        st.session_state.tags = ["Main_Meter", "Boiler_01"]
    if 'consumption_records' not in st.session_state:
        st.session_state.consumption_records = []
