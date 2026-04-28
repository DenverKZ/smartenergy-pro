import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import json
import os

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================
st.set_page_config(
    page_title="SmartEnergy Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ДЛЯ ТЁМНОЙ ТЕМЫ ====================
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2 { color: #e1e4e8 !important; }
    .description-text {
        border-left: 3px solid #00e5ff;
        padding-left: 1rem;
        margin: 1rem 0;
        color: #8a8d98;
        font-size: 0.9rem;
    }
    .metric-card {
        background-color: #1a1c23;
        border: 1px solid #2a2c33;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover { border-color: #00e5ff; transform: translateY(-2px); }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #00e5ff;
        font-family: 'Courier New', monospace;
    }
    .metric-label {
        font-size: 0.7rem;
        color: #8a8d98;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }
    [data-testid="stSidebar"] {
        background-color: #0f1117;
        border-right: 1px solid #2a2c33;
    }
    hr { border-color: #2a2c33; margin: 1.5rem 0; }
    .footer {
        text-align: center;
        padding: 1rem;
        color: #5a5d68;
        font-size: 0.7rem;
        border-top: 1px solid #2a2c33;
        margin-top: 2rem;
    }
    /* Стиль для кнопок в sidebar */
    div[data-testid="stSidebar"] button {
        background-color: transparent;
        color: #8a8d98;
        text-align: left;
        border: none;
        padding: 0.5rem 1rem;
        margin: 0.2rem 0;
        border-radius: 8px;
        font-weight: normal;
    }
    div[data-testid="stSidebar"] button:hover {
        background-color: #1a1c23;
        color: #00e5ff;
    }
    /* Таблицы */
    .stDataFrame {
        background-color: #1a1c23;
        border-radius: 8px;
    }
    /* Вкладки */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1a1c23;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00e5ff;
        color: #0f1117;
    }
</style>
""", unsafe_allow_html=True)

# ==================== ИНИЦИАЛИЗАЦИЯ ДАННЫХ ====================
def init_session_state():
    if 'resources' not in st.session_state:
        st.session_state.resources = [
            {"id": "1", "name": "Бензин автомобильный", "unit": "т", "coefTUT": 1.49, "coefCO2": 3.129, "tariff": 450000, "active": True},
            {"id": "2", "name": "Газ природный", "unit": "тыс. м³", "coefTUT": 1.154, "coefCO2": 2.423, "tariff": 150000, "active": True},
            {"id": "3", "name": "Дизельное топливо", "unit": "т", "coefTUT": 1.45, "coefCO2": 3.045, "tariff": 420000, "active": True},
            {"id": "4", "name": "Электроэнергия", "unit": "тыс. кВт·ч", "coefTUT": 0.123, "coefCO2": 0.258, "tariff": 25000, "active": True},
            {"id": "5", "name": "Уголь Экибастузский", "unit": "т", "coefTUT": 0.628, "coefCO2": 1.319, "tariff": 25000, "active": True},
            {"id": "6", "name": "Тепловая энергия", "unit": "Гкал", "coefTUT": 0.1429, "coefCO2": 0.300, "tariff": 8500, "active": True},
        ]
    if 'consumption_records' not in st.session_state:
        st.session_state.consumption_records = []
    if 'tags' not in st.session_state:
        st.session_state.tags = ["Main_Meter", "Boiler_01", "Boiler_02"]

init_session_state()

# ==================== ФУНКЦИИ ====================
def get_exchange_rates():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            usd_to_kzt = 459.47
            rates = data.get("rates", {})
            eur_to_kzt = round(usd_to_kzt / rates.get("EUR", 1.0) * rates.get("EUR", 1.0), 2)
            rub_to_kzt = round(usd_to_kzt / rates.get("RUB", 1.0) * rates.get("RUB", 1.0), 2)
            cny_to_kzt = round(usd_to_kzt / rates.get("CNY", 1.0) * rates.get("CNY", 1.0), 2)
            return {"USD": usd_to_kzt, "EUR": eur_to_kzt, "RUB": rub_to_kzt, "CNY": cny_to_kzt}
    except: pass
    return {"USD": 459.47, "EUR": 538.89, "RUB": 6.13, "CNY": 67.23}

def get_weather():
    cities = [
        {"name": "Атырау", "lat": 47.1167, "lon": 51.8833},
        {"name": "Актау", "lat": 43.65, "lon": 51.1667},
        {"name": "Кульсары", "lat": 46.95, "lon": 53.9833},
        {"name": "Уральск", "lat": 51.2333, "lon": 51.3667},
        {"name": "Актобе", "lat": 50.2833, "lon": 57.1667},
    ]
    weather_data = []
    for city in cities:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current_weather=true"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                weather_data.append({"city": city["name"], "temp": data["current_weather"]["temperature"]})
        except:
            weather_data.append({"city": city["name"], "temp": None})
    return weather_data

# ==================== БОКОВАЯ ПАНЕЛЬ С КНОПКАМИ НАВИГАЦИИ ====================
with st.sidebar:
    st.markdown("## ⚡ SmartEnergyPro")
    st.markdown("---")
    
    # ===== КНОПКИ НАВИГАЦИИ =====
    st.markdown("### 📋 Меню")
    
    # Используем radio для навигации (это и есть кнопки)
    page = st.radio(
        "",
        ["🏠 Главная", "✏️ Ввод данных", "🌤️ Погода", "⚙️ Настройки"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Курсы валют
    st.markdown("**Курсы валют → ₸**")
    rates = get_exchange_rates()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**$1 USD**  \n{rates['USD']} ₸")
        st.markdown(f"**€1 EUR**  \n{rates['EUR']} ₸")
    with col2:
        st.markdown(f"**₽1 RUB**  \n{rates['RUB']} ₸")
        st.markdown(f"**¥1 CNY**  \n{rates['CNY']} ₸")
    
    st.markdown("---")
    st.caption("v.3.4.2 (Stable Edition)")
    st.caption("© 2026 SmartEnergy Systems")

# ==================== СТРАНИЦА 1: ГЛАВНАЯ ====================
def page_home():
    st.title("⚡ SmartEnergy Pro")
    st.markdown(f"### Система мониторинга на {datetime.now().strftime('%d.%m.%Y')}")
    
    st.markdown("""
    <div class="description-text">
        Добро пожаловать в панель управления SmartEnergy Pro. Система обеспечивает непрерывный контроль 
        потребления топливно-энергетических ресурсов (ТЭР) на промышленных объектах, анализ телеметрии 
        и оценку влияния метеорологических условий на энергоэффективность.
    </div>
    """, unsafe_allow_html=True)
    
    # Карточки метрик
    total_resources = len(st.session_state.resources)
    active_tags = len(st.session_state.tags)
    cities_count = 5
    
    weather_data = get_weather()
    valid_temps = [w["temp"] for w in weather_data if w["temp"] is not None]
    avg_temp = sum(valid_temps) / len(valid_temps) if valid_temps else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_resources}</div>
            <div class="metric-label">Ресурсов в базе</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_tags}</div>
            <div class="metric-label">Активных ТЭГов</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{cities_count}</div>
            <div class="metric-label">Городов мониторинга</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_temp:.1f}°C</div>
            <div class="metric-label">Средняя температура</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🌡️ Текущая температура по объектам")
    
    if weather_data:
        cols = st.columns(5)
        for idx, w in enumerate(weather_data):
            with cols[idx]:
                temp_display = f"{w['temp']:.1f}°C" if w['temp'] is not None else "—"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{temp_display}</div>
                    <div class="metric-label">{w['city']}</div>
                </div>
                """, unsafe_allow_html=True)

# ==================== СТРАНИЦА 2: ВВОД ДАННЫХ ====================
def page_data_input():
    st.title("✏️ Ввод данных")
    st.caption("Регистрация фактического потребления по тегам")
    
    # Форма для новой записи
    with st.expander("➕ Новая запись потребления", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            date = st.date_input("Дата", datetime.now())
        with col2:
            active_res = [r for r in st.session_state.resources if r["active"]]
            res_names = [f"{r['name']} ({r['unit']})" for r in active_res]
            if res_names:
                res_idx = st.selectbox("Ресурс", range(len(res_names)), format_func=lambda x: res_names[x])
                selected = active_res[res_idx]
            else:
                selected = None
                st.warning("Нет активных ресурсов. Добавьте в настройках.")
        with col3:
            qty = st.number_input("Количество", min_value=0.0, step=0.1, format="%.2f")
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
    
    # Статистика и таблица
    if st.session_state.consumption_records:
        df = pd.DataFrame(st.session_state.consumption_records)
        df["tut"] = df["quantity"] * df["coefTUT"]
        df["co2"] = df["quantity"] * df["coefCO2"]
        df["cost"] = df["quantity"] * df["tariff"]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Σ т.у.т.", f"{df['tut'].sum():.3f}")
        col2.metric("Σ т CO₂", f"{df['co2'].sum():.3f}")
        col3.metric("Σ стоимость, ₸", f"{df['cost'].sum():,.2f}")
        
        st.subheader("📋 Журнал записей")
        st.dataframe(df[["date", "resource", "quantity", "unit", "tag", "tut", "co2"]], use_container_width=True)
        
        # Экспорт CSV
        csv = df[["date", "resource", "quantity", "unit", "tag", "tut", "co2", "cost"]].to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Экспорт в CSV", csv, f"consumption_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    else:
        st.info("Записей пока нет. Заполните форму выше, чтобы добавить первую.")

# ==================== СТРАНИЦА 3: ПОГОДА ====================
def page_weather():
    st.title("🌤️ Погода")
    st.caption("Текущие условия и исторические данные")
    
    weather_data = get_weather()
    if weather_data:
        cols = st.columns(5)
        for idx, w in enumerate(weather_data):
            with cols[idx]:
                temp_display = f"{w['temp']:.1f}°C" if w['temp'] is not None else "—"
                st.metric(w["city"], temp_display)
    else:
        st.error("Не удалось загрузить данные о погоде")

# ==================== СТРАНИЦА 4: НАСТРОЙКИ ====================
def page_settings():
    st.title("⚙️ Настройки")
    
    tab1, tab2 = st.tabs(["📋 Ресурсы ТЭР", "🏷️ Теги"])
    
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
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("💾 Сохранить ресурсы", type="primary"):
            for i, row in edited.iterrows():
                if i < len(st.session_state.resources):
                    st.session_state.resources[i]["name"] = row["name"]
                    st.session_state.resources[i]["unit"] = row["unit"]
                    st.session_state.resources[i]["coefTUT"] = row["coefTUT"]
                    st.session_state.resources[i]["tariff"] = row["tariff"]
                    st.session_state.resources[i]["active"] = row["active"]
                    st.session_state.resources[i]["coefCO2"] = row["coefTUT"] * 2.1
            st.success("Сохранено!")
            st.rerun()
    
    with tab2:
        new_tag = st.text_input("Новый тег", placeholder="Например: Boiler_03")
        if st.button("➕ Добавить тег"):
            if new_tag and new_tag not in st.session_state.tags:
                st.session_state.tags.append(new_tag)
                st.rerun()
            elif new_tag in st.session_state.tags:
                st.warning("Тег уже существует")
        
        st.markdown("### Существующие теги")
        for tag in st.session_state.tags:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"`{tag}`")
            with col2:
                if st.button("🗑️", key=tag):
                    st.session_state.tags.remove(tag)
                    st.rerun()

# ==================== НАВИГАЦИЯ ПО СТРАНИЦАМ ====================
if page == "🏠 Главная":
    page_home()
elif page == "✏️ Ввод данных":
    page_data_input()
elif page == "🌤️ Погода":
    page_weather()
elif page == "⚙️ Настройки":
    page_settings()

# ==================== ФУТЕР ====================
st.markdown("""
<div class="footer">
    SmartEnergy Pro — промышленная платформа энергомониторинга
</div>
""", unsafe_allow_html=True)
