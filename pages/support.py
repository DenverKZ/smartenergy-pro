import streamlit as st
from datetime import datetime

def show():
    st.title("🆘 Поддержка")
    st.caption("Документация, контакты и обращения в техническую службу")
    
    # ========== СТАТУСНАЯ СТРОКА ==========
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Версия", "3.4.2 (Stable)")
    with col2:
        st.metric("Источник погоды", "Open-Meteo API")
    with col3:
        st.metric("SLA отклика", "до 24 часов")
    
    st.markdown("---")
    
    # ========== FAQ ==========
    st.subheader("❓ Часто задаваемые вопросы")
    
    faq_items = {
        "Как добавить новый ресурс в справочник ТЭР?": 
            "Перейдите в раздел «Настройки» → вкладка «Активные ресурсы». Нажмите «Добавить ресурс» в правом верхнем углу. Удалить можно только пользовательские ресурсы — системные защищены от случайного удаления.",
        
        "Как пересчитать т.н.э. и CO₂ из т.у.т.?": 
            "На вкладке «т.у.т.» нажмите «Пересчитать т.н.э./CO₂» — оба производных коэффициента восстановятся по формулам 0.7 × т.у.т. и 2.1 × т.у.т.",
        
        "Почему архив погоды не подгружается за последние 2 дня?": 
            "Open-Meteo формирует архивный массив с задержкой ~48 часов. Конечная дата автоматически смещается на максимально доступную, чтобы не получить пустой ответ.",
        
        "Где хранятся мои данные?": 
            "Все настройки, теги, журнал потребления и события календаря сохраняются локально в браузере (localStorage) или в памяти сессии Streamlit. Данные не покидают ваше устройство.",
        
        "Как экспортировать журнал потребления?": 
            "В разделе «Ввод данных» нажмите «Экспорт CSV» в заголовке журнала. Файл откроется в Excel или Google Sheets с поддержкой кириллицы.",
        
        "Можно ли импортировать данные из Excel?": 
            "Функция импорта планируется в следующей версии. Пока вы можете добавлять записи вручную через форму на странице «Ввод данных».",
        
        "Как изменить тему оформления?": 
            "В боковой панели есть кнопки выбора темы: 🌞 Светлая, 🌙 Тёмная, 💻 Системная. Тема сохраняется в настройках браузера.",
        
        "Поддерживаются ли другие валюты?": 
            "Курсы валют отображаются в тенге (₸) для USD, EUR, RUB, CNY. При необходимости можно добавить другие валюты."
    }
    
    for q, a in faq_items.items():
        with st.expander(q):
            st.markdown(a)
    
    st.markdown("---")
    
    # ========== КОНТАКТЫ ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📞 Контакты технической поддержки")
        st.markdown("""
        | Канал | Контакт |
        |-------|---------|
        | ✉️ Email | `support@smartenergy.kz` |
        | 📱 Телефон | `+7 (727) 250-00-00` |
        | 💬 Telegram | `@smartenergy_kz` |
        | 📠 Факс | `+7 (727) 250-00-01` |
        
        **Режим работы:**  
        Пн–Пт: 09:00 – 18:00 (Астана)
        """)
    
    with col2:
        st.subheader("🚨 Аварийная линия")
        st.markdown("""
        <div style="background-color: #ff9d00; padding: 1rem; border-radius: 8px; text-align: center;">
            <span style="font-size: 2rem;">🚨</span><br>
            <span style="font-weight: bold; color: #0f1117;">Круглосуточно</span><br>
            <span style="font-size: 1.5rem; font-weight: bold; color: #0f1117;">+7 (727) 911-00-00</span><br>
            <span style="color: #0f1117;">Для критических инцидентов</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== ФОРМА ОБРАЩЕНИЯ ==========
    st.subheader("✉️ Создать обращение в техподдержку")
    st.caption("Заполните форму — мы свяжемся с вами по указанному адресу")
    
    # Инициализация обращений
    if 'support_tickets' not in st.session_state:
        st.session_state.support_tickets = []
    
    with st.form("support_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Ваше имя", placeholder="Иванов Иван")
        with col2:
            email = st.text_input("Email для ответа", placeholder="ivan@company.kz")
        
        subject = st.text_input("Тема обращения", placeholder="Проблема с ...")
        
        priority = st.selectbox("Приоритет", ["Низкий", "Средний", "Высокий", "Критический"])
        
        message = st.text_area("Описание проблемы", placeholder="Подробно опишите ситуацию...", height=150)
        
        # Вложения (заглушка)
        st.caption("📎 При необходимости приложите скриншоты — их можно отправить ответным письмом")
        
        submitted = st.form_submit_button("📨 Отправить обращение", type="primary", use_container_width=True)
        
        if submitted:
            if subject and message and email:
                ticket = {
                    "id": str(int(datetime.now().timestamp())),
                    "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "name": name or "Аноним",
                    "email": email,
                    "subject": subject,
                    "priority": priority,
                    "message": message,
                    "status": "🟡 В обработке"
                }
                st.session_state.support_tickets.insert(0, ticket)
                st.success(f"✅ Обращение №{ticket['id']} зарегистрировано! Мы ответим в течение {24 if priority != 'Критический' else 4} часов.")
                st.balloons()
            elif not email:
                st.error("❌ Укажите email для обратной связи")
            else:
                st.error("❌ Заполните тему и описание проблемы")
    
    # ========== ИСТОРИЯ ОБРАЩЕНИЙ ==========
    if st.session_state.support_tickets:
        st.markdown("---")
        st.subheader("📋 Мои обращения")
        
        for ticket in st.session_state.support_tickets[:10]:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.markdown(f"**№{ticket['id']}**")
                    st.caption(ticket['date'])
                with col2:
                    st.markdown(f"**{ticket['subject']}**")
                with col3:
                    priority_colors = {
                        "Низкий": "🔵",
                        "Средний": "🟡",
                        "Высокий": "🟠",
                        "Критический": "🔴"
                    }
                    st.markdown(f"{priority_colors.get(ticket['priority'], '⚪')} {ticket['priority']}")
                    st.markdown(f"{ticket['status']}")
                with col4:
                    if st.button("📄", key=f"view_{ticket['id']}"):
                        with st.expander(f"Обращение №{ticket['id']}", expanded=True):
                            st.markdown(f"**Тема:** {ticket['subject']}")
                            st.markdown(f"**Описание:** {ticket['message']}")
                            st.markdown(f"**Email:** {ticket['email']}")
                            st.markdown(f"**Статус:** {ticket['status']}")
                st.markdown("---")
    
    # ========== ПОЛЕЗНЫЕ РЕСУРСЫ ==========
    with st.expander("📚 Полезные ресурсы"):
        st.markdown("""
        ### Документация
        - [Руководство пользователя](https://docs.smartenergy.kz)
        - [API документация](https://api.smartenergy.kz/docs)
        - [Видеоуроки](https://youtube.com/@smartenergy)
        
        ### Интеграции
        - 1С:Предприятие
        - SAP ERP
        - SCADA-системы
        
        ### Обновления
        Версия 3.4.2 — стабильный релиз
        - Исправлены ошибки отображения графиков
        - Добавлен экспорт в CSV
        - Улучшена производительность
        """)
    
    # ========== ФУТЕР ==========
    st.markdown("---")
    st.caption("© 2026 SmartEnergyPro. Все права защищены. Политика конфиденциальности")
