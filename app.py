import streamlit as st
import requests
from datetime import datetime

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
    /* Основной фон */
    .stApp {
        background-color: #0f1117;
    }
    
    /* Заголовки */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
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
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #00e5ff;
        transform: translateY(-2px);
    }
    
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
    
    /* Боковая панель */
    [data-testid="stSidebar"] {
        background-color: #0f1117;
        border-right: 1px solid #2a2c33;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e1e4e8;
    }
    
    /* Кнопки */
    .stButton button {
        background-color: #00e5ff;
        color: #0f1117;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #00b8d4;
        transform: scale(1.02);
    }
    
    /* Разделитель */
    hr {
        border-color: #2a2c33;
        margin: 1.5rem 0;
    }
    
    /* Блок курсов валют */
    .currency-card {
        background-color: #1a1c23;
        border: 1px solid #2a2c33;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0.2rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .currency-symbol {
        font-weight: bold;
        color: #00e5ff;
    }
    
    .currency-value {
        font-family: 'Courier New', monospace;
        color: #e1e4e8;
    }
    
    /* Версия в футере */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #5a5d68;
        font-size: 0.7rem;
        border-top: 1px solid #2a2c33;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ ====================

def get_exchange_rates():
    """Получение курсов валют (тенге к USD, EUR, RUB, CNY)"""
    try:
        # Используем бесплатный API
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            usd_to_kzt = 459.47  # базовое значение USD/KZT
            rates = data.get("rates", {})
            
            # Рассчитываем курсы
            eur_to_kzt = round(usd_to_kzt / rates.get("EUR", 1.0) * rates.get("EUR", 1.0), 2)
            rub_to_kzt = round(usd_to_kzt / rates.get("RUB", 1.0) * rates.get("RUB", 1.0), 2)
            cny_to_kzt = round(usd_to_kzt / rates.get("CNY", 1.0) * rates.get("CNY", 1.0), 2)
            
            return {
                "USD": usd_to_kzt,
                "EUR": eur_to_kzt,
                "RUB": rub_to_kzt,
                "CNY": cny_to_kzt
            }
    except Exception as e:
        pass
    
    # Возвращаем тестовые данные, если API недоступен
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
                weather_data.append({
                    "city": city["name"],
                    "temp": data["current_weather"]["temperature"]
                })
        except Exception:
            weather_data.append({"city": city["name"], "temp": None})
    
    return weather_data

# ==================== БОКОВАЯ ПАНЕЛЬ ====================
with st.sidebar:
    st.markdown("## ⚡ SmartEnergyPro")
    st.markdown("---")
    
    # Тема оформления (декоративно)
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
    st.caption("v.3.4.2 (Stable Edition)")
    st.caption("© 2026 SmartEnergy Systems")

# ==================== ОСНОВНОЙ КОНТЕНТ ====================

# Заголовок
st.title("⚡ SmartEnergy Pro")
st.markdown(f"### Система мониторинга на {datetime.now().strftime('%d.%m.%Y')}")

# Описание
st.markdown("""
<div class="description-text">
    Добро пожаловать в панель управления SmartEnergy Pro. Система обеспечивает непрерывный контроль 
    потребления топливно-энергетических ресурсов (ТЭР) на промышленных объектах, анализ телеметрии 
    и оценку влияния метеорологических условий на энергоэффективность.
</div>
""", unsafe_allow_html=True)

# ==================== КАРТОЧКИ МЕТРИК ====================
# Данные для метрик
total_resources = 26
active_tags = 2
cities_count = 5

# Получаем погоду для метрики средней температуры
weather_data = get_weather()
if weather_data:
    valid_temps = [w["temp"] for w in weather_data if w["temp"] is not None]
    avg_temp = sum(valid_temps) / len(valid_temps) if valid_temps else 0
else:
    avg_temp = 0

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

# ==================== ТЕМПЕРАТУРА ПО ГОРОДАМ ====================
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
else:
    st.info("🌐 Данные о погоде временно недоступны. Проверьте подключение к интернету.")

# ==================== ФУТЕР ====================
st.markdown("""
<div class="footer">
    SmartEnergy Pro — промышленная платформа энергомониторинга
</div>
""", unsafe_allow_html=True)
