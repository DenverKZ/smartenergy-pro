import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import json
import os
from pathlib import Path

# Настройка страницы
st.set_page_config(
    page_title="SmartEnergy Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS для тёмной темы
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .metric-card {
        background-color: #1a1c23;
        border: 1px solid #2a2c33;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00e5ff;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #8a8d98;
        text-transform: uppercase;
    }
    h1, h2, h3 { color: #e1e4e8 !important; }
    div[data-testid="stMetric"] {
        background-color: #1a1c23;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #2a2c33;
    }
    div[data-testid="stMetric"] div { color: #00e5ff !important; }
</style>
""", unsafe_allow_html=True)

# Инициализация данных
def init_session_state():
    if 'resources' not in st.session_state:
        st.session_state.resources = [
            {"id": "1", "name": "Бензин автомобильный", "unit": "т", "coefTUT": 1.49, "coefCO2": 3.129, "tariff": 450000, "active": True},
            {"id": "2", "name": "Газ природный", "unit": "тыс. м³", "coefTUT": 1.154, "coefCO2": 2.423, "tariff": 150000, "active": True},
            {"id": "3", "name": "Дизельное топливо", "unit": "т", "coefTUT": 1.45, "coefCO2": 3.045, "tariff": 420000, "active": True},
            {"id": "4", "name": "Электроэнергия", "unit": "тыс. кВт·ч", "coefTUT": 0.123, "coefCO2": 0.258, "tariff": 25000, "active": True},
        ]
    if 'consumption_records' not in st.session_state:
        st.session_state.consumption_records = []
    if 'tags' not in st.session_state:
        st.session_state.tags = ["Main_Meter", "Boiler_01", "Boiler_02"]

init_session_state()

def get_weather():
    cities = [
        {"name": "Атырау", "lat": 47.1167, "lon": 51.8833},
        {"name": "Актау", "lat": 43.65, "lon": 51.1667},
        {"name": "Уральск", "lat": 51.2333, "lon": 51.3667},
    ]
    weather_data = []
    for city in cities:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current_weather=true"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                weather_data.append({"city": city["name"], "temp": data["current_weather"]["temperature"]})
        except:
            weather_data.append({"city": city["name"], "temp": None})
    return weather_data

# Боковое меню
with st.sidebar:
    st.markdown("## ⚡ SmartEnergy Pro")
    st.markdown("---")
    page = st.radio("Навигация", ["🏠 Главная", "✏️ Ввод данных", "🌤️ Погода", "⚙️ Настройки"])
    st.markdown("---")
    st.caption("v.3.4.2 | Streamlit")

# ГЛАВНАЯ СТРАНИЦА
if page == "🏠 Главная":
    st.title("⚡ SmartEnergy Pro")
    st.markdown(f"### Система мониторинга на {datetime.now().strftime('%d.%m.%Y')}")
    
    col1, col2, col3, col4 = st.columns(4)
    active = sum(1 for r in st.session_state.resources if r["active"])
    col1.metric("Ресурсов в базе", len(st.session_state.resources))
    col2.metric("Активных ТЭГов", len(st.session_state.tags))
    col3.metric("Городов мониторинга", 3)
    
    weather = get_weather()
    if weather:
        avg_temp = sum(w["temp"] for w in weather if w["temp"]) / len([w for w in weather if w["temp"]])
        col4.metric("Средняя температура", f"{avg_temp:.1f}°C")
    
    st.markdown("---")
    st.subheader("🌡️ Текущая температура")
    
    if weather:
        cols = st.columns(3)
        for i, w in enumerate(weather):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{w['city']}</div>
                    <div class="metric-value">{w['temp']:.1f}°C</div>
                </div>
                """, unsafe_allow_html=True)

# ВВОД ДАННЫХ
elif page == "✏️ Ввод данных":
    st.title("✏️ Ввод данных")
    
    with st.expander("➕ Новая запись", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            date = st.date_input("Дата", datetime.now())
        with col2:
            active_res = [r for r in st.session_state.resources if r["active"]]
            res_names = [f"{r['name']} ({r['unit']})" for r in active_res]
            res_idx = st.selectbox("Ресурс", range(len(res_names)), format_func=lambda x: res_names[x])
            selected = active_res[res_idx] if active_res else None
        with col3:
            qty = st.number_input("Количество", min_value=0.0, step=0.1)
        with col4:
            tag = st.selectbox("Тег", st.session_state.tags)
        
        if st.button("💾 Записать", type="primary"):
            if selected and qty > 0:
                st.session_state.consumption_records.append({
                    "id": str(datetime.now().timestamp()),
                    "date": date.strftime("%Y-%m-%d"),
                    "resource": selected["name"],
                    "unit": selected["unit"],
                    "quantity": qty,
                    "tag": tag,
                    "coefTUT": selected["coefTUT"],
                    "coefCO2": selected["coefCO2"],
                    "tariff": selected["tariff"]
                })
                st.success(f"✅ Добавлено: {selected['name']} - {qty} {selected['unit']}")
                st.rerun()
    
    if st.session_state.consumption_records:
        df = pd.DataFrame(st.session_state.consumption_records)
        df["tut"] = df["quantity"] * df["coefTUT"]
        df["co2"] = df["quantity"] * df["coefCO2"]
        df["cost"] = df["quantity"] * df["tariff"]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Σ т.у.т.", f"{df['tut'].sum():.3f}")
        col2.metric("Σ т CO₂", f"{df['co2'].sum():.3f}")
        col3.metric("Σ стоимость, ₸", f"{df['cost'].sum():,.2f}")
        
        st.dataframe(df[["date", "resource", "quantity", "unit", "tag", "tut", "co2"]], use_container_width=True)

# ПОГОДА
elif page == "🌤️ Погода":
    st.title("🌤️ Погода")
    
    weather = get_weather()
    if weather:
        cols = st.columns(3)
        for i, w in enumerate(weather):
            with cols[i]:
                st.metric(w["city"], f"{w['temp']:.1f}°C")

# НАСТРОЙКИ
elif page == "⚙️ Настройки":
    st.title("⚙️ Настройки")
    
    tab1, tab2 = st.tabs(["📋 Ресурсы", "🏷️ Теги"])
    
    with tab1:
        df_res = pd.DataFrame(st.session_state.resources)
        edited = st.data_editor(
            df_res[["name", "unit", "coefTUT", "tariff", "active"]],
            column_config={
                "name": "Ресурс",
                "unit": "Ед. изм.",
                "coefTUT": st.column_config.NumberColumn("т.у.т.", format="%.4f"),
                "tariff": st.column_config.NumberColumn("Тариф, ₸", format="%.2f"),
                "active": st.column_config.CheckboxColumn("Активен")
            },
            use_container_width=True
        )
        if st.button("💾 Сохранить"):
            for i, row in edited.iterrows():
                st.session_state.resources[i]["name"] = row["name"]
                st.session_state.resources[i]["unit"] = row["unit"]
                st.session_state.resources[i]["coefTUT"] = row["coefTUT"]
                st.session_state.resources[i]["tariff"] = row["tariff"]
                st.session_state.resources[i]["active"] = row["active"]
            st.success("Сохранено!")
            st.rerun()
    
    with tab2:
        new_tag = st.text_input("Новый тег")
        if st.button("➕ Добавить тег"):
            if new_tag and new_tag not in st.session_state.tags:
                st.session_state.tags.append(new_tag)
                st.rerun()
        
        for tag in st.session_state.tags:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"`{tag}`")
            with col2:
                if st.button("🗑️", key=tag):
                    st.session_state.tags.remove(tag)
                    st.rerun()
