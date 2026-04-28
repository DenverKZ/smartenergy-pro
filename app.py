import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import os
from pathlib import Path

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================
st.set_page_config(
    page_title="SmartEnergy Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ДЛЯ ТОЧНОГО СТИЛЯ ====================
st.markdown("""
<style>
    /* Основной фон */
    .stApp {
        background-color: #0f1117;
    }
    
    /* Заголовки */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #e1e4e8 !important;
    }
    
    /* Текст описания */
    .description-text {
        border-left: 3px solid #00e5ff;
        padding-left: 1rem;
        margin: 1rem 0;
        color: #8a8d98;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Карточки метрик */
    .metric-card {
        background-color: #1a1c23;
        border: 1px solid #2a2c33;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #00e5ff;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00e5ff;
        font-family: 'Courier New', monospace;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: #8a8d98;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }
    
    /* Боковая панель */
    [data-testid="stSidebar"] {
        background-color: #0f1117;
        border-right: 1px solid #2a2c33;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e1e4e8;
    }
    
    /* Кнопки в сайдбаре (radio) */
    div[data-testid="stSidebar"] div[role="radiogroup"] {
        margin-top: 1rem;
    }
    
    div[data-testid="stSidebar"] label {
        background-color: transparent;
        color: #8a8d98;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 500;
        margin: 0.1rem 0;
    }
    
    div[data-testid="stSidebar"] label:hover {
        background-color: #1a1c23;
        color: #00e5ff;
    }
    
    div[data-testid="stSidebar"] label[data-baseweb="radio"] [data-testid="stMarkdown"] {
        color: inherit;
    }
    
    /* Вкладки */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: #1a1c23;
        border-radius: 8px;
        padding: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: #8a8d98;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00e5ff;
        color: #0f1117;
    }
    
    /* Таблицы */
    .stDataFrame {
        background-color: #1a1c23;
        border-radius: 8px;
        border: 1px solid #2a2c33;
    }
    
    .stDataFrame th {
        background-color: #0f1117;
        color: #e1e4e8;
    }
    
    /* Кнопки */
    .stButton button {
        background-color: #00e5ff;
        color: #0f1117;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        background-color: #00b8d4;
        transform: translateY(-1px);
    }
    
    /* Разделитель */
    hr {
        border-color: #2a2c33;
        margin: 1rem 0;
    }
    
    /* Футер */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #5a5d68;
        font-size: 0.7rem;
        border-top: 1px solid #2a2c33;
        margin-top: 2rem;
    }
    
    /* Блок курсов валют */
    .currency-label {
        font-size: 0.75rem;
        color: #8a8d98;
    }
    
    .currency-value {
        font-size: 0.9rem;
        font-weight: 600;
        color: #e1e4e8;
        font-family: monospace;
    }
    
    /* Badge */
    .badge {
        background-color: #1a1c23;
        border: 1px solid #2a2c33;
        border-radius: 12px;
        padding: 0.2rem 0.6rem;
        font-size: 0.7rem;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# ==================== ИНИЦИАЛИЗАЦИЯ ДАННЫХ ====================
def init_session_state():
    # Справочник ресурсов (как в оригинале)
    if 'resources' not in st.session_state:
        st.session_state.resources = [
            {"id": "1", "name": "Бензин автомобильный", "unit": "т", "coefTUT": 1.49, "coefCO2": 3.129, "tariff": 450000, "active": True},
            {"id": "2", "name": "Газ природный", "unit": "тыс. м³", "coefTUT": 1.154, "coefCO2": 2.423, "tariff": 150000, "active": True},
            {"id": "3", "name": "Дизельное топливо", "unit": "т", "coefTUT": 1.45, "coefCO2": 3.045, "tariff": 420000, "active": True},
            {"id": "4", "name": "Электроэнергия", "unit": "тыс. кВт·ч", "coefTUT": 0.123, "coefCO2": 0.258, "tariff": 25000, "active": True},
            {"id": "5", "name": "Уголь Экибастузский", "unit": "т", "coefTUT": 0.628, "coefCO2": 1.319, "tariff": 25000, "active": True},
            {"id": "6", "name": "Тепловая энергия", "unit": "Гкал", "coefTUT": 0.1429, "coefCO2": 0.300, "tariff": 8500, "active": True},
        ]
    
    # Записи потребления
    if 'consumption_records' not in st.session_state:
        st.session_state.consumption_records = []
    
    # Теги
    if 'tags' not in st.session_state:
        st.session_state.tags = ["Main_Meter", "Boiler_01"]
    
    # События календаря
    if 'calendar_events' not in st.session_state:
        st.session_state.calendar_events = []
    
    # Журнал погоды
    if 'weather_log' not in st.session_state:
        st.session_state.weather_log = []

init_session_state()

# ==================== ФУНКЦИИ ДЛЯ API ====================
def get_exchange_rates():
    """Получение курсов валют"""
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
    except:
        pass
    return {"USD": 459.47, "EUR": 538.89, "RUB": 6.13, "CNY": 67.23}

def get_weather():
    """Получение текущей погоды для 5 городов Казахстана"""
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

# ==================== БОКОВАЯ ПАНЕЛЬ ====================
with st.sidebar:
    st.markdown("## ⚡ SmartEnergyPro")
    st.markdown("---")
    
    # Тема оформления
    st.markdown("**Тема оформления**  \n🌙 Dark / Industrial")
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
    
    # Навигация
    page = st.radio(
        "📋 Меню",
        ["🏠 Главная", "✏️ Ввод данных", "🌤️ Погода", "⚙️ Настройки", "📅 Календарь", "🆘 Поддержка"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("v.3.4.2 (Stable Edition)")
    st.caption("© 2026 SmartEnergy Systems")

# ==================== СТРАНИЦА: ГЛАВНАЯ ====================
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
    
    # Метрики
    total_resources = len(st.session_state.resources)
    active_resources = sum(1 for r in st.session_state.resources if r["active"])
    active_tags = len(st.session_state.tags)
    cities_count = 5
    
    # Средняя температура
    weather_data = get_weather()
    valid_temps = [w["temp"] for w in weather_data if w["temp"] is not None]
    avg_temp = sum(valid_temps) / len(valid_temps) if valid_temps else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_resources} / {total_resources}</div>
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

# ==================== СТРАНИЦА: ВВОД ДАННЫХ ====================
def page_data_input():
    st.title("✏️ Ввод данных")
    st.caption("Регистрация фактического потребления по тегам")
    
    # Форма добавления
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
            qty = st.number_input("Количество", min_value=0.0, step=0.1, format="%.3f")
        with col4:
            tag = st.selectbox("Тег", st.session_state.tags)
        
        if st.button("💾 Записать", type="primary", use_container_width=True):
            if selected and qty > 0:
                new_record = {
                    "id": str(datetime.now().timestamp()),
                    "date": date.strftime("%Y-%m-%d"),
                    "resource": selected["name"],
                    "unit": selected["unit"],
                    "quantity": qty,
                    "tag": tag,
                    "coefTUT": selected["coefTUT"],
                    "coefCO2": selected["coefCO2"],
                    "tariff": selected["tariff"]
                }
                st.session_state.consumption_records.insert(0, new_record)
                st.success(f"✅ Добавлено: {selected['name']} - {qty} {selected['unit']}")
                st.rerun()
    
    # Статистика
    if st.session_state.consumption_records:
        df = pd.DataFrame(st.session_state.consumption_records)
        df["tut"] = df["quantity"] * df["coefTUT"]
        df["co2"] = df["quantity"] * df["coefCO2"]
        df["cost"] = df["quantity"] * df["tariff"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Σ т.у.т.", f"{df['tut'].sum():.3f}")
        with col2:
            st.metric("Σ т CO₂", f"{df['co2'].sum():.3f}")
        with col3:
            st.metric("Σ стоимость, ₸", f"{df['cost'].sum():,.2f}")
        
        st.subheader("📋 Журнал записей")
        st.dataframe(df[["date", "resource", "quantity", "unit", "tag", "tut", "co2"]], use_container_width=True)
        
        # Экспорт
        csv = df[["date", "resource", "quantity", "unit", "tag", "tut", "co2", "cost"]].to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Экспорт в CSV", csv, f"consumption_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    else:
        st.info("Записей пока нет. Заполните форму выше, чтобы добавить первую.")

# ==================== СТРАНИЦА: ПОГОДА ====================
def page_weather():
    st.title("🌤️ Метеорологический архив")
    st.caption("Текущие условия и исторические данные")
    
    # Текущая погода
    weather_data = get_weather()
    if weather_data:
        cols = st.columns(5)
        for idx, w in enumerate(weather_data):
            with cols[idx]:
                temp_display = f"{w['temp']:.1f}°C" if w['temp'] is not None else "—"
                st.metric(w["city"], temp_display)
    
    st.markdown("---")
    
    # Ручной журнал замеров
    st.subheader("📝 Ручной журнал замеров")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        manual_temp = st.number_input("Температура, °C", value=15.0, step=0.5, format="%.1f")
    with col2:
        manual_hum = st.number_input("Влажность, %", min_value=0, max_value=100, value=50)
    with col3:
        if st.button("💾 Записать замер", type="primary", use_container_width=True):
            new_log = {
                "id": str(datetime.now().timestamp()),
                "timestamp": datetime.now().isoformat(),
                "temperature": manual_temp,
                "humidity": manual_hum
            }
            st.session_state.weather_log.append(new_log)
            st.success("Запись добавлена")
            st.rerun()
    
    # График замеров
    if st.session_state.weather_log:
        df_log = pd.DataFrame(st.session_state.weather_log)
        df_log['timestamp'] = pd.to_datetime(df_log['timestamp'])
        df_log = df_log.sort_values('timestamp')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_log['timestamp'],
            y=df_log['temperature'],
            name='Температура, °C',
            line=dict(color='#00e5ff', width=2),
            mode='lines+markers'
        ))
        fig.add_trace(go.Scatter(
            x=df_log['timestamp'],
            y=df_log['humidity'],
            name='Влажность, %',
            line=dict(color='#ff9d00', width=2),
            mode='lines+markers',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Динамика замеров",
            xaxis_title="Дата/Время",
            yaxis_title="Температура, °C",
            yaxis2=dict(title="Влажность, %", overlaying='y', side='right'),
            template='plotly_dark',
            height=400,
            plot_bgcolor='#1a1c23',
            paper_bgcolor='#1a1c23'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ==================== СТРАНИЦА: НАСТРОЙКИ ====================
def page_settings():
    st.title("⚙️ Конфигурация системы")
    st.caption("Справочник ТЭР, тарифы и метеотеги")
    
    # Активные ресурсы
    active_count = sum(1 for r in st.session_state.resources if r["active"])
    st.markdown(f"<span class='badge'>Активно: {active_count} / {len(st.session_state.resources)}</span>", unsafe_allow_html=True)
    
    tabs = st.tabs(["📋 Активные ресурсы", "💰 Тарифы", "🏷️ Теги"])
    
    with tabs[0]:
        st.subheader("Каталог энергоресурсов")
        st.caption("Отметьте ресурсы, которые отслеживает ваше предприятие. Активные попадают в редакторы коэффициентов и тарифов.")
        
        # Редактируемая таблица
        df_res = pd.DataFrame(st.session_state.resources)
        edited = st.data_editor(
            df_res[["name", "unit", "coefTUT", "tariff", "active"]],
            column_config={
                "name": "Вид энергоресурса",
                "unit": "Ед. изм.",
                "coefTUT": st.column_config.NumberColumn("Коэф. (т.у.т.)", format="%.4f"),
                "tariff": st.column_config.NumberColumn("Тариф (без НДС), ₸", format="%.2f"),
                "active": st.column_config.CheckboxColumn("Учёт")
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
    
    with tabs[1]:
        st.subheader("Тарифы на энергоресурсы")
        
        tariff_df = pd.DataFrame([{
            "Ресурс": r['name'],
            "Ед. изм.": r['unit'],
            "Тариф, ₸": r['tariff']
        } for r in st.session_state.resources if r['active']])
        
        edited_tariffs = st.data_editor(
            tariff_df,
            column_config={
                "Тариф, ₸": st.column_config.NumberColumn("Тариф, ₸", format="%.2f")
            },
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("💾 Сохранить тарифы", type="primary"):
            for idx, row in edited_tariffs.iterrows():
                for r in st.session_state.resources:
                    if r['name'] == row['Ресурс'] and r['active']:
                        r['tariff'] = row['Тариф, ₸']
            st.success("Тарифы сохранены")
    
    with tabs[2]:
        st.subheader("Теги объектов")
        st.caption("Идентификаторы точек учёта (счётчики, котлы, узлы)")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            new_tag = st.text_input("Новый тег", placeholder="Например: Boiler_04")
        with col2:
            if st.button("➕ Добавить", use_container_width=True):
                if new_tag and new_tag not in st.session_state.tags:
                    st.session_state.tags.append(new_tag)
                    st.success(f"Тег '{new_tag}' добавлен")
                    st.rerun()
        
        st.markdown("### Существующие теги")
        cols = st.columns(4)
        for idx, tag in enumerate(st.session_state.tags):
            with cols[idx % 4]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"`{tag}`")
                with col_b:
                    if st.button("🗑️", key=f"del_{tag}"):
                        st.session_state.tags.remove(tag)
                        st.rerun()

# ==================== СТРАНИЦА: КАЛЕНДАРЬ ====================
def page_calendar():
    st.title("📅 Календарь")
    st.caption("Поверки приборов учёта, ТО, отчётность")
    
    # Добавление события
    with st.expander("➕ Новое событие", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            event_date = st.date_input("Дата", datetime.now())
        with col2:
            event_type = st.selectbox("Тип", ["Поверка", "ТО", "Отчёт", "Прочее"])
        
        event_title = st.text_input("Название", placeholder="Поверка счётчика Boiler_01")
        event_notes = st.text_area("Примечание", placeholder="Дополнительная информация")
        
        if st.button("💾 Сохранить событие", type="primary"):
            if event_title:
                new_event = {
                    "id": str(datetime.now().timestamp()),
                    "date": event_date.strftime("%Y-%m-%d"),
                    "title": event_title,
                    "notes": event_notes,
                    "type": event_type
                }
                st.session_state.calendar_events.append(new_event)
                st.success("Событие добавлено")
                st.rerun()
    
    # Отображение событий
    if st.session_state.calendar_events:
        events_df = pd.DataFrame(st.session_state.calendar_events)
        events_df['date'] = pd.to_datetime(events_df['date'])
        
        # Сегодняшние события
        today = datetime.now().date()
        today_events = events_df[events_df['date'].dt.date == today]
        
        if not today_events.empty:
            st.subheader(f"📌 События на сегодня ({today.strftime('%d.%m.%Y')})")
            for _, event in today_events.iterrows():
                st.info(f"**{event['type']}**: {event['title']}")
        
        # Ближайшие события
        st.subheader("📋 Ближайшие события")
        future_events = events_df[events_df['date'].dt.date >= today].sort_values('date')
        
        for _, event in future_events.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 6, 1])
                with col1:
                    st.markdown(f"**{event['date'].strftime('%d.%m.%Y')}**")
                with col2:
                    st.markdown(f"**{event['type']}**: {event['title']}")
                    if event['notes']:
                        st.caption(event['notes'])
                with col3:
                    if st.button("🗑️", key=f"del_cal_{event['id']}"):
                        st.session_state.calendar_events = [e for e in st.session_state.calendar_events if e['id'] != event['id']]
                        st.rerun()
                st.markdown("---")
    else:
        st.info("Нет запланированных событий. Добавьте первое событие.")

# ==================== СТРАНИЦА: ПОДДЕРЖКА ====================
def page_support():
    st.title("🆘 Поддержка")
    st.caption("Документация, контакты и обращения в техническую службу")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Версия", "3.4.2 (Stable)")
    with col2:
        st.metric("Источник погоды", "Open-Meteo API")
    with col3:
        st.metric("SLA отклика", "до 24 часов")
    
    st.markdown("---")
    
    # FAQ
    st.subheader("❓ Часто задаваемые вопросы")
    faq = {
        "Как добавить новый ресурс в справочник ТЭР?": 
            "Перейдите в раздел «Настройки» → «Активные ресурсы» и измените данные в таблице. Удалить можно только пользовательские ресурсы.",
        "Как пересчитать т.н.э. и CO₂ из т.у.т.?": 
            "Коэффициенты рассчитываются автоматически: т.н.э. = т.у.т. × 0.7, CO₂ = т.у.т. × 2.1",
        "Почему архив погоды не подгружается за последние 2 дня?": 
            "Open-Meteo формирует архивный массив с задержкой ~48 часов.",
        "Где хранятся мои данные?": 
            "Все данные сохраняются локально в браузере (localStorage) или в памяти сессии Streamlit.",
        "Как экспортировать журнал потребления?": 
            "В разделе «Ввод данных» нажмите кнопку «Экспорт в CSV»."
    }
    
    for q, a in faq.items():
        with st.expander(q):
            st.write(a)
    
    st.markdown("---")
    
    # Контакты
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📞 Контакты")
        st.markdown("""
        - ✉️ **Email**: support@smartenergy.kz
        - 📱 **Телефон**: +7 (727) 250-00-00
        - 💬 **Telegram**: @smartenergy_kz
        """)
    with col2:
        st.subheader("🚨 Аварийная линия")
        st.markdown("""
        Для критических инцидентов — звоните **+7 (727) 911-00-00** круглосуточно.
        """)
    
    # Форма обращения
    st.markdown("---")
    st.subheader("✉️ Создать обращение")
    with st.form("support_form"):
        subject = st.text_input("Тема")
        email = st.text_input("Email для ответа")
        message = st.text_area("Описание проблемы", height=100)
        if st.form_submit_button("📨 Отправить", type="primary"):
            if subject and message:
                st.success("✅ Обращение зарегистрировано! Мы свяжемся с вами.")
                st.balloons()
            else:
                st.error("❌ Заполните тему и описание проблемы")

# ==================== НАВИГАЦИЯ ====================
if page == "🏠 Главная":
    page_home()
elif page == "✏️ Ввод данных":
    page_data_input()
elif page == "🌤️ Погода":
    page_weather()
elif page == "⚙️ Настройки":
    page_settings()
elif page == "📅 Календарь":
    page_calendar()
elif page == "🆘 Поддержка":
    page_support()

# ==================== ФУТЕР ====================
st.markdown("""
<div class="footer">
    SmartEnergy Pro — промышленная платформа энергомониторинга
</div>
""", unsafe_allow_html=True)
